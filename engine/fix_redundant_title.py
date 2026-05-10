import os
import re
from pathlib import Path

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src", "content", "posts"))

def fix_content(content, title):
    lines = content.split('\n')
    # Frontmatter와 본문 분리
    try:
        idx = lines.index('---', 1)
        body_start = idx + 1
    except:
        return content

    # 본문 첫 10줄 내에서 제목과 유사한 강조 라인 찾기
    for i in range(body_start, min(body_start + 10, len(lines))):
        line = lines[i].strip()
        # **제목** 또는 # 제목 형태 확인
        if (line.startswith('**') and line.endswith('**')) or line.startswith('#'):
            clean_line = re.sub(r'[\*#]', '', line).strip()
            # 제목과 70% 이상 유사하면 제거 대상으로 판단
            # 간단하게 제목의 주요 키워드가 포함되어 있는지 확인
            title_keywords = set(re.findall(r'\w+', title))
            line_keywords = set(re.findall(r'\w+', clean_line))
            
            common = title_keywords.intersection(line_keywords)
            if len(common) >= len(title_keywords) * 0.5 or len(clean_line) < 5: 
                # 깨진 아이콘이나 너무 짧은 강조선도 함께 제거
                print(f"  [제거] 중복 의심 라인: {line[:30]}...")
                lines[i] = ""
                # 그 주변 빈 줄도 정리
                if i + 1 < len(lines) and lines[i+1].strip() == "":
                    lines[i+1] = ""
                break
                
    return '\n'.join(lines)

def main():
    print(f"중복 제목 제거 작업 시작...")
    count = 0
    for fp in Path(BASE_DIR).rglob("*.md"):
        if ".deleted" in str(fp): continue
        
        try:
            content = fp.read_text(encoding='utf-8')
            # 제목 추출
            title_match = re.search(r'title:\s*"(.*?)"', content)
            if not title_match: continue
            title = title_match.group(1)
            
            new_content = fix_content(content, title)
            
            if content != new_content:
                fp.write_text(new_content, encoding='utf-8')
                count += 1
        except Exception as e:
            print(f"  [에러] {fp.name}: {e}")

    print(f"\n작업 완료! {count}개 포스트의 중복 제목을 정리했습니다.")

if __name__ == "__main__":
    main()
