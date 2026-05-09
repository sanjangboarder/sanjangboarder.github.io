"""
글쓰기 엔진 (Post Generator)
- style_guide.json을 기반으로 "산장보더" 문체로 글을 생성합니다.
- 1) 기존 포스트 재구성 2) 키워드 기반 신규 포스트 생성을 지원합니다.
"""

import os
import json
import random
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

STYLE_GUIDE_PATH = os.path.join(os.path.dirname(__file__), "data", "style_guide.json")
RAW_POSTS_DIR    = os.path.join(os.path.dirname(__file__), "data", "raw_posts")
OUTPUT_DIR       = os.path.join(os.path.dirname(__file__), "..", "src", "content", "posts") # Astro 실제 포스트 폴더
GEMINI_API_KEY   = os.getenv("GEMINI_API_KEY", "")

class PostGenerator:
    def __init__(self):
        with open(STYLE_GUIDE_PATH, "r", encoding="utf-8") as f:
            self.style_data = json.load(f)
        
        self.guide = self.style_data["ai_style_guide"]
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    def _get_system_prompt(self):
        """스타일 가이드를 기반으로 시스템 프롬프트 생성"""
        return f"""너는 '산장보더'라는 닉네임의 전문 블로거야. 
다음 가이드를 완벽하게 준수하여 글을 작성해줘.

[톤앤매너]
- {self.guide['tone']}
- {self.guide['formality']}

[문장 및 단락 스타일]
- {self.guide['sentence_style']}
- {self.guide['paragraph_style']}

[구조]
- 도입부: {self.guide['opening_pattern']}
- 마무리: {self.guide['closing_pattern']}
- 특징 표현: {', '.join(self.guide['characteristic_expressions'])}
- 이모지 사용: {self.guide['emoji_usage']}

[필수 사항]
- {', '.join(self.guide['do_list'])}

[주의 사항]
- {', '.join(self.guide['dont_list'])}
"""

    def generate_new_post(self, category, topic, reference_info=""):
        """새로운 키워드와 정보를 바탕으로 포스팅 생성"""
        prompt = f"""
카테고리: {category}
주제: {topic}
참고 정보: {reference_info}

위 주제에 대해 '산장보더' 블로그 포스팅을 작성해줘. 
내용은 아주 상세하고 유익해야 하며, 반드시 마크다운(Markdown) 형식으로 작성해줘.
포스팅 제목은 글 제일 처음에 '# 제목' 형태로 넣어줘.
"""
        
        print(f"\n[신규 포스트 생성 중...] 주제: {topic}")
        response = self.model.generate_content(
            [self._get_system_prompt(), prompt]
        )
        return response.text

    def reconstruct_post(self, post_path):
        """기존 글을 읽어와서 재구성"""
        with open(post_path, "r", encoding="utf-8") as f:
            old_content = f.read()

        prompt = f"""
다음은 과거에 작성된 블로그 포스트야. 
이 내용을 현재의 '산장보더' 문체로 더 세련되게 재구성해줘.
정보가 누락되지 않게 하고, 더 풍성한 설명이나 최신 의견을 덧붙여줘.

[기존 내용]
{old_content}
"""
        print(f"\n[기존 포스트 재구성 중...] {os.path.basename(post_path)}")
        response = self.model.generate_content(
            [self._get_system_prompt(), prompt]
        )
        return response.text

    def save_to_astro(self, content, category):
        """생성된 내용을 Astro 프로젝트의 content 폴더에 저장"""
        # 제목 추출
        lines = content.strip().split('\n')
        title = lines[0].replace('# ', '').strip() if lines[0].startswith('# ') else "Generated Post"
        
        # Frontmatter 생성
        today = datetime.now().strftime("%Y-%m-%d")
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()[:50]
        filename = f"{today}_{safe_title}.md"
        
        # Astro content 폴더 경로 설정 (없으면 생성)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        filepath = os.path.join(OUTPUT_DIR, filename)

        # 본문에서 # 제목 줄 제거 (이미 Frontmatter에 들어가므로)
        body = '\n'.join(lines[1:]).strip() if lines[0].startswith('# ') else content

        final_content = f"""---
title: "{title}"
date: {today}
category: "{category}"
description: "{title}에 대한 산장보더의 솔직한 리뷰와 정보 공유입니다."
---

{body}
"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(final_content)
        
        print(f"✅ Astro 포스트 저장 완료: {filepath}")
        return filepath

if __name__ == "__main__":
    generator = PostGenerator()
    
    # 테스트 1: 신규 포스트 생성
    # new_post = generator.generate_new_post("낚시용품", "2026년형 초경량 릴 추천", "가상의 A사 릴, 무게 130g, 드랙력 5kg")
    # generator.save_to_astro(new_post, "낚시용품")

    # 테스트 2: 기존 글 재구성 (무작위 하나 선택)
    # import glob
    # all_mds = glob.glob(os.path.join(RAW_POSTS_DIR, "**", "*.md"), recursive=True)
    # if all_mds:
    #     old_post = random.choice(all_mds)
    #     reconstructed = generator.reconstruct_post(old_post)
    #     generator.save_to_astro(reconstructed, "재구성")
    pass
