# -*- coding: utf-8 -*-
"""
Naver Blog Post Validation Script
- Scans all posts in `src/content/posts/`
- Validates frontmatter fields (title, date, logNo, lang, etc.)
- Ensures English posts map correctly to Korean posts via logNo
- Detects unescaped quotes in YAML frontmatter
- Scans English posts for untranslated Korean text
"""
import os
import re
import sys
from pathlib import Path

# Force UTF-8 encoding on Windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src", "content", "posts"))

CATEGORY_MAP_VALUES = {
    "Sea Fishing Tips & Info", "Metropolitan Fishing Reports", "National Fishing Reports",
    "Foraging & Crab Collecting", "Fishing Gear Reviews", "AliExpress Product Reviews",
    "Travel & Restaurant Reviews", "IT, Software & Drones", "Events & Sponsorings",
    "Sports & Leisure Info", "Cycling", "Camping", "Walking & Diet", "Winter Leisure",
    "Sports Stories", "Automotive", "AI, Software Dev & DevOps", "Economics Study",
    "My Interests", "Shared Board", "Memorable Writings", "General"
}

def parse_frontmatter(content):
    """Simple frontmatter parser"""
    match = re.match(r'^---\r?\n(.*?)\r?\n---\r?\n(.*)$', content, re.DOTALL)
    if not match:
        return {}, content, "Missing frontmatter delimiters (---)"
    
    fm_text = match.group(1)
    body = match.group(2)
    
    fm = {}
    errors = []
    for line_num, line in enumerate(fm_text.split('\n'), start=2):
        if not line.strip():
            continue
        if ':' not in line:
            errors.append(f"Line {line_num}: Invalid YAML line (missing ':')")
            continue
        k, v = line.split(':', 1)
        k = k.strip()
        v = v.strip()
        
        # Check for duplicate key
        if k in fm:
            errors.append(f"Line {line_num}: Duplicated mapping key '{k}'")
        
        # Check for unescaped double quotes inside frontmatter values
        if v.startswith('"') and v.endswith('"'):
            inner = v[1:-1]
            if '"' in inner and '\\"' not in inner:
                errors.append(f"Line {line_num}: Unescaped double quotes found inside value for '{k}'")
        
        # Strip quotes for parsed value
        v = v.strip('"').strip("'")
        fm[k] = v
            
    return fm, body, "; ".join(errors) if errors else None

def has_korean(text):
    """Returns True if the text contains Korean characters"""
    return bool(re.search(r'[\uac00-\ud7a3\u1100-\u11ff\u3130-\u318f]', text))

def count_korean_chars(text):
    """Counts the number of Korean characters in text"""
    return len(re.findall(r'[\uac00-\ud7a3]', text))

def validate_posts():
    posts_path = Path(BASE_DIR)
    if not posts_path.exists():
        print(f"Error: Base directory {BASE_DIR} does not exist.")
        sys.exit(1)

    print(">>> 블로그 포스팅 검증 스크립트 실행 시작...")
    
    # 1. Gather all md files
    all_files = list(posts_path.rglob("*.md"))
    print(f"  검사 대상 마크다운 파일 수: {len(all_files)}개")

    ko_posts = {}
    en_posts = {}
    
    errors = []
    warnings = []

    for fp in all_files:
        rel_path = fp.relative_to(posts_path)
        parts = rel_path.parts
        
        # Skip samples or deleted folders
        if 'Samples' in parts or '.deleted' in parts:
            continue
            
        is_en = 'en' in parts
        
        with open(fp, "r", encoding="utf-8") as f:
            raw_content = f.read()
            
        fm, body, fm_err = parse_frontmatter(raw_content)
        
        filename = fp.name
        rel_str = str(rel_path).replace('\\', '/')
        
        if fm_err:
            errors.append(f"[{rel_str}] Frontmatter 파싱 오류: {fm_err}")
            continue
            
        title = fm.get("title", "")
        date = fm.get("date", "")
        log_no = fm.get("logNo", "")
        lang = fm.get("lang", "ko")
        category = fm.get("category", "")
        
        # Validate critical fields existence
        if not title:
            errors.append(f"[{rel_str}] 필수 필드 누락: 'title'")
        if not date:
            errors.append(f"[{rel_str}] 필수 필드 누락: 'date'")
        if not log_no:
            errors.append(f"[{rel_str}] 필수 필드 누락: 'logNo'")
            
        # Store in dicts for mapping validation
        if log_no:
            if is_en:
                if log_no in en_posts:
                    warnings.append(f"[{rel_str}] 중복된 영문 logNo 감지: {log_no}")
                en_posts[log_no] = {
                    "path": rel_str,
                    "title": title,
                    "category": category,
                    "date": date,
                    "body": body,
                    "description": fm.get("description", "")
                }
            else:
                if log_no in ko_posts:
                    warnings.append(f"[{rel_str}] 중복된 국문 logNo 감지: {log_no}")
                ko_posts[log_no] = {
                    "path": rel_str,
                    "title": title,
                    "category": category,
                    "date": date
                }

        # Language specific check
        if is_en:
            if lang != "en":
                errors.append(f"[{rel_str}] 영문 폴더 하위에 존재하나 lang 필드가 'en'이 아님 (현재: '{lang}')")
            
            # Category name standard check
            if category and category not in CATEGORY_MAP_VALUES:
                warnings.append(f"[{rel_str}] 비표준 영문 카테고리 명 감지: '{category}'")
                
            # Check for leftover Korean text in English posts
            title_ko_chars = count_korean_chars(title)
            desc_ko_chars = count_korean_chars(fm.get("description", ""))
            body_ko_chars = count_korean_chars(body)
            
            if title_ko_chars > 0:
                errors.append(f"[{rel_str}] 영문 제목에 한국어 문자 감지 ({title_ko_chars}개)")
            if desc_ko_chars > 5:  # Allow small threshold for Korean names/proper nouns
                errors.append(f"[{rel_str}] 영문 요약(description)에 다수의 한국어 문자 감지 ({desc_ko_chars}개)")
            if body_ko_chars > 30:  # Allow small threshold for Korean nouns (e.g. 찌스, 아오맥스, etc.)
                errors.append(f"[{rel_str}] 영문 본문에 다수의 한국어 문자 감지 ({body_ko_chars}개) - 번역 누락 의심")

    # 2. Validate translation mapping (English -> Korean)
    for log_no, en_post in en_posts.items():
        if log_no not in ko_posts:
            warnings.append(f"[{en_post['path']}] 번역본이 있으나 해당하는 국문 원본 포스트(logNo: {log_no})를 찾을 수 없음")
            
    print("\n============================================================")
    print("📋 검증 결과 리포트")
    print("============================================================")
    print(f"  * 분석 완료된 국문 포스트: {len(ko_posts)}개")
    print(f"  * 분석 완료된 영문 포스트: {len(en_posts)}개")
    
    print(f"\n🚨 오류 (Errors): {len(errors)}개")
    for err in errors:
        print(f"  - {err}")
        
    print(f"\n⚠️ 경고 (Warnings): {len(warnings)}개")
    for warn in warnings:
        print(f"  - {warn}")
        
    print("============================================================")
    
    if errors:
        print("❌ 검증 실패: 치명적인 구조적 오류가 발견되었습니다.")
        sys.exit(1)
    else:
        print("✅ 검증 완료: 모든 포스팅 무결성 및 구조 체크를 통과했습니다.")
        sys.exit(0)

if __name__ == "__main__":
    validate_posts()
