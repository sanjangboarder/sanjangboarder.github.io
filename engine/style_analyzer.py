"""
문체 분석기 (Style Analyzer)
- 수집된 1,500+ 마크다운 파일에서 사용자의 글쓰기 패턴을 분석합니다.
- 통계적 분석 + Gemini API 심층 분석을 결합하여
  새 포스팅 생성 시 활용할 style_guide.json을 생성합니다.
"""

import os
import re
import json
import random
from collections import Counter
from pathlib import Path

# Gemini API
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

RAW_POSTS_DIR = os.path.join(os.path.dirname(__file__), "data", "raw_posts")
OUTPUT_DIR    = os.path.join(os.path.dirname(__file__), "data")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# ──────────────────────────────────────────
# 유틸: 마크다운 파일 로드
# ──────────────────────────────────────────
def load_all_posts(raw_dir):
    """모든 마크다운 파일을 읽어 리스트로 반환"""
    posts = []
    for md_file in Path(raw_dir).rglob("*.md"):
        try:
            text = md_file.read_text(encoding="utf-8")
            # Frontmatter 제거
            if text.startswith("---"):
                parts = text.split("---", 2)
                body = parts[2].strip() if len(parts) >= 3 else text
            else:
                body = text

            # 마크다운 기호 및 이미지 링크 제거 (순수 텍스트만 추출)
            body = re.sub(r'!\[.*?\]\(.*?\)', '', body)   # 이미지
            body = re.sub(r'\[.*?\]\(.*?\)', '', body)    # 링크
            body = re.sub(r'#+\s', '', body)               # 헤딩 기호
            body = re.sub(r'\*+', '', body)                # 볼드/이탤릭
            body = re.sub(r'`+.*?`+', '', body)           # 코드
            body = re.sub(r'\n{3,}', '\n\n', body)        # 과도한 빈 줄
            body = body.strip()

            # 너무 짧은 파일은 제외 (이미지만 있는 포스트 등)
            if len(body) > 200:
                category = md_file.parent.name
                posts.append({"category": category, "text": body, "file": str(md_file.name)})
        except Exception as e:
            pass

    return posts

# ──────────────────────────────────────────
# 통계 분석
# ──────────────────────────────────────────
def analyze_stats(posts):
    """문장/단락 단위의 통계적 패턴 분석"""
    all_sentences = []
    all_paragraphs = []
    opening_lines = []
    closing_lines = []

    for post in posts:
        text = post["text"]
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        sentences  = re.split(r'(?<=[다요죠네까군요])\s+', text)
        sentences  = [s.strip() for s in sentences if len(s.strip()) > 5]

        all_sentences.extend(sentences)
        all_paragraphs.extend(paragraphs)

        if paragraphs:
            opening_lines.append(paragraphs[0][:100])
            closing_lines.append(paragraphs[-1][:100])

    # 문장 길이 분포
    sent_lengths = [len(s) for s in all_sentences]
    avg_sent_len = sum(sent_lengths) / len(sent_lengths) if sent_lengths else 0

    # 단락 길이 분포
    para_lengths = [len(p) for p in all_paragraphs]
    avg_para_len = sum(para_lengths) / len(para_lengths) if para_lengths else 0

    # 자주 쓰는 어미/종결 표현
    endings = re.findall(r'(?:습니다|입니다|합니다|됩니다|있습니다|같습니다|것 같습니다|것 같네요|겠습니다|네요|군요|죠|요\.)', ' '.join(all_sentences))
    ending_counter = Counter(endings).most_common(15)

    # 자주 쓰는 첫 문장 패턴
    opening_patterns = Counter([line[:20] for line in opening_lines if line]).most_common(10)

    return {
        "total_posts": len(posts),
        "total_sentences": len(all_sentences),
        "avg_sentence_length_chars": round(avg_sent_len, 1),
        "avg_paragraph_length_chars": round(avg_para_len, 1),
        "common_endings": ending_counter,
        "common_opening_patterns": opening_patterns,
        "sample_openings": random.sample(opening_lines, min(10, len(opening_lines))),
        "sample_closings": random.sample(closing_lines, min(10, len(closing_lines))),
    }

