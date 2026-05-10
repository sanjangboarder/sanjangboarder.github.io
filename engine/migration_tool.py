"""
네이버 블로그 마이그레이션 도구 (최종 안정화 버전 - 테스트 모드 포함)
"""
import os
import re
import time
import requests
from bs4 import BeautifulSoup
import markdownify
from pathlib import Path
from datetime import datetime, timezone

BLOG_ID   = "sanjangboarder"
BASE_DIR  = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src", "content", "posts"))
DELETED_DIR = os.path.join(BASE_DIR, ".deleted")
HEADERS   = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://m.blog.naver.com/",
}

# 브라우저 스캔으로 확인된 실제 카테고리 목록 (유실 방지용)
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
    except: return "unknown"

def safe_dirname(name):
    return re.sub(r'[\\/:*?"<>|]', '_', str(name)).strip()

def safe_filename(text, max_len=60):
    return "".join(c for c in text if c.isalnum() or c in (' ', '-', '_')).strip()[:max_len]

def sanitize_yaml(v):
    if v is None: return ""
    # 빌드 에러 방지를 위해 백슬래시 이스케이프 및 특수기호 정리
    return str(v).replace('\\', '\\\\').replace('\n', ' ').replace('\r', '').replace('"', "'").strip()

def clean_markdown(md_text, title=""):
    """마크다운 노이즈 제거 및 본문 최적화"""
    # 1. 네이버 특유의 이미지 링크 노이즈 제거
    md_text = re.sub(r'\[\!\[\]\((.*?)\)\]\(#\)', r'![](\1)', md_text)
    
    # 2. 연속된 이미지 사이의 빈 줄 제거 (한 줄에 나란히 배치하기 위함)
    md_text = re.sub(r'(\!\[.*?\]\(.*?\))\s*\n\s*(\!\[.*?\]\(.*?\))', r'\1\n\2', md_text)
    md_text = re.sub(r'(\!\[.*?\]\(.*?\))\s*\n\s*(\!\[.*?\]\(.*?\))', r'\1\n\2', md_text)
    
    # 3. 본문 상단 중복 제목 및 깨진 아이콘 제거
    if title:
        title_keywords = [k for k in re.findall(r'[가-힣\w]+', title) if len(k) > 1]
        lines = md_text.split('\n')
        body_lines = []
        skipped_redundant = False
        text_count = 0
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                body_lines.append(line)
                continue
            
            text_count += 1
            if not skipped_redundant and text_count <= 5:
                # 굵은 글씨나 제목 태그이면서 제목과 유사한 경우
                clean_line = re.sub(r'[\*#🚗🚌🚢🎣💡🚀😱🐢💣🧪]', '', stripped).strip()
                match_count = sum(1 for k in title_keywords if k in clean_line)
                if match_count >= len(title_keywords) * 0.4 or clean_line in title or len(clean_line) < 3:
                    skipped_redundant = True
                    continue # 해당 라인 건너뜀
            body_lines.append(line)
        md_text = '\n'.join(body_lines)

    md_text = md_text.replace('\u200b', '')
    md_text = re.sub(r'\n{3,}', '\n\n', md_text)
    return md_text.strip()

def get_existing_posts():
    mapping = {}
    posts_path = Path(BASE_DIR)
    if not posts_path.exists(): return mapping
    for fp in posts_path.rglob("*.md"):
        if ".deleted" in str(fp): continue
        match = re.search(r'_(\d{10,13})_', fp.name)
        if match: mapping[str(match.group(1))] = str(fp)
    return mapping

def get_post_content(blog_id, log_no, title=""):
    url = f"https://m.blog.naver.com/{blog_id}/{log_no}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        content_div = (soup.select_one('div.se-main-container') or soup.select_one('div#postViewArea'))
        if not content_div: return None

        for og in content_div.select('.se-oglink, .se-module-oglink'):
            a = og.find('a')
            if a and a.get('href'):
                href = a['href']
                og_title = og.select_one('.se-oglink-title')
                txt = og_title.get_text(strip=True) if og_title else "상세보기"
                new_p = soup.new_tag('p')
                new_p.string = f"\n\n[Link: {txt}]({href})\n\n"
                og.replace_with(new_p)

        for img in content_div.select('img'):
            src = img.get('src', '')
            if src: img['src'] = re.sub(r'\?type=\w+', '?type=w800', src)

        for tag in content_div.select('.se-placesMap, .se-sticker'): tag.decompose()
        md = markdownify.markdownify(str(content_div), heading_style="ATX")
        return clean_markdown(md, title)
    except: return None

def migrate_all(test_mode=True):
    print(f"[{BLOG_ID}] 마이그레이션 시작 (테스트 모드: {test_mode})")
    existing_map = get_existing_posts()
    synced_logs = set()
    total = 0

    for c_no, c_name in CATEGORIES:
        print(f"\n>>> 카테고리: {c_name}")
        for page in range(1, 51):
            api_url = f"https://m.blog.naver.com/api/blogs/{BLOG_ID}/post-list?page={page}&pageSize=20&categoryNo={c_no}&sortType=recentpost"
            try:
                resp = requests.get(api_url, headers=HEADERS, timeout=10)
                items = resp.json().get("result", {}).get("items", [])
                if not items: break
                
                for item in items:
                    log_no = str(item.get("logNo"))
                    if log_no in synced_logs: continue
                    
                    title = item.get("titleWithInspectMessage", f"post_{log_no}")
                    date_str = ts_to_date(item.get("addDate", 0))
                    
                    content = get_post_content(BLOG_ID, log_no, title)
                    if not content: continue
                    
                    synced_logs.add(log_no)
                    total += 1
                    
                    cat_dir = os.path.join(BASE_DIR, safe_dirname(c_name))
                    os.makedirs(cat_dir, exist_ok=True)
                    new_fpath = os.path.join(cat_dir, f"{date_str}_{log_no}_{safe_filename(title)}.md")
                    
                    if log_no in existing_map and os.path.abspath(existing_map[log_no]) != os.path.abspath(new_fpath):
                        if os.path.exists(existing_map[log_no]): os.remove(existing_map[log_no])
                    
                    with open(new_fpath, "w", encoding="utf-8") as f:
                        f.write(f"---\ntitle: \"{sanitize_yaml(title)}\"\ndate: {date_str}\ncategory: \"{sanitize_yaml(c_name)}\"\ncategoryNo: {c_no}\nlogNo: {log_no}\nsource: \"https://m.blog.naver.com/{BLOG_ID}/{log_no}\"\nthumbnail: \"{item.get('thumbnailUrl', '')}\"\ndescription: \"{sanitize_yaml(item.get('briefContents', ''))}\"\n---\n\n{content}")
                    
                    print(f"  [{total}] {date_str} | {title[:40]}...")
                    time.sleep(1.0) # 네이버 배려를 위한 충분한 지연 시간 (1초)
                    
                    if test_mode and total >= 5: return synced_logs
            except: break
    return synced_logs

if __name__ == "__main__":
    # 외출하신 동안 천천히(1초 간격) 전체 포스트를 가져옵니다.
    migrate_all(test_mode=False)
