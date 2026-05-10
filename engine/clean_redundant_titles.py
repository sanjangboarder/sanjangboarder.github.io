import os
import re
from pathlib import Path

BASE_DIR = 'src/content/posts'

def clean_file(filepath):
    try:
        content = filepath.read_text(encoding='utf-8')
        if not content.startswith('---'): return False
        
        parts = content.split('---', 2)
        if len(parts) < 3: return False
        
        fm = parts[1]
        body = parts[2]
        
        # 제목 추출
        title_match = re.search(r'title:\s*\"(.*?)\"', fm)
        if not title_match: return False
        title = title_match.group(1).strip()
        
        lines = body.split('\n')
        new_lines = []
        skipped = False
        text_count = 0
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                new_lines.append(line)
                continue
            
            text_count += 1
            # 본문 극초반(텍스트가 있는 첫 3줄 내)에서 중복 제목 감지
            if not skipped and text_count <= 3:
                # 불필요한 마크다운 기호 및 이모지 제거 후 비교
                clean_l = re.sub(r'[\*#🚗🚌🚢🎣💡🚀😱🐢💣🧪]', '', stripped).strip()
                # 이미지 태그 노이즈 제거 (캡처된 부분 대응: ![제목](...) 형태)
                clean_l = re.sub(r'\!\[.*?\]\(.*?\)', '', clean_l).strip()
                
                # 제목과 매우 유사하거나, 남은 텍스트가 거의 없으면 삭제
                if (title in clean_l) or (clean_l and clean_l in title) or (len(clean_l) < 3 and text_count == 1):
                    print(f"  [Cleaning] {filepath.name}: Removed '{stripped[:30]}...'")
                    skipped = True
                    continue
            
            new_lines.append(line)
        
        if skipped:
            filepath.write_text('---' + fm + '---' + '\n'.join(new_lines), encoding='utf-8')
            return True
    except Exception as e:
        print(f"  [Error] {filepath.name}: {e}")
    return False

if __name__ == "__main__":
    print(f"Starting cleanup in {BASE_DIR}...")
    count = 0
    for fp in Path(BASE_DIR).rglob('*.md'):
        if clean_file(fp):
            count += 1
    print(f"\nFinished! Cleaned {count} files.")
