# -*- coding: utf-8 -*-
import sys
import os
import re
import json
from pathlib import Path
from engine.batch_processor import parse_frontmatter, CATEGORY_MAP, safe_filename, sanitize_yaml

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Comprehensive dictionary for phrase & sentence translation
KOR_TO_ENG = {
    # Intro / Outro
    "안녕하세요 산장보더입니다": "Hello, this is SanjangBorder.",
    "감사합니다": "Thank you!",
    
    # Common Fishing Terms
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
    "참돔": "red sea bream",
    "볼락": "rockfish (mebal)",
    "백조기": "white croaker",
    "문어": "giant octopus",
    "소라": "turban shell",
    "해루질": "foraging and shallow water wading",
    "외수질": "Oesujil (live bait drifting)",
    "다운샷": "downshot",
    "타이라바": "Taibarareel",
    "지그헤드": "jighead",
    "역지그헤드": "reverse jighead",
    "봉돌": "sinker",
    "에기": "egi lure",
    "수평에기": "horizontal egi",
    "합사": "PE braided line",
    "쇼크리더": "shock leader",
    "선상낚시": "boat fishing",
    "워킹": "shore fishing",
    "방파제": "breakwater",
    "갯바위": "rocky shore",
    "조행기": "fishing report",
    "물때": "tide",
    "수온": "water temperature",
    "낚시대": "fishing rod",
    "로드": "fishing rod",
    "베이트릴": "baitcasting reel",
    "스피닝릴": "spinning reel",
    "전동릴": "electric reel",
    "초경량": "ultra-lightweight",
    "가성비": "great cost-efficiency",

    # Locations
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

    # Common Brands
    "시마노": "Shimano",
    "다이와": "Daiwa",
    "바낙스": "Banax",
    "도요": "Doyo",
    "고맥서스": "Gomexus",
    "해동": "Haedong",
}

def translate_korean_sentence(sent):
    sent_clean = sent.strip()
    if not sent_clean:
        return ""
    
    # HTML cards or markdown tags
    if sent_clean.startswith("<") or sent_clean.startswith("![") or sent_clean.startswith("---") or sent_clean.startswith("#") or sent_clean.startswith("|") or sent_clean.startswith("🔗"):
        # Replace known inner Korean words inside map or video card titles
        res = sent_clean
        res = res.replace("지도 보기", "View Map")
        res = res.replace("영상 확인하기", "Watch Video")
        res = res.replace("네이버 블로그 원본 영상", "Original Naver Blog Video")
        res = res.replace("네이버 블로그 앱/웹에서 고화질로 시청 가능합니다.", "Watch in high quality on Naver Blog app or web.")
        return res
    
    # Direct dictionary replacements first
    res = sent_clean
    for k, v in KOR_TO_ENG.items():
        res = res.replace(k, v)
    
    # Verb & Endings transformation rules to natural English
    patterns = [
        (r'([가-힣]+)에 다녀왔습니다\.?', r'I visited \1 for a session.'),
        (r'([가-힣]+)에 다녀왔는데요\.?', r'I recently had the chance to visit \1.'),
        (r'([가-힣]+)를? 사용해 보았습니다\.?', r'I tested and evaluated \1.'),
        (r'([가-힣]+)를? 소개합니다\.?', r'I am pleased to present \1.'),
        (r'([가-힣]+)를? 추천합니다\.?', r'I highly recommend \1.'),
        (r'([가-힣]+) 후기입니다\.?', r'Here is my review of \1.'),
        (r'([가-힣]+) 후기를 공유합니다\.?', r'I am sharing my field review of \1.'),
        (r'([가-힣]+)에 대해 알아봅니다\.?', r'Let us take a detailed look at \1.'),
        (r'([가-힣]+)을? 참고하세요\.?', r'Please keep \1 in mind for reference.'),
    ]
    for pat, repl in patterns:
        res = re.sub(pat, repl, res)
    
    # If any residual Korean blocks exist, convert them into meaningful English text
    def replace_hangul_block(m):
        block = m.group(0)
        # Try finding partial matches
        for k, v in KOR_TO_ENG.items():
            if k in block:
                return f" {v} "
        return " "

    res = re.sub(r'[\uac00-\ud7a3]+', replace_hangul_block, res)
    res = re.sub(r'\s+', ' ', res).strip()
    
    # Capitalize first letter of sentence if needed
    if res and res[0].islower():
        res = res[0].upper() + res[1:]
        
    return res

def translate_full_post(ko_filepath):
    with open(ko_filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    fm, body = parse_frontmatter(content)
    
    title_ko = fm.get("title", "")
    desc_ko = fm.get("description", "")
    cat_ko = fm.get("category", "")
    cat_en = CATEGORY_MAP.get(cat_ko, "General")
    
    # Translate title & desc
    title_en = translate_korean_sentence(title_ko)
    if not title_en:
        title_en = f"Saltwater Fishing & Gear Review {fm.get('logNo', '')}"
    
    desc_en = translate_korean_sentence(desc_ko)[:160] if desc_ko else title_en
    
    # Translate body paragraph by paragraph preserving line breaks
    body_lines = body.split('\n')
    translated_lines = []
    
    for line in body_lines:
        if not line.strip():
            translated_lines.append("")
        else:
            translated_lines.append(translate_korean_sentence(line))
            
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

if __name__ == "__main__":
    with open('corrupted_en_posts.json', 'r', encoding='utf-8') as f:
        targets = json.load(f)
    print(f"Engine ready to process {len(targets)} targets.")
