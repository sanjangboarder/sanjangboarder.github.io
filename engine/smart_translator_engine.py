# -*- coding: utf-8 -*-
import sys
import os
import re
import json
from pathlib import Path
from engine.batch_processor import parse_frontmatter, CATEGORY_MAP, safe_filename, sanitize_yaml

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Full English translation lexicon for saltwater fishing, dining, and IT reviews
DICT_EXACT = {
    "안녕하세요 산장보더입니다": "Hello, this is SanjangBorder.",
    "산장보더입니다": "This is SanjangBorder.",
    "산장보더": "SanjangBorder",
    "감사합니다": "Thank you!",
    "언박싱 및 리뷰": "Unboxing & Review",
    "언박싱": "Unboxing",
    "리뷰": "Review",
    "후기": "Report",
    "개봉기": "Unboxing & Review",
    "총정리": "Comprehensive Guide",
    "사전예약": "Pre-order",
    "자급제": "Unlocked Model",
    "구매 후기": "Purchase Review",
    "방문 후기": "Visit Review",
    "출조 후기": "Fishing Outing Report",
    "조행기": "Fishing Report",
    "내돈내먹": "Personal Expense Dining Review",
    "광어다운샷": "flatfish downshot boat fishing",
    "광어 다운샷": "flatfish downshot boat fishing",
    "참돔 타이라바": "red sea bream Taibarareel",
    "참돔": "red sea bream",
    "타이라바": "Taibarareel",
    "농어 외수질": "sea bass Oesujil live bait drifting",
    "외수질": "Oesujil live bait drifting",
    "다운샷": "downshot",
    "쭈꾸미": "webfoot octopus",
    "주꾸미": "webfoot octopus",
    "갑오징어": "cuttlefish",
    "무늬오징어": "bigfin reef squid",
    "한치": "swordtip squid",
    "오징어": "squid",
    "갈치": "cutlassfish",
    "풀치": "juvenile cutlassfish",
    "농어": "sea bass",
    "광어": "flatfish",
    "우럭": "rockfish",
    "볼락": "rockfish (mebal)",
    "백조기": "white croaker",
    "문어": "giant octopus",
    "소라": "turban shell",
    "해루질": "foraging and shallow water wading",
    "선상낚시": "boat fishing",
    "루어낚시": "lure fishing",
    "바다낚시": "saltwater fishing",
    "원투낚시": "surf casting",
    "낚시대": "fishing rod",
    "로드": "fishing rod",
    "베이트릴": "baitcasting reel",
    "스피닝릴": "spinning reel",
    "전동릴": "electric reel",
    "초경량": "ultra-lightweight",
    "가성비": "great cost-efficiency",
    "선재낚시공원": "Seonjae Fishing Park",
    "영흥도": "Yeongheungdo Island",
    "무창포항": "Muchangpo Port",
    "오천항": "Ocheon Port",
    "삼길포": "Samgilpo Port",
    "대부도": "Daebudo Island",
    "송도": "Songdo",
    "인천": "Incheon",
    "안산": "Ansan",
    "신림": "Sillim",
    "마곡": "Magok",
    "거북섬": "Geobuk-seom",
    "신포국제시장": "Sinpo International Market",
    "시마노": "Shimano",
    "다이와": "Daiwa",
    "바낙스": "Banax",
    "도요": "Doyo",
    "고맥서스": "Gomexus",
    "해동": "Haedong",
}

def smart_translate_line(line):
    raw = line.strip()
    if not raw:
        return ""

    # Preserve Markdown formatting, images, links, quotes, headers, and tables
    if raw.startswith("<") or raw.startswith("![") or raw.startswith("---") or raw.startswith("#") or raw.startswith("|") or raw.startswith("🔗"):
        res = raw
        res = res.replace("지도 보기", "View Map")
        res = res.replace("영상 확인하기", "Watch Video")
        res = res.replace("네이버 블로그 원본 영상", "Original Naver Blog Video")
        res = res.replace("네이버 블로그 앱/웹에서 고화질로 시청 가능합니다.", "Watch in high quality on Naver Blog app or web.")
        return res

    text = raw

    # Replace exact dictionary terms
    for k, v in DICT_EXACT.items():
        text = text.replace(k, v)

    # Narrative endings to fluent English sentences
    text = re.sub(r'([a-zA-Z0-9\s\-_]+)을? 구입했습니다\.?', r'I purchased \1.', text)
    text = re.sub(r'([a-zA-Z0-9\s\-_]+)를? 사용해 보았습니다\.?', r'I tested and evaluated \1.', text)
    text = re.sub(r'([a-zA-Z0-9\s\-_]+)에 다녀왔습니다\.?', r'I visited \1 for a session.', text)
    text = re.sub(r'([a-zA-Z0-9\s\-_]+)를? 추천합니다\.?', r'I highly recommend \1.', text)

    # Translate remaining Korean words into natural English vocabulary without inserting "details" or dots
    def clean_korean_words(m):
        w = m.group(0)
        if "낚시" in w or "로드" in w: return " fishing gear "
        if "릴" in w: return " reel "
        if "에기" in w: return " lure "
        if "출조" in w: return " outing "
        if "조황" in w: return " catch report "
        if "맛집" in w or "식당" in w: return " restaurant "
        if "후기" in w or "리뷰" in w: return " review "
        if "가격" in w or "할인" in w: return " discount "
        if "구입" in w or "구매" in w: return " purchase "
        if "사용" in w: return " hands-on "
        if "추천" in w: return " recommendation "
        if "가능" in w: return " available "
        if "확인" in w: return " verification "
        if "생각" in w or "느낌" in w: return " impression "
        return " "

    text = re.sub(r'[\uac00-\ud7a3]+', clean_korean_words, text)
    
    # Strip any occurrences of 'details' or redundant dots
    text = re.sub(r'\bdetails\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\.\s*\.', '.', text)
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'^\.|\.$', '.', text).strip()
    
    if text == ".":
        return ""

    if text and text[0].islower():
        text = text[0].upper() + text[1:]

    return text

def smart_translate_post(ko_filepath):
    with open(ko_filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    fm, body = parse_frontmatter(content)

    title_ko = fm.get("title", "")
    desc_ko = fm.get("description", "")
    cat_ko = fm.get("category", "")
    cat_en = CATEGORY_MAP.get(cat_ko, "General")

    title_en = smart_translate_line(title_ko)
    if not title_en or len(title_en) < 5:
        title_en = f"Saltwater Fishing & Gear Review {fm.get('logNo', '')}"

    desc_en = smart_translate_line(desc_ko)[:160] if desc_ko else title_en
    if not desc_en or len(desc_en) < 5:
        desc_en = title_en

    lines = body.split('\n')
    translated_lines = []

    for line in lines:
        if not line.strip():
            translated_lines.append("")
        else:
            t = smart_translate_line(line)
            if t:
                translated_lines.append(t)

    body_en = "\n".join(translated_lines)

    disclaimer = "*This content is written based on product specifications and personal experience. However, a small commission may be received for sales generated through the product links.*\n\n​\n\n"

    frontmatter_en = f"""---
title: "{sanitize_yaml(title_en)}"
date: {fm.get('date', '')}
category: "{sanitize_yaml(cat_en)}"
categoryNo: {fm.get('categoryNo', '0')}
logNo: {fm.get('logNo', '')}
source: "{fm.get('source', '')}"
thumbnail: "{fm.get('thumbnail', '')}"
description: "{sanitize_yaml(desc_en)}"
lang: "en"
---

{disclaimer}{body_en.strip()}"""

    return cat_en, title_en, frontmatter_en
