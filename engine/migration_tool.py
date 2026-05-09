"""
네이버 블로그 마이그레이션 도구 (requests 기반 - 카테고리 포함)
- post-list API에서 categoryName, addDate, thumbnailUrl 추출
- 카테고리별 폴더 구조로 저장
- Astro 호환 Frontmatter 형식으로 메타데이터 기록
"""

import os
import re
import time
import json
import requests
from datetime import datetime, timezone
from bs4 import BeautifulSoup
import markdownify

BLOG_ID   = "sanjangboarder"
BASE_DIR  = os.path.join(os.path.dirname(__file__), "data", "raw_posts")
HEADERS   = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9",
    "Referer": "https://m.blog.naver.com/",
}

# ──────────────────────────────────────────
# 유틸
# ──────────────────────────────────────────
def ts_to_date(ms_timestamp):
    """밀리초 타임스탬프 → 'YYYY-MM-DD' 문자열"""
    try:
        return datetime.fromtimestamp(ms_timestamp / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
    except:
        return "unknown"

def safe_dirname(name):
    """카테고리명을 폴더명으로 사용할 수 있게 정리"""
    return re.sub(r'[\\/:*?"<>|]', '_', name).strip()

def safe_filename(text, max_len=60):
    """파일명에 사용할 수 없는 문자 제거"""
    return "".join(c for c in text if c.isalnum() or c in (' ', '-', '_')).strip()[:max_len]

# ──────────────────────────────────────────
# 1. 글 목록 수집 (API 기반)
# ──────────────────────────────────────────
def get_all_post_list(blog_id, max_posts=2000):
    """post-list API로 전체 글 목록 수집 (카테고리 포함)"""
    all_items = []
    categories = {}   # categoryNo → categoryName 매핑
    page, page_size = 1, 30

    print(f"\n[글 목록 수집 시작] 블로그: {blog_id}")
    while len(all_items) < max_posts:
        url = (
            f"https://m.blog.naver.com/api/blogs/{blog_id}/post-list"
            f"?page={page}&pageSize={page_size}&categoryNo=0&sortType=recentpost"
        )
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            if resp.status_code != 200:
                print(f"  페이지 {page} 실패: {resp.status_code}")
                break

            data = resp.json()
            items = data.get("result", {}).get("items", [])
            if not items:
                print(f"  페이지 {page}: 더 이상 글이 없습니다.")
                break

            for item in items:
                cat_no   = item.get("categoryNo", 0)
                cat_name = item.get("categoryName", "미분류")
                if cat_no not in categories:
                    categories[cat_no] = cat_name

            all_items.extend(items)
            print(f"  페이지 {page} 수집: {len(items)}개 (누적: {len(all_items)}개)")
            page += 1
            time.sleep(0.5)

        except Exception as e:
            print(f"  페이지 {page} 오류: {e}")
            break

    print(f"\n[글 목록 수집 완료] 총 {len(all_items)}개")
    print(f"[발견된 카테고리 {len(categories)}개]")
    for no, name in sorted(categories.items()):
        print(f"  - [{no}] {name}")

    # 카테고리 목록을 JSON으로 저장 (나중에 Astro 메뉴 생성에 활용)
    cat_file = os.path.join(os.path.dirname(__file__), "data", "categories.json")
    os.makedirs(os.path.dirname(cat_file), exist_ok=True)
    with open(cat_file, "w", encoding="utf-8") as f:
        json.dump(categories, f, ensure_ascii=False, indent=2)
    print(f"  → 카테고리 목록 저장: {cat_file}")

    return all_items, categories

# ──────────────────────────────────────────
# 2. 본문 수집 및 마크다운 변환
# ──────────────────────────────────────────
def get_post_content(blog_id, log_no):
    """특정 포스트 본문을 가져와 마크다운으로 반환"""
    url = f"https://m.blog.naver.com/{blog_id}/{log_no}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return None

        soup = BeautifulSoup(resp.text, 'html.parser')

        # 제목 추출
        title_tag = (
            soup.select_one('div.se-title-text') or
            soup.select_one('h3.se_textarea')    or
            soup.select_one('.pcol1')
        )
        title = title_tag.get_text(strip=True) if title_tag else f"post_{log_no}"

        # 본문 추출
        content_div = (
            soup.select_one('div.se-main-container') or
            soup.select_one('div#postViewArea')
        )
        if not content_div:
            return None

        # 이미지 URL 썸네일 → 원본 업그레이드
        for img in content_div.select('img'):
            src = img.get('src', '')
            if src:
                img['src'] = re.sub(r'\?type=\w+', '?type=w800', src)

        # 네이버 내부 요소 제거 (지도, 스티커 등)
        for tag in content_div.select('.se-placesMap, .se-oglink, .se-sticker'):
            tag.decompose()

        markdown = markdownify.markdownify(str(content_div), heading_style="ATX")
        return {"title": title, "content": markdown}

    except Exception as e:
        print(f"    본문 오류 ({log_no}): {e}")
        return None

# ──────────────────────────────────────────
# 3. 파일 저장 (카테고리 폴더 + Frontmatter)
# ──────────────────────────────────────────
def sanitize_yaml(value: str) -> str:
    """YAML frontmatter에 안전한 문자열로 변환"""
    if not isinstance(value, str):
        return str(value)
    value = value.replace('\n', ' ').replace('\r', '')
    value = value.replace('"', "'")
    return value.strip()

def save_post(blog_id, item, title, content):
    log_no    = item.get("logNo")
    cat_name  = item.get("categoryName", "미분류")
    cat_no    = item.get("categoryNo", 0)
    date_str  = ts_to_date(item.get("addDate", 0))
    thumb_url = item.get("thumbnailUrl", "")
    brief     = item.get("briefContents", "")[:150]

    # 카테고리별 폴더 생성
    cat_dir = os.path.join(BASE_DIR, safe_dirname(cat_name))
    os.makedirs(cat_dir, exist_ok=True)

    # 파일명: YYYY-MM-DD_logNo_제목.md
    fname = f"{date_str}_{log_no}_{safe_filename(title)}.md"
    fpath = os.path.join(cat_dir, fname)

    # Astro 호환 Frontmatter + 본문 (YAML 안전 처리)
    with open(fpath, "w", encoding="utf-8") as f:
        f.write("---\n")
        f.write(f'title: "{sanitize_yaml(title)}"\n')
        f.write(f'date: {date_str}\n')
        f.write(f'category: "{sanitize_yaml(cat_name)}"\n')
        f.write(f'categoryNo: {cat_no}\n')
        f.write(f'logNo: {log_no}\n')
        f.write(f'source: "https://m.blog.naver.com/{blog_id}/{log_no}"\n')
        f.write(f'thumbnail: "{sanitize_yaml(thumb_url)}"\n')
        f.write(f'description: "{sanitize_yaml(brief)}"\n')
        f.write("---\n\n")
        f.write(content)

    return os.path.relpath(fpath, BASE_DIR)

# ──────────────────────────────────────────
# 실행
# ──────────────────────────────────────────
if __name__ == "__main__":
    TEST_MODE = False  # ✅ 전체 수집 모드
    max_posts = 10 if TEST_MODE else 2000

    print("=" * 60)
    print(f"네이버 블로그 마이그레이션 | {'테스트 (10개)' if TEST_MODE else '전체 수집'}")
    print("=" * 60)

    # Step 1: 목록 + 카테고리 수집
    post_list, categories = get_all_post_list(BLOG_ID, max_posts=max_posts)

    # Step 2 & 3: 본문 수집 + 저장
    success, fail = 0, 0
    print(f"\n[본문 수집 시작] 총 {len(post_list)}개")
    for i, item in enumerate(post_list, 1):
        log_no   = item.get("logNo")
        title    = item.get("titleWithInspectMessage", f"post_{log_no}")
        cat_name = item.get("categoryName", "미분류")
        date_str = ts_to_date(item.get("addDate", 0))

        print(f"  [{i:4d}/{len(post_list)}] [{cat_name}] {title[:35]}...")
        result = get_post_content(BLOG_ID, log_no)

        if result:
            saved = save_post(BLOG_ID, item, result["title"], result["content"])
            print(f"           ✅ {saved}")
            success += 1
        else:
            print(f"           ❌ 본문 없음 (logNo={log_no})")
            fail += 1

        time.sleep(0.3)

    print("\n" + "=" * 60)
    print(f"완료!  성공: {success}개 / 실패: {fail}개")
    print(f"저장 위치: {BASE_DIR}")
    print("=" * 60)
