# -*- coding: utf-8 -*-
import sys
import os
import re
import json
from pathlib import Path

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

posts_path = Path('src/content/posts')
en_posts_dir = posts_path / 'en'

# Collect all English posts with date and logNo
en_posts = []
for fp in en_posts_dir.rglob('*.md'):
    m = re.search(r'(\d{4}-\d{2}-\d{2})_(\d{10,13})_', fp.name)
    if m:
        date_str = m.group(1)
        log_no = m.group(2)
        en_posts.append({
            'file_path': str(fp),
            'filename': fp.name,
            'date': date_str,
            'logNo': log_no,
            'category_dir': fp.parent.name
        })

# Sort by date and logNo descending (most recent 150 posts)
en_posts.sort(key=lambda x: (x['date'], x['logNo']), reverse=True)
recent_150 = en_posts[:150]

print(f"Total English posts found: {len(en_posts)}")
print(f"Inspecting recent {len(recent_150)} English posts...")

ko_map = {}
for fp in posts_path.rglob('*.md'):
    if 'en' in fp.parts or 'Samples' in fp.parts or '.deleted' in fp.parts:
        continue
    m = re.search(r'_(\d{10,13})_', fp.name)
    if m:
        ko_map[m.group(1)] = str(fp)

def check_quality(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    lines = content.split('\n')
    words = re.findall(r'\b[a-zA-Z]{3,}\b', content)
    # Check if content body lines (excluding frontmatter and images) are too short
    text_lines = [l for l in lines if l.strip() and not l.strip().startswith('---') and not l.strip().startswith('!') and not l.strip().startswith('<') and not l.strip().startswith('title:') and not l.strip().startswith('description:')]
    
    is_weak = False
    reasons = []
    
    if len(text_lines) < 15:
        is_weak = True
        reasons.append(f"Short text lines ({len(text_lines)} lines)")
    if len(words) < 120:
        is_weak = True
        reasons.append(f"Low word count ({len(words)} words)")
        
    return is_weak, ", ".join(reasons), len(text_lines), len(words)

inspect_results = []
weak_count = 0

for item in recent_150:
    is_weak, reason, line_cnt, word_cnt = check_quality(item['file_path'])
    ko_path = ko_map.get(item['logNo'], '')
    
    # Generate expected URL
    cat_slug = safe_category_slug = item['category_dir'].lower().replace(' ', '-').replace('&', '')
    cat_slug = re.sub(r'-+', '-', cat_slug)
    filename_no_ext = os.path.splitext(item['filename'])[0]
    # URL structure: https://sanjangboarder.github.io/posts/en/{cat_slug}/{filename_slug}/
    url = f"https://sanjangboarder.github.io/posts/en/{cat_slug}/{filename_no_ext.lower()}/"
    
    entry = {
        'logNo': item['logNo'],
        'date': item['date'],
        'en_path': item['file_path'],
        'ko_path': ko_path,
        'filename': item['filename'],
        'is_weak': is_weak,
        'reason': reason,
        'line_cnt': line_cnt,
        'word_cnt': word_cnt,
        'url': url
    }
    inspect_results.append(entry)
    if is_weak:
        weak_count += 1

with open('inspect_recent_150_results.json', 'w', encoding='utf-8') as f:
    json.dump(inspect_results, f, ensure_ascii=False, indent=2)

print(f"Inspection Completed! Out of 150 recent posts:")
print(f" - Weak / Insufficient posts to rewrite: {weak_count}")
print(f" - Healthy posts: {150 - weak_count}")
