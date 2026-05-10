import os
import re
from pathlib import Path

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src", "content", "posts"))

def fix_image_layout(content):
    # 연속된 이미지 사이의 빈 줄 제거
    # ![](...)\n\n![](...) -> ![](...)\n![](...)
    # 여러 번 반복 실행하여 3개 이상의 이미지도 처리
    prev_content = ""
    while prev_content != content:
        prev_content = content
        content = re.sub(r'(\!\[.*?\]\(.*?\))\s*\n\s*(\!\[.*?\]\(.*?\))', r'\1\n\2', content)
    return content

def main():
    print(f"이미지 레이아웃 수정 시작: {BASE_DIR}")
    count = 0
    for fp in Path(BASE_DIR).rglob("*.md"):
        if ".deleted" in str(fp): continue
        
        try:
            content = fp.read_text(encoding='utf-8')
            new_content = fix_image_layout(content)
            
            if content != new_content:
                fp.write_text(new_content, encoding='utf-8')
                count += 1
                if count % 50 == 0:
                    print(f"  {count}개 파일 수정 중...")
        except Exception as e:
            print(f"  [에러] {fp.name}: {e}")

    print(f"\n작업 완료! 총 {count}개의 파일이 수정되었습니다.")

if __name__ == "__main__":
    main()
