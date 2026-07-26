# -*- coding: utf-8 -*-
import os
import re
import json
from pathlib import Path

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src", "content", "posts"))

CATEGORY_MAP = {
    "바다낚시 팁_정보": "Sea Fishing Tips & Info",
    "수도권 조행기": "Metropolitan Fishing Reports",
    "전국구 조행기": "National Fishing Reports",
    "해루질 이야기": "Foraging & Crab Collecting",
    "낚시용품 리뷰": "Fishing Gear Reviews",
    "알리제품 리뷰": "AliExpress Product Reviews",
    "장소_맛집 리뷰": "Travel & Restaurant Reviews",
    "IT기기_SW_드론 리뷰": "IT, Software & Drones",
    "이벤트_체험단": "Events & Sponsorings",
    "운동_레져정보": "Sports & Leisure Info",
    "자전거": "Cycling",
    "캠핑": "Camping",
    "걷기다이어트": "Walking & Diet",
    "겨울레져활동": "Winter Leisure",
    "스포츠이야기": "Sports Stories",
    "자동차_오토모티브": "Automotive",
    "AI, SW개발, DevOps": "AI, Software Dev & DevOps",
    "경제관련공부": "Economics Study",
    "나의 관심정보": "My Interests",
    "함께 쓰는 게시판": "Shared Board",
    "기억하고 싶은 글": "Memorable Writings"
}

def safe_filename(text, max_len=60):
    return "".join(c for c in text if c.isalnum() or c in (' ', '-', '_')).strip()[:max_len]

def sanitize_yaml(v):
    if v is None: return ""
    return str(v).replace('\\', '\\\\').replace('\n', ' ').replace('\r', '').replace('"', "'").strip()

def parse_frontmatter(content):
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

def get_target_info(start_idx, count):
    with open('scratch_50_targets.json', 'r', encoding='utf-8') as f:
        targets = json.load(f)
    
    sub = targets[start_idx:start_idx+count]
    items = []
    for filename, filepath, log_no in sub:
        with open(filepath, 'r', encoding='utf-8') as f:
            raw = f.read()
        fm, body = parse_frontmatter(raw)
        cat_ko = fm.get("category", "")
        cat_en = CATEGORY_MAP.get(cat_ko, "General")
        items.append({
            "logNo": log_no,
            "filepath": filepath,
            "filename": filename,
            "date": fm.get("date", ""),
            "title": fm.get("title", ""),
            "description": fm.get("description", ""),
            "category_ko": cat_ko,
            "category_en": cat_en,
            "categoryNo": fm.get("categoryNo", "0"),
            "source": fm.get("source", ""),
            "thumbnail": fm.get("thumbnail", ""),
            "body": body
        })
    return items

def save_translated_post(item, title_en, desc_en, body_en):
    cat_dir_en = os.path.join(BASE_DIR, "en", safe_filename(item["category_en"]))
    os.makedirs(cat_dir_en, exist_ok=True)
    
    dest_file_name = f"{item['date']}_{item['logNo']}_{safe_filename(title_en)}.md"
    dest_file_path = os.path.join(cat_dir_en, dest_file_name)
    
    disclaimer = "*This content is written based on product specifications and personal experience. However, a small commission may be received for sales generated through the product links.*\n\n​\n\n"
    
    frontmatter_en = f"""---
title: "{sanitize_yaml(title_en)}"
date: {item['date']}
category: "{sanitize_yaml(item['category_en'])}"
categoryNo: {item['categoryNo']}
logNo: {item['logNo']}
source: "{item['source']}"
thumbnail: "{item['thumbnail']}"
description: "{sanitize_yaml(desc_en)}"
lang: "en"
---

{disclaimer}{body_en.strip()}"""

    with open(dest_file_path, "w", encoding="utf-8") as f:
        f.write(frontmatter_en)
    print(f"Saved: en/{safe_filename(item['category_en'])}/{dest_file_name}")

if __name__ == "__main__":
    items = get_target_info(0, 10)
    print(f"Loaded {len(items)} items for batch 1")
    for i, it in enumerate(items):
        print(f"[{i+1}] {it['date']} | {it['category_en']} | {it['title'][:30]}")
