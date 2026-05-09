"""
네이버 블로그 마이그레이션 도구 (프리미엄 레이아웃 버전)
- 지도 카드(Map Card) 생성
- 동영상 카드(Video Card) 생성
- 링크 카드(OG Preview) 자동 생성
- 연속 이미지 그리드(Flex/Grid) 배치
"""
import os
import re
import time
import json
import requests
from bs4 import BeautifulSoup
import markdownify

BLOG_ID   = "sanjangboarder"
BASE_DIR  = os.path.join(os.path.dirname(__file__), "..", "src", "content", "posts")
HEADERS   = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://m.blog.naver.com/",
}

def get_post_content(blog_id, log_no):
    url = f"https://m.blog.naver.com/{blog_id}/{log_no}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        content_div = (soup.select_one('div.se-main-container') or soup.select_one('div#postViewArea'))
        if not content_div: return None

        # 1. 지도 처리 (네이버 맵 카드 생성)
        for map_div in content_div.select('.se-module-placesMap, .se-placesMap'):
            name = map_div.select_one('strong')
            address = map_div.select_one('p')
            if name:
                name_txt = name.get_text(strip=True)
                addr_txt = address.get_text(strip=True) if address else ""
                map_link = f"https://map.naver.com/p/search/{name_txt.replace(' ', '+')}"
                map_html = f'\n\n<div class="map-card glass"><div class="map-info"><span class="map-icon">📍</span><div class="map-text"><div class="map-name">{name_txt}</div><div class="map-addr">{addr_txt}</div></div></div><a href="{map_link}" target="_blank" class="map-btn">지도 보기</a></div>\n\n'
                map_div.replace_with(soup.new_string(map_html))

        # 2. 동영상 처리 (네이버 비디오/유튜브)
        for video_div in content_div.select('.se-module-video, .se-video'):
            video_data = video_div.select_one('script.__se_video_data')
            if video_data:
                try:
                    data = json.loads(video_data.string)
                    title = data.get('title', '동영상')
                    thumb = data.get('thumbnail', '')
                    video_link = f"https://blog.naver.com/{blog_id}/{log_no}"
                    video_html = f'\n\n<div class="video-card glass"><div class="video-thumb"><img src="{thumb}" /><div class="play-btn">▶</div></div><div class="video-info"><div class="video-title">{title}</div><a href="{video_link}" target="_blank" class="video-btn">원본 영상 보기</a></div></div>\n\n'
                    video_div.replace_with(soup.new_string(video_html))
                except: pass
            
            # 유튜브 iframe이 있을 경우 처리
            iframe = video_div.select_one('iframe')
            if iframe and 'youtube.com' in iframe.get('src', ''):
                src = iframe['src']
                yt_html = f'\n\n<div class="video-wrapper"><iframe src="{src}" frameborder="0" allowfullscreen></iframe></div>\n\n'
                video_div.replace_with(soup.new_string(yt_html))

        # 3. 링크 카드 처리
        for og in content_div.select('.se-oglink, .se-module-oglink'):
            a = og.find('a')
            if a and a.get('href'):
                href = a['href']
                title = og.select_one('.se-oglink-title, .se-module-oglink-title')
                title_txt = title.get_text(strip=True) if title else "상세보기"
                link_markdown = f'\n\n🔗 [{title_txt}]({href})\n\n'
                og.replace_with(soup.new_string(link_markdown))

        # 4. 이미지 처리
        for a in content_div.select('a'):
            href = a.get('href', '')
            if not href or href.startswith('#') or 'postView' in href: a.unwrap()
        for img in content_div.select('img'):
            src = img.get('src', '')
            if src: img['src'] = re.sub(r'\?type=\w+', '?type=w800', src)

        # 불필요 요소 제거 (이미 처리한 지도는 제외)
        for tag in content_div.select('.se-sticker'): tag.decompose()
            
        # 마크다운 변환
        md = markdownify.markdownify(str(content_div), heading_style="ATX")

        # 5. 이미지 그리드 처리
        def replace_images(match):
            text = match.group(0).strip()
            urls = re.findall(r'!\[.*?\]\((.*?)\)', text)
            if not urls: return text
            if len(urls) >= 2:
                img_tags = "\n".join([f'<img src="{url}" />' for url in urls])
                return f'\n<div class="image-grid">\n{img_tags}\n</div>\n\n'
            else:
                return f'\n<div class="single-image">\n<img src="{urls[0]}" />\n</div>\n\n'

        img_pattern = r'(?:!\[.*?\]\([^\)]+\)\s*)+'
        md = re.sub(img_pattern, replace_images, md)
        
        # 제목 추출
        title_tag = soup.select_one('div.se-title-text, h3.se_textarea, .pcol1')
        title = title_tag.get_text(strip=True) if title_tag else f"post_{log_no}"
        
        return {"title": title, "md": md}
    except Exception as e:
        print(f"Error migrating {log_no}: {e}")
        return None

def save_post(blog_id, log_no, result):
    title = result["title"]
    md_content = result["md"]
    date_str = time.strftime("%Y-%m-%d")
    
    cat_dir = os.path.join(BASE_DIR, "Samples")
    os.makedirs(cat_dir, exist_ok=True)
    fpath = os.path.join(cat_dir, f"{log_no}.md")
    
    safe_title = title.replace('"', "'")
    with open(fpath, "w", encoding="utf-8") as f:
        f.write("---\n")
        f.write(f'title: "{safe_title}"\n')
        f.write(f'date: {date_str}\n')
        f.write(f'category: "Sample"\n')
        f.write(f'logNo: {log_no}\n')
        f.write("---\n\n")
        f.write(md_content)

if __name__ == "__main__":
    # 요청하신 지도/동영상 포함 샘플 추가
    TARGETS = ["224274812197", "224266605150", "223940541814", "224275450829", "224266511228"]
    for log_no in TARGETS:
        print(f"수집 중: {log_no}...")
        result = get_post_content(BLOG_ID, log_no)
        if result:
            save_post(BLOG_ID, log_no, result)
    print("지도 및 동영상 포함 샘플 업데이트 완료!")