# ──────────────────────────────────────────
# Gemini AI 심층 분석
# ──────────────────────────────────────────
def analyze_with_gemini(posts, stats):
    """카테고리별 샘플 텍스트를 Gemini에게 분석시켜 문체 가이드를 생성"""
    if not GEMINI_API_KEY:
        print("⚠️  GEMINI_API_KEY가 설정되지 않았습니다. .env 파일에 추가해 주세요.")
        return None

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash")

    # 카테고리별로 샘플 선정 (각 카테고리에서 2~3개)
    by_category = {}
    for post in posts:
        cat = post["category"]
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(post)

    sample_texts = []
    for cat, cat_posts in by_category.items():
        samples = random.sample(cat_posts, min(2, len(cat_posts)))
        for s in samples:
            sample_texts.append(f"[카테고리: {cat}]\n{s['text'][:800]}")

    combined_sample = "\n\n---\n\n".join(sample_texts[:30])  # 최대 30개 샘플

    prompt = f"""다음은 한 블로거가 작성한 블로그 포스트 샘플들입니다. 
총 {stats['total_posts']}개의 글을 분석한 통계도 함께 참고해 주세요.

[통계 정보]
- 평균 문장 길이: {stats['avg_sentence_length_chars']}자
- 평균 단락 길이: {stats['avg_paragraph_length_chars']}자
- 자주 쓰는 어미: {dict(stats['common_endings'][:8])}

[블로그 포스트 샘플]
{combined_sample}

위 내용을 바탕으로 이 블로거의 글쓰기 스타일을 아래 항목으로 상세히 분석해 주세요.
새로운 글을 작성할 때 AI가 이 스타일을 완벽하게 모방할 수 있도록 
구체적이고 실용적인 가이드를 JSON 형식으로 작성해 주세요.

반드시 아래 JSON 형식으로만 답변해 주세요:
{{
  "tone": "전반적인 어조 설명 (예: 친근하고 솔직한 경험 공유형)",
  "formality": "문체 격식 수준 (예: 반말과 존댓말 혼용, 주로 해요체)",
  "sentence_style": "문장 스타일 특징",
  "paragraph_style": "단락 구성 특징",
  "opening_pattern": "글 도입부 패턴",
  "closing_pattern": "글 마무리 패턴",
  "characteristic_expressions": ["자주 쓰는 특징적 표현 1", "표현 2", "표현 3", "표현 4", "표현 5"],
  "emoji_usage": "이모지/특수문자 사용 패턴",
  "content_structure": "주로 사용하는 글 구성 방식",
  "do_list": ["반드시 포함해야 할 요소 1", "요소 2", "요소 3"],
  "dont_list": ["피해야 할 요소 1", "요소 2"],
  "sample_intro_template": "이 블로거 스타일의 도입부 예시 문장",
  "sample_closing_template": "이 블로거 스타일의 마무리 예시 문장"
}}"""

    print("\n[Gemini API 분석 중...] 잠시 기다려 주세요...")
    try:
        response = model.generate_content(prompt)
        raw = response.text.strip()
        # JSON 블록 추출
        json_match = re.search(r'\{.*\}', raw, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        else:
            print("  JSON 파싱 실패. 원문 저장.")
            return {"raw_analysis": raw}
    except Exception as e:
        print(f"  Gemini 오류: {e}")
        return None

# ──────────────────────────────────────────
# 실행
# ──────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("문체 분석기 시작")
    print("=" * 60)

    # Step 1: 파일 로드
    print("\n[1/3] 마크다운 파일 로드 중...")
    posts = load_all_posts(RAW_POSTS_DIR)
    print(f"  ✅ {len(posts)}개 포스트 로드 완료")

    # Step 2: 통계 분석
    print("\n[2/3] 통계 분석 중...")
    stats = analyze_stats(posts)
    print(f"  ✅ 완료")
    print(f"  - 평균 문장 길이: {stats['avg_sentence_length_chars']}자")
    print(f"  - 평균 단락 길이: {stats['avg_paragraph_length_chars']}자")
    print(f"  - 자주 쓰는 어미 Top 5: {stats['common_endings'][:5]}")

    # Step 3: Gemini 분석
    print("\n[3/3] Gemini AI 문체 분석 중...")
    ai_guide = analyze_with_gemini(posts, stats)

    # 결과 저장
    style_guide = {
        "blog_id": "sanjangboarder",
        "stats": {
            "total_posts": stats["total_posts"],
            "avg_sentence_length": stats["avg_sentence_length_chars"],
            "avg_paragraph_length": stats["avg_paragraph_length_chars"],
            "common_endings": stats["common_endings"][:10],
        },
        "ai_style_guide": ai_guide,
        "sample_openings": stats["sample_openings"],
        "sample_closings": stats["sample_closings"],
    }

    output_path = os.path.join(OUTPUT_DIR, "style_guide.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(style_guide, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 문체 분석 완료!")
    print(f"  저장 위치: {output_path}")

    if ai_guide and "tone" in ai_guide:
        print(f"\n[AI 분석 요약]")
        print(f"  어조: {ai_guide.get('tone', '')}")
        print(f"  문체: {ai_guide.get('formality', '')}")
        print(f"  특징 표현: {ai_guide.get('characteristic_expressions', [])}")
