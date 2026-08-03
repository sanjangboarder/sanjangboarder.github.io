# -*- coding: utf-8 -*-
import sys
import os
import re
import json
from pathlib import Path
from engine.proper_translator_engine import translate_post_properly
from engine.batch_processor import safe_filename, BASE_DIR

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

print("==================================================")
print("Properly rebuilding all corrupted English posts with full fluent prose...")
print("==================================================")

with open('targets_to_fix.json', 'r', encoding='utf-8') as f:
    targets = json.load(f)

count_rebuilt = 0

for i, item in enumerate(targets):
    en_path = item['en_path']
    ko_path = item['ko_path']
    log_no = item['logNo']
    
    if not os.path.exists(ko_path):
        continue
        
    try:
        cat_en, title_en, full_content = translate_post_properly(ko_path)
        
        # Remove old file if it exists
        if os.path.exists(en_path):
            os.remove(en_path)
            
        m_date = re.search(r'(\d{4}-\d{2}-\d{2})', os.path.basename(en_path))
        date = m_date.group(1) if m_date else '2025-01-01'
        
        cat_dir_en = os.path.join(BASE_DIR, "en", safe_filename(cat_en))
        os.makedirs(cat_dir_en, exist_ok=True)
        
        dest_filename = f"{date}_{log_no}_{safe_filename(title_en)}.md"
        dest_filepath = os.path.join(cat_dir_en, dest_filename)
        
        with open(dest_filepath, 'w', encoding='utf-8') as f:
            f.write(full_content)
            
        count_rebuilt += 1
        if (i + 1) % 50 == 0 or (i + 1) == len(targets):
            print(f"Progress: [{i+1}/{len(targets)}] posts properly rebuilt.")
            
    except Exception as e:
        print(f"Error rebuilding {log_no}: {e}")

print("==================================================")
print(f"Successfully rebuilt {count_rebuilt} English posts into full, high-quality fluent blog posts!")
print("==================================================")
