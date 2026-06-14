# -*- coding: utf-8 -*-
"""
네이버 블로그 동기화 도구 (최신 레이아웃 호환)
- 이미 존재하는 포스트는 건너뛰고 새 포스트만 가져옵니다.
- 지도, 영상, 이미지 그리드 등 최신 프리미엄 레이아웃을 적용합니다.
"""
import os
import re
import time
import json
import requests
import sys
from bs4 import BeautifulSoup
import markdownify
from pathlib import Path
from datetime import datetime, timezone

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BLOG_ID   = "sanjangboarder"
BASE_DIR  = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src", "content", "posts"))
HEADERS   = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://m.blog.naver.com/",
}

CATEGORIES = [
    (26, "바다낚시 팁_정보"), (3, "수도권 조행기"), (17, "전국구 조행기"),
    (48, "해루질 이야기"), (34, "낚시용품 리뷰"), (32, "알리제품 리뷰"),
    (35, "장소_맛집 리뷰"), (33, "IT기기_SW_드론 리뷰"), (25, "이벤트_체험단"),
    (36, "운동_레져정보"), (40, "자전거"), (39, "캠핑"), (37, "걷기다이어트"),
    (43, "겨울레져활동"), (44, "스포츠이야기"), (50, "자동차_오토모티브"),
    (27, "AI, SW개발, DevOps"), (55, "경제관련공부"), (13, "나의 관심정보"),
    (16, "함께 쓰는 게시판"), (14, "기억하고 싶은 글")
]

def ts_to_date(ms_timestamp):
    try:
        return datetime.fromtimestamp(ms_timestamp / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
    except:
        return "unknown"

def safe_dirname(name):
    return re.sub(r'[\\/:*?"<>|]', '_', str(name)).strip()

def safe_filename(text, max_len=60):
    return "".join(c for c in text if c.isalnum() or c in (' ', '-', '_')).strip()[:max_len]

def sanitize_yaml(v):
    if v is None: return ""
    return str(v).replace('\\', '\\\\').replace('\n', ' ').replace('\r', '').replace('"', "'").strip()

def get_existing_log_nos():
    """이미 존재하는 포스트의 logNo 집합 반환"""
    log_nos = set()
    posts_path = Path(BASE_DIR)
    if not posts_path.exists(): return log_nos
    for fp in posts_path.rglob("*.md"):
        if ".deleted" in str(fp): continue
        match = re.search(r'_(\d{10,13})_', fp.name)
        if match:
            log_nos.add(str(match.group(1)))
    return log_nos

def get_post_content(blog_id, log_no):
    url = f"https://m.blog.naver.com/{blog_id}/{log_no}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        html_text = resp.text
        soup = BeautifulSoup(html_text, 'html.parser')
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

        # 2. 동영상 처리 (영상 링크 카드 형태로 변경)
        for video_div in content_div.select('.se-module-video, .se-video, .se-component-video'):
            video_data_tag = video_div.select_one('script.__se_video_data')
            title_txt = "네이버 블로그 원본 영상"
            if video_data_tag:
                try:
                    data = json.loads(video_data_tag.string)
                    title_txt = data.get('title', title_txt)
                except: pass
            
            video_link = f"https://blog.naver.com/{blog_id}/{log_no}"
            video_html = f'''
<div class="video-link-card glass">
    <div class="v-link-info">
        <span class="v-link-icon">🎬</span>
        <div class="v-link-text">
            <div class="v-link-title">{title_txt}</div>
            <div class="v-link-desc">네이버 블로그 앱/웹에서 고화질로 시청 가능합니다.</div>
        </div>
    </div>
    <a href="{video_link}" target="_blank" class="v-link-btn">영상 확인하기</a>
</div>
'''
            video_div.replace_with(soup.new_string(video_html))

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

        # 불필요 요소 제거
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
        
        return {"title": title, "md": md.strip()}
    except Exception as e:
        print(f"    [오류] {e}")
        return None

def sync_new_posts():
    print(f"[{BLOG_ID}] 새 포스트 동기화 시작 (최신 레이아웃 적용)...")
    existing_log_nos = get_existing_log_nos()
    print(f"  기존 포스트 수: {len(existing_log_nos)}개")

    new_posts = []
    # 카테고리별로 최신 글 2페이지만 스캔
    for c_no, c_name in CATEGORIES:
        for page in range(1, 3):
            api_url = f"https://m.blog.naver.com/api/blogs/{BLOG_ID}/post-list?page={page}&pageSize=20&categoryNo={c_no}&sortType=recentpost"
            try:
                resp = requests.get(api_url, headers=HEADERS, timeout=10)
                items = resp.json().get("result", {}).get("items", [])
                if not items: break

                found_new = False
                for item in items:
                    log_no = str(item.get("logNo"))
                    if log_no in existing_log_nos: continue
                    found_new = True
                    new_posts.append((c_no, c_name, item))

                if not found_new and page > 1:
                    break
            except Exception as e:
                print(f"  [카테고리 오류] {c_name}: {e}")
                break

    if not new_posts:
        print("\n[완료] 새로 추가된 포스트가 없습니다.")
        return

    print(f"\n새로 추가된 포스트: {len(new_posts)}개")
    print("-" * 60)

    saved = 0
    for c_no, c_name, item in new_posts:
        log_no = str(item.get("logNo"))
        date_str = ts_to_date(item.get("addDate", 0))

        print(f"  [{saved+1}/{len(new_posts)}] {date_str} | logNo: {log_no}")

        result = get_post_content(BLOG_ID, log_no)
        if not result:
            print(f"    [건너뜀] 본문을 가져올 수 없습니다.")
            continue

        title = result["title"]
        content = result["md"]

        cat_dir = os.path.join(BASE_DIR, safe_dirname(c_name))
        os.makedirs(cat_dir, exist_ok=True)
        fpath = os.path.join(cat_dir, f"{date_str}_{log_no}_{safe_filename(title)}.md")

        frontmatter = f"""---
title: "{sanitize_yaml(title)}"
date: {date_str}
category: "{sanitize_yaml(c_name)}"
categoryNo: {c_no}
logNo: {log_no}
source: "https://m.blog.naver.com/{BLOG_ID}/{log_no}"
thumbnail: "{item.get('thumbnailUrl', '')}"
description: "{sanitize_yaml(item.get('briefContents', ''))}"
---

{content}"""

        with open(fpath, "w", encoding="utf-8") as f:
            f.write(frontmatter)

        print(f"    [저장완료] {os.path.basename(fpath)}")
        saved += 1
        time.sleep(1.0)

    print(f"\n{'='*60}")
    print(f"[완료] 동기화: {saved}개 포스트 추가됨")
    print(f"{'='*60}")

if __name__ == "__main__":
    sync_new_posts()
