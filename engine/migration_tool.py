"""
네이버 블로그 마이그레이션 도구 (링크 보존 초강화 최종판)
"""
import os
import re
import time
import requests
from bs4 import BeautifulSoup
import markdownify

BLOG_ID   = "sanjangboarder"
BASE_DIR  = os.path.join(os.path.dirname(__file__), "..", "src", "content", "posts")
HEADERS   = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://m.blog.naver.com/",
}

def ts_to_date(ms_timestamp):
    try:
        from datetime import datetime, timezone
        return datetime.fromtimestamp(ms_timestamp / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
    except:
        return "unknown"

def safe_dirname(name):
    return re.sub(r'[\\/:*?"<>|]', '_', name).strip()

def safe_filename(text, max_len=60):
    return "".join(c for c in text if c.isalnum() or c in (' ', '-', '_')).strip()[:max_len]

def get_post_content(blog_id, log_no):
    url = f"https://m.blog.naver.com/{blog_id}/{log_no}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        content_div = (soup.select_one('div.se-main-container') or soup.select_one('div#postViewArea'))
        if not content_div: return None

        # 1. 모든 링크 박스(OG 링크)를 명시적 마크다운 링크로 변환
        for og in content_div.select('.se-oglink, .se-module-oglink'):
            a = og.find('a')
            if a and a.get('href'):
                href = a['href']
                title = og.select_one('.se-oglink-title')
                txt = title.get_text(strip=True) if title else "상세보기"
                # 링크를 강조하여 텍스트로 삽입
                new_p = soup.new_tag('p')
                new_p.string = f"\n\n[Link: {txt}]({href})\n\n"
                og.replace_with(new_p)

        # 2. 이미지 주소 변환 (고해상도)
        for img in content_div.select('img'):
            src = img.get('src', '')
            if src: img['src'] = re.sub(r'\?type=\w+', '?type=w800', src)

        # 3. 지도/스티커 등 불필요 요소 제거
        for tag in content_div.select('.se-placesMap, .se-sticker'): tag.decompose()
            
        return markdownify.markdownify(str(content_div), heading_style="ATX")
    except: return None

def sanitize_yaml(v):
    return str(v).replace('\n', ' ').replace('\r', '').replace('"', "'").strip()

if __name__ == "__main__":
    # 최근 10개 샘플 수집 시작
    print(f"[{BLOG_ID}] 최근 10개 샘플 수집 시작...")
    resp = requests.get(f"https://m.blog.naver.com/api/blogs/{BLOG_ID}/post-list?pageSize=10", headers=HEADERS)
    items = resp.json().get("result", {}).get("items", [])
    
    for i, item in enumerate(items, 1):
        log_no = item.get("logNo")
        title = item.get("titleWithInspectMessage", f"post_{log_no}")
        cat_name = item.get("categoryName", "미분류")
        date_str = ts_to_date(item.get("addDate", 0))
        
        c = get_post_content(BLOG_ID, log_no)
        if c:
            cat_dir = os.path.join(BASE_DIR, safe_dirname(cat_name))
            os.makedirs(cat_dir, exist_ok=True)
            fpath = os.path.join(cat_dir, f"{date_str}_{log_no}_{safe_filename(title)}.md")
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(f"---\ntitle: \"{sanitize_yaml(title)}\"\ndate: {date_str}\ncategory: \"{sanitize_yaml(cat_name)}\"\nlogNo: {log_no}\n---\n\n{c}")
            print(f"  [{i}/10] 수집 완료: {os.path.basename(fpath)}")
        time.sleep(0.3)
    print("\n샘플 10개 수집이 완료되었습니다!")
