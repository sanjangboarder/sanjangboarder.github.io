# -*- coding: utf-8 -*-
"""
Naver Blog Translation Engine (Gemini-Powered)
- Reads local Korean posts from `src/content/posts/`
- Translates content (Title, Description, Body) to English using gemini-2.5-flash
- Maps Korean category names to English
- Preserves all markdown formatting, custom map/video cards, and images
- Saves translations to `src/content/posts/en/[Category_EN]/` with lang: "en"
"""
import os
import re
import time
import json
import sys
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

# Force UTF-8 encoding on Windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

load_dotenv()

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src", "content", "posts"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

CATEGORY_MAP = {
    "바다낚시 팁_정보": "Sea Fishing Tips & Info",
    "수도권 조행기": "Metropolitan Fishing Reports",
    "전국구 조행기": "National Fishing Reports",
    "해루질 이야기": "Foraging & Crab Collecting",
    "낚시용품 리뷰": "Fishing Gear Reviews",
    "낚시용품": "Fishing Gear Reviews",
    "알리제품 리뷰": "AliExpress Product Reviews",
    "알리익스프레스": "AliExpress Product Reviews",
    "장소_맛집 리뷰": "Travel & Restaurant Reviews",
    "장소/맛집": "Travel & Restaurant Reviews",
    "IT기기_SW_드론 리뷰": "IT, Software & Drones",
    "IT기기/SW/드론": "IT, Software & Drones",
    "이벤트_체험단": "Events & Sponsorings",
    "이벤트/체험단": "Events & Sponsorings",
    "운동_레져정보": "Sports & Leisure Info",
    "자전거": "Cycling",
    "캠핑": "Camping",
    "걷기다이어트": "Walking & Diet",
    "겨울레져활동": "Winter Leisure",
    "스포츠이야기": "Sports Stories",
    "자동차_오토모티브": "Automotive",
    "자동차/오토모티브": "Automotive",
    "AI, SW개발, DevOps": "AI, Software Dev & DevOps",
    "경제관련공부": "Economics Study",
    "나의 관심정보": "My Interests",
    "함께 쓰는 게시판": "Shared Board",
    "기억하고 싶은 글": "Memorable Writings"
}

def safe_filename(text, max_len=60):
    # Keep alphanumeric characters, spaces, hyphens, and underscores
    return "".join(c for c in text if c.isalnum() or c in (' ', '-', '_')).strip()[:max_len]

def sanitize_yaml(v):
    if v is None: return ""
    return str(v).replace('\\', '\\\\').replace('\n', ' ').replace('\r', '').replace('"', "'").strip()

