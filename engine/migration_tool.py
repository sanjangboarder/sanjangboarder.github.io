"""
네이버 블로그 마이그레이션 도구 (동기화 및 삭제 처리 강화 버전)
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
    # 백슬래시는 YAML 큰따옴표 내에서 이스케이프가 필요함, 줄바꿈 제거 및 따옴표 치환
    return str(v).replace('\\', '\\\\').replace('\n', ' ').replace('\r', '').replace('"', "'").strip()

def clean_markdown(md_text):
    """마크다운 노이즈 제거"""
    md_text = re.sub(r'\[\!\[\]\((.*?)\)\]\(#\)', r'![](\1)', md_text)
    md_text = md_text.replace('\u200b', '')
    md_text = re.sub(r'\n{3,}', '\n\n', md_text)
    return md_text.strip()

def get_existing_posts():
    """로컬에 이미 있는 포스트들을 logNo 기준으로 매핑 {logNo: full_path}"""
    mapping = {}
    posts_path = Path(BASE_DIR)
    if not posts_path.exists(): return mapping
    
    for fp in posts_path.rglob("*.md"):
        if ".deleted" in str(fp): continue
        match = re.search(r'_(\d{10,13})_', fp.name)
        if match:
            mapping[str(match.group(1))] = str(fp)
        else:
            try:
                content = fp.read_text(encoding='utf-8', errors='ignore')
                fm_match = re.search(r'logNo:\s*(\d+)', content)
                if fm_match: mapping[str(fm_match.group(1))] = str(fp)
            except: pass
    return mapping

def get_post_content(blog_id, log_no):
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
                title = og.select_one('.se-oglink-title')
                txt = title.get_text(strip=True) if title else "상세보기"
                new_p = soup.new_tag('p')
                new_p.string = f"\n\n[Link: {txt}]({href})\n\n"
                og.replace_with(new_p)

        for img in content_div.select('img'):
            src = img.get('src', '')
            if src: img['src'] = re.sub(r'\?type=\w+', '?type=w800', src)

        for tag in content_div.select('.se-placesMap, .se-sticker'): tag.decompose()
            
        md = markdownify.markdownify(str(content_div), heading_style="ATX")
        return clean_markdown(md)
    except: return None

def migrate_posts(page_size=20, max_pages=1):
    print(f"[{BLOG_ID}] 마이그레이션 및 동기화 시작 (최대 {max_pages} 페이지)...")
    existing_map = get_existing_posts()
    synced_logs = set()
    
    for page in range(1, max_pages + 1):
        # 파라미터가 정확해야 200 JSON을 반환함
        api_url = f"https://m.blog.naver.com/api/blogs/{BLOG_ID}/post-list?page={page}&pageSize={page_size}&categoryNo=0&sortType=recentpost"
        try:
            resp = requests.get(api_url, headers=HEADERS, timeout=10)
            if resp.status_code != 200:
                print(f"  [오류] API 호출 실패 (상태코드: {resp.status_code})")
                break
            
            data = resp.json().get("result", {})
            items = data.get("items", [])
            if not items:
                print(f"  [알림] 더 이상 가져올 데이터가 없습니다. (Page {page})")
                break
            
            for item in items:
                log_no = str(item.get("logNo"))
                title = item.get("titleWithInspectMessage", f"post_{log_no}")
                cat_name = item.get("categoryName", "미분류")
                cat_no = item.get("categoryNo", 0)
                date_str = ts_to_date(item.get("addDate", 0))
                thumb = item.get("thumbnailUrl", "")
                desc = sanitize_yaml(item.get("briefContents", ""))
                
                synced_logs.add(log_no)
                
                # 콘텐츠 가져오기
                content = get_post_content(BLOG_ID, log_no)
                if not content: continue
                
                # 저장 경로 결정
                cat_dir = os.path.join(BASE_DIR, safe_dirname(cat_name))
                os.makedirs(cat_dir, exist_ok=True)
                new_fpath = os.path.join(cat_dir, f"{date_str}_{log_no}_{safe_filename(title)}.md")
                
                # 기존 파일 처리 (위치 변경 시 이동)
                if log_no in existing_map:
                    old_path = existing_map[log_no]
                    if os.path.abspath(old_path) != os.path.abspath(new_fpath):
                        print(f"  [이동] {log_no}: {os.path.basename(old_path)} -> {cat_name} 폴더")
                        if os.path.exists(old_path): os.remove(old_path)
                
                # 파일 저장 (항상 최신 내용으로 덮어씀)
                with open(new_fpath, "w", encoding="utf-8") as f:
                    f.write(f"---")
                    f.write(f"\ntitle: \"{sanitize_yaml(title)}\"")
                    f.write(f"\ndate: {date_str}")
                    f.write(f"\ncategory: \"{sanitize_yaml(cat_name)}\"")
                    f.write(f"\ncategoryNo: {cat_no}")
                    f.write(f"\nlogNo: {log_no}")
                    f.write(f"\nsource: \"https://m.blog.naver.com/{BLOG_ID}/{log_no}\"")
                    f.write(f"\nthumbnail: \"{thumb}\"")
                    f.write(f"\ndescription: \"{desc}\"")
                    f.write(f"\n---")
                    f.write(f"\n\n{content}")
                
                print(f"  [완료] {date_str} | {cat_name} | {title[:30]}...")
                time.sleep(0.05)
                
        except Exception as e:
            print(f"  [에러] Page {page} 처리 중 오류: {e}")
            break
    
    # 삭제된 포스트 처리 (네이버에는 없는데 로컬에는 있는 경우)
    # 단, 전체 마이그레이션(max_pages가 충분히 클 때)인 경우에만 신뢰할 수 있음
    if max_pages > 50: # 대략 1000개 이상 긁을 때만 작동
        print("\n[삭제 확인] 네이버에서 사라진 포스트를 체크합니다...")
        for lno, path in existing_map.items():
            if lno not in synced_logs:
                os.makedirs(DELETED_DIR, exist_ok=True)
                target = os.path.join(DELETED_DIR, os.path.basename(path))
                print(f"  [삭제감지] {lno} -> .deleted 폴더로 이동")
                if os.path.exists(path):
                    os.rename(path, target)

    return synced_logs

if __name__ == "__main__":
    # 테스트를 위해 1페이지만 실행. 
    # 전체 마이그레이션 시에는 max_pages를 100 정도로 설정하세요.
    synced = migrate_posts(page_size=20, max_pages=1)
    print(f"\n동기화 작업 완료! (처리된 포스트: {len(synced)}개)")
