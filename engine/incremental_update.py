# -*- coding: utf-8 -*-
"""
네이버 블로그 증분 업데이트 도구
- 이미 존재하는 포스트(logNo 기준)는 건너뜁니다.
- 새로 추가된 포스트만 가져와서 저장합니다.
"""
import os
import re
import time
import sys
import requests
from bs4 import BeautifulSoup
import markdownify

# Windows 콘솔 UTF-8 출력 강제 설정
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from pathlib import Path
from datetime import datetime, timezone

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

def clean_markdown(md_text, title=""):
    md_text = re.sub(r'\[!\[\]\((.*?)\)\]\(#\)', r'![](\1)', md_text)
    md_text = re.sub(r'(!\[.*?\]\(.*?\))\s*\n\s*(!\[.*?\]\(.*?\))', r'\1\n\2', md_text)
    md_text = re.sub(r'(!\[.*?\]\(.*?\))\s*\n\s*(!\[.*?\]\(.*?\))', r'\1\n\2', md_text)

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
                clean_line = re.sub(r'[\*#🚗🚌🚢🎣💡🚀😱🐢💣🧪]', '', stripped).strip()
                match_count = sum(1 for k in title_keywords if k in clean_line)
                if match_count >= len(title_keywords) * 0.4 or clean_line in title or len(clean_line) < 3:
                    skipped_redundant = True
                    continue
            body_lines.append(line)
        md_text = '\n'.join(body_lines)

    md_text = md_text.replace('\u200b', '')
    md_text = re.sub(r'\n{3,}', '\n\n', md_text)
    return md_text.strip()

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
    except Exception as e:
        print(f"    [오류] {e}")
        return None

def incremental_update():
    print(f"[{BLOG_ID}] 증분 업데이트 시작...")
    existing_log_nos = get_existing_log_nos()
    print(f"  기존 포스트 수: {len(existing_log_nos)}개")

    new_posts = []
    # 카테고리별로 최신 글 2페이지만 스캔 (최근 40개씩)
    for c_no, c_name in CATEGORIES:
        for page in range(1, 3):  # 최대 2페이지 = 40개
            api_url = f"https://m.blog.naver.com/api/blogs/{BLOG_ID}/post-list?page={page}&pageSize=20&categoryNo={c_no}&sortType=recentpost"
            try:
                resp = requests.get(api_url, headers=HEADERS, timeout=10)
                items = resp.json().get("result", {}).get("items", [])
                if not items: break

                found_new = False
                for item in items:
                    log_no = str(item.get("logNo"))
                    if log_no in existing_log_nos:
                        continue  # 이미 존재하는 글 스킵
                    # 새 글 발견
                    found_new = True
                    new_posts.append((c_no, c_name, item))

                if not found_new and page > 1:
                    break  # 2페이지에서 새 글이 없으면 더 이상 스캔 불필요
            except Exception as e:
                print(f"  [카테고리 오류] {c_name}: {e}")
                break

    if not new_posts:
        print("\n[완료] 새로 추가된 포스트가 없습니다. 이미 최신 상태입니다.")
        return

    print(f"\n새로 추가된 포스트: {len(new_posts)}개")
    print("-" * 60)

    saved = 0
    for c_no, c_name, item in new_posts:
        log_no = str(item.get("logNo"))
        title = item.get("titleWithInspectMessage", f"post_{log_no}")
        date_str = ts_to_date(item.get("addDate", 0))

        print(f"  [{saved+1}/{len(new_posts)}] {date_str} | {title[:50]}")

        content = get_post_content(BLOG_ID, log_no, title)
        if not content:
            print(f"    [건너뜀] 본문을 가져올 수 없습니다.")
            continue

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
    print(f"[완료] 증분 업데이트: {saved}개 포스트 추가됨")
    print(f"{'='*60}")

if __name__ == "__main__":
    incremental_update()