def parse_frontmatter(content):
    """Simple frontmatter parser"""
    match = re.match(r'^---\r?\n(.*?)\r?\n---\r?\n(.*)$', content, re.DOTALL)
    if not match:
        return {}, content
    
    fm_text = match.group(1)
    body = match.group(2)
    
    fm = {}
    for line in fm_text.split('\n'):
        if ':' in line:
            k, v = line.split(':', 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            fm[k] = v
            
    return fm, body

class PostTranslator:
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not configured in .env file.")
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    def translate_post(self, title, description, body):
        """Translates metadata (JSON) and body (raw text) separately for maximum robustness"""
        # 1. Translate metadata
        meta_prompt = f"""
Translate the following Korean blog post title and description to English.
Output ONLY as a JSON object with keys "title" and "description". Do not add any formatting code blocks other than json.

Title: {title}
Description: {description}
"""
        title_en, desc_en = title, description
        try:
            response = self.model.generate_content(meta_prompt)
            text = response.text.strip()
            # extract JSON
            res_json = None
            try:
                res_json = json.loads(text)
            except:
                match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
                if match:
                    try:
                        res_json = json.loads(match.group(1))
                    except: pass
            if not res_json:
                match_braces = re.search(r'(\{.*\})', text, re.DOTALL)
                if match_braces:
                    try:
                        res_json = json.loads(match_braces.group(1))
                    except: pass
            if res_json:
                title_en = res_json.get("title", title)
                desc_en = res_json.get("description", description)
        except Exception as e:
            print(f"      [Metadata Translation Error] {e}")

        # 2. Translate body
        body_prompt = f"""
Translate the following Korean blog post body into natural, high-quality English.
Maintain the friendly, informative, and professional tone of the original author.

Rules:
1. Keep all markdown structure (headings like # or ##, bullet points, bold/italic, tables, links, images) exactly as they are.
2. Keep custom HTML elements (such as map cards, video link cards, grids, etc.) intact, but translate the text labels within them to English (e.g. "지도 보기" -> "View Map", "영상 확인하기" -> "Watch Video", "네이버 블로그 앱/웹에서 고화질로 시청 가능합니다." -> "High quality view available on Naver Blog app/web.", etc.).
3. Do not modify or translate image URLs or hyperlink URLs. Keep them exactly as they are.
4. Output ONLY the translated body text. Do not output any markdown headers for the title, introductory text, or explanations.

[Korean Body]
{body}
"""
        body_en = body
        try:
            response = self.model.generate_content(body_prompt)
            body_en = response.text.strip()
            # Unwrap if model wrapped the raw text response in markdown code blocks
            if body_en.startswith("```markdown") and body_en.endswith("```"):
                body_en = body_en[11:-3].strip()
            elif body_en.startswith("```") and body_en.endswith("```"):
                body_en = body_en[3:-3].strip()
        except Exception as e:
            print(f"      [Body Translation Error] {e}")

        return title_en, desc_en, body_en

def translate_all_new_posts(limit=10):
    print(">>> 시작: 한국어 포스트 영어 번역 엔진 가동...")
    translator = PostTranslator()
    
    posts_path = Path(BASE_DIR)
    if not posts_path.exists():
        print(f"Error: Base directory {BASE_DIR} does not exist.")
        return

    # Find all Korean posts (excluding 'en' subfolder and 'Samples' folder)
    all_md_files = []
    for fp in posts_path.rglob("*.md"):
        relative_path = fp.relative_to(posts_path)
        parts = relative_path.parts
        if 'en' in parts or 'Samples' in parts or '.deleted' in parts:
            continue
        all_md_files.append(fp)

    # Sort files by name/date descending to translate latest first
    all_md_files.sort(key=lambda x: x.name, reverse=True)
    print(f"  총 대상 한국어 포스트 수: {len(all_md_files)}개")

    translated_count = 0
    for fp in all_md_files:
        if translated_count >= limit:
            print(f"\n[알림] 설정된 번역 제한 개수({limit}개)에 도달하여 중단합니다.")
            break

        # Extract post name & logNo
        match = re.search(r'_(\d{10,13})_', fp.name)
        if not match:
            continue
        log_no = match.group(1)
        
        # Parse existing file
        with open(fp, "r", encoding="utf-8") as f:
            raw_content = f.read()
            
        fm, body = parse_frontmatter(raw_content)
        title = fm.get("title", "")
        description = fm.get("description", "")
        category_ko = fm.get("category", "")
        category_no = fm.get("categoryNo", "0")
        date_str = fm.get("date", "")
        source = fm.get("source", "")
        thumbnail = fm.get("thumbnail", "")

        # Mapped English Category
        category_en = CATEGORY_MAP.get(category_ko, "General")
        
        # Destination Path
        cat_dir_en = os.path.join(BASE_DIR, "en", safe_filename(category_en))
        
        # Scan if translation file already exists
        dest_filename_pattern = f"*{log_no}*.md"
        dest_path_obj = Path(os.path.join(BASE_DIR, "en"))
        existing_translation = list(dest_path_obj.rglob(dest_filename_pattern))
        
        if existing_translation:
            # Already translated, skip
            continue

        print(f"\n  [{translated_count+1}] 번역 중: {date_str} | {title[:40]}...")
        
        # Perform Translation
        t_start = time.time()
        title_en, desc_en, body_en = translator.translate_post(title, description, body)
        t_end = time.time()
        
        # Save translated post
        os.makedirs(cat_dir_en, exist_ok=True)
        dest_file_name = f"{date_str}_{log_no}_{safe_filename(title_en)}.md"
        dest_file_path = os.path.join(cat_dir_en, dest_file_name)
        
        frontmatter_en = f"""---
title: "{sanitize_yaml(title_en)}"
date: {date_str}
category: "{sanitize_yaml(category_en)}"
categoryNo: {category_no}
logNo: {log_no}
source: "{source}"
thumbnail: "{thumbnail}"
description: "{sanitize_yaml(desc_en)}"
lang: "en"
---

{body_en.strip()}"""

        with open(dest_file_path, "w", encoding="utf-8") as f:
            f.write(frontmatter_en)
            
        print(f"    [완료] 저장됨 -> en/{safe_filename(category_en)}/{dest_file_name} (소요시간: {t_end - t_start:.1f}초)")
        translated_count += 1
        time.sleep(1.5) # Sleep to avoid rate limits

    print(f"\n============================================================")
    print(f"[완료] 총 {translated_count}개의 포스트 영어 번역이 생성되었습니다.")
    print(f"============================================================")

if __name__ == "__main__":
    # Translate latest 12 new posts
    translate_all_new_posts(limit=12)
