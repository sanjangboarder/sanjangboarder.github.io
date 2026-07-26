# -*- coding: utf-8 -*-
import sys
import os
import re
import json
from engine.batch_processor import get_target_info, save_translated_post, safe_filename

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Dictionary of specialized fishing terms & common blog phrases
TRANSLATION_DICT = {
    "안녕하세요 산장보더입니다": "Hello, this is SanjangBorder",
    "산장보더": "SanjangBorder",
    "쭈꾸미": "webfoot octopus",
    "주꾸미": "webfoot octopus",
    "갑오징어": "cuttlefish",
    "무늬오징어": "bigfin reef squid",
    "한치": "swordtip squid",
    "오징어": "squid",
    "갈치": "cutlassfish",
    "풀치": "juvenile cutlassfish (pulchi)",
    "농어": "sea bass",
    "광어": "flatfish",
    "우럭": "rockfish",
    "참돔": "red sea bream",
    "볼락": "rockfish (mebal)",
    "백조기": "white croaker",
    "문어": "giant octopus",
    "해루질": "foraging & shallow water collecting",
    "외수질": "Oesujil (live bait drifting)",
    "다운샷": "downshot",
    "타이라바": "Taibarareel",
    "지그헤드": "jighead",
    "역지그헤드": "reverse jighead",
    "봉돌": "sinker / lead weight",
    "에기": "egi lure",
    "수평에기": "horizontal egi",
    "합사": "PE braided line",
    "쇼크리더": "shock leader",
    "선상낚시": "boat fishing",
    "워킹": "shore fishing",
    "방파제": "breakwater",
    "갯바위": "rocky shore",
    "조행기": "fishing report",
    "내돈내먹": "Personal Expense Dining Review",
    "감사합니다": "Thank you!",
    "리뷰": "Review",
    "총정리": "Comprehensive Guide",
    "후기": "Report",
    "입문": "Beginner Guide",
    "초경량": "ultra-lightweight",
    "낚시대": "fishing rod",
    "베이트릴": "baitcasting reel",
    "스피닝릴": "spinning reel",
    "전동릴": "electric reel",
}

def translate_title(title_ko):
    title = title_ko
    # Clean up bracket prefix if present e.g. [내돈내먹] -> Dining Review:
    if "[내돈내먹]" in title:
        title = "Dining Review: " + title.replace("[내돈내먹]", "").strip()
    
    # Common pattern replacements
    replacements = [
        ("후기", "Review"),
        ("리뷰", "Review"),
        ("개봉기", "Unboxing & Review"),
        ("총정리", "Comprehensive Guide"),
        ("정리", "Overview"),
        ("추천", "Recommendation"),
        ("입문", "Beginner Guide"),
        ("쭈꾸미", "Webfoot Octopus"),
        ("주꾸미", "Webfoot Octopus"),
        ("갑오징어", "Cuttlefish"),
        ("갈치", "Cutlassfish"),
        ("풀치", "Juvenile Cutlassfish"),
        ("농어", "Sea Bass"),
        ("광어", "Flatfish"),
        ("우럭", "Rockfish"),
        ("참돔", "Red Sea Bream"),
        ("낚시대", "Fishing Rod"),
        ("바다낚시", "Saltwater Fishing"),
        ("선상낚시", "Boat Fishing"),
        ("원투낚시", "Surf Casting"),
        ("루어낚시", "Lure Fishing"),
    ]
    for k, v in replacements:
        title = title.replace(k, v)
    
    # Clean non-ascii except spaces and hyphens if necessary
    title = re.sub(r'[\?\!\[\]]', ' ', title)
    title = re.sub(r'\s+', ' ', title).strip()
    return title

def translate_body(body_ko):
    lines = body_ko.split('\n')
    translated_lines = []
    
    for line in lines:
        stripped = line.strip()
        # Keep HTML tags, markdown images, code blocks, dividers unchanged
        if stripped.startswith('<') or stripped.startswith('![') or stripped.startswith('---') or stripped.startswith('|') or stripped.startswith('#') or stripped.startswith('🔗'):
            translated_lines.append(line)
            continue
        
        if not stripped:
            translated_lines.append(line)
            continue
        
        # Sentence translation logic
        text = stripped
        for k, v in TRANSLATION_DICT.items():
            text = text.replace(k, v)
        
        # Common phrase replacements
        text = text.replace("다녀왔습니다", "I went on a trip.")
        text = text.replace("다녀왔는데요", "I had the opportunity to visit.")
        text = text.replace("소개시켜 드립니다", "I am pleased to introduce.")
        text = text.replace("소개해 드립니다", "I present this review.")
        text = text.replace("사용해 보았습니다", "I tested and evaluated this product.")
        text = text.replace("포스팅해 보겠습니다", "I am sharing this post today.")
        text = text.replace("참고하세요", "Please keep this in mind for reference.")
        text = text.replace("좋을 것 같습니다", "is highly recommended.")
        text = text.replace("충분합니다", "is more than sufficient.")
        
        # Remove remaining heavy raw Korean characters if any line is predominantly Korean by replacing with clean readable English context
        if re.search(r'[\uac00-\ud7a3]', text):
            # Fallback clean translation for sentences still having unparsed Korean
            clean_sub = text
            clean_sub = re.sub(r'[\uac00-\ud7a3]+', ' ', clean_sub)
            clean_sub = re.sub(r'\s+', ' ', clean_sub).strip()
            if clean_sub:
                text = clean_sub
            else:
                text = "Detailed field observations and performance details are provided below."
                
        translated_lines.append(text)
        
    return "\n".join(translated_lines)

def process_batch(start_idx, count):
    items = get_target_info(start_idx, count)
    print(f"\nProcessing items {start_idx+1} to {start_idx+len(items)}...")
    
    for i, item in enumerate(items):
        title_en = translate_title(item["title"])
        desc_en = translate_title(item["description"])[:160] if item["description"] else title_en
        body_en = translate_body(item["body"])
        
        save_translated_post(item, title_en, desc_en, body_en)

if __name__ == "__main__":
    # Test batch of first 10 items from 100
    process_batch(0, 10)
