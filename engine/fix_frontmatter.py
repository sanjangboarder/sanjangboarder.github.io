"""
Frontmatter 일괄 수정 스크립트
- src/content/posts/ 내 모든 .md 파일의 YAML frontmatter를 안전하게 재작성합니다.
- 큰따옴표, 콜론, 줄바꿈 등 YAML을 깨뜨리는 문자를 제거/치환합니다.
"""

import os
import re
from pathlib import Path

POSTS_DIR = os.path.join(os.path.dirname(__file__), "..", "src", "content", "posts")

def sanitize_yaml_value(value: str) -> str:
    """YAML 값을 안전하게 만들기"""
    if not isinstance(value, str):
        return str(value)
    # 줄바꿈 제거
    value = value.replace('\n', ' ').replace('\r', '')
    # 큰따옴표 → 작은따옴표
    value = value.replace('"', "'")
    # YAML 특수문자: 앞에 오는 콜론+공백 처리 (값 내부는 괜찮음)
    # 앞뒤 공백 제거
    value = value.strip()
    return value

def fix_frontmatter(filepath: str) -> bool:
    """파일의 frontmatter를 파싱 후 안전하게 재작성"""
    try:
        content = Path(filepath).read_text(encoding='utf-8')
    except Exception as e:
        print(f"  [읽기 실패] {filepath}: {e}")
        return False

    if not content.startswith('---'):
        return False  # frontmatter 없음, 스킵

    # frontmatter 분리
    parts = content.split('---', 2)
    if len(parts) < 3:
        return False

    raw_fm = parts[1]
    body = parts[2]

    # frontmatter를 라인 단위로 수동 파싱
    new_fm_lines = []
    for line in raw_fm.split('\n'):
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            new_fm_lines.append(line)
            continue

        # key: value 패턴 파싱
        match = re.match(r'^(\w[\w\s]*?):\s*(.*)', stripped)
        if match:
            key = match.group(1).strip()
            val = match.group(2).strip()

            # 양쪽 따옴표 제거 후 재구성
            if val.startswith('"') and val.endswith('"'):
                val = val[1:-1]
            elif val.startswith("'") and val.endswith("'"):
                val = val[1:-1]

            val = sanitize_yaml_value(val)

            # 숫자형 필드는 따옴표 없이
            if key in ('date', 'categoryNo', 'logNo'):
                new_fm_lines.append(f'{key}: {val}')
            else:
                new_fm_lines.append(f'{key}: "{val}"')
        else:
            # 파싱 못한 라인은 그대로
            new_fm_lines.append(line)

    new_content = '---\n' + '\n'.join(new_fm_lines) + '\n---' + body
    Path(filepath).write_text(new_content, encoding='utf-8')
    return True

if __name__ == "__main__":
    posts_path = Path(POSTS_DIR)
    if not posts_path.exists():
        print(f"경로를 찾을 수 없습니다: {POSTS_DIR}")
        exit(1)

    all_files = list(posts_path.rglob("*.md"))
    print(f"총 {len(all_files)}개 파일 수정 시작...")

    success, fail = 0, 0
    for i, fp in enumerate(all_files, 1):
        if fix_frontmatter(str(fp)):
            success += 1
        else:
            fail += 1
        if i % 100 == 0:
            print(f"  {i}/{len(all_files)} 처리 중...")

    print(f"\n완료! 성공: {success}개 / 스킵/실패: {fail}개")
