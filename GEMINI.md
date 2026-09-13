# Antigravity Rules & Directives (github_blog)

This repository contains the GitHub Pages blog (`https://sanjangboarder.github.io`).
Whenever working on content updates, translations, bug fixes, or feature additions in this repository, strictly adhere to the following rules:

---

## 1. 🚨 Content Translation Directives (영문 포스트 집필 철칙)
1. **임의 요약 및 축약 절대 금지 (Full 1:1 Content Translation)**:
   - 영문 포스트를 작성할 때 "핵심 요약"이나 "축약본" 형태로 분량을 줄이는 행위를 **절대 금지**합니다.
   - 국문 원문의 모든 문단, 사진/캡션, 세부 에피소드, 상세 스펙/수치, 실전 사용 팁, 결론까지 빠짐없이 **1:1 풀 텍스트(Full-Text) 정성 직접 번역**으로 집필해야 합니다.
2. **기계적 편의주의 스크립트 금지**:
   - `re.sub` 단순 치환이나 단어 번역기로 때우지 않고, 문맥과 뉘앙스를 살린 고품질 영문 아티클로 완성합니다.

---

## 2. 🔍 SEO & Meta Description Rules (Bing / Google 웹마스터 도구 준수)
1. **모든 포스트 `description` 필수 작성**:
   - 신규 포스트 추가 또는 기존 포스트 업데이트 시 frontmatter에 반드시 `description:` 필드를 포함해야 합니다.
2. **적정 길이 및 품질 (150~160자 권장, 최소 50자 이상)**:
   - 검색엔진(Bing, Google) 검색 결과 스니펫에 가장 적합한 **150~160자 내외**로 작성합니다.
   - 사이트 기본 문구나 카테고리명만 단순 나열하는 중복 문구 작성을 절대 금지하며, 해당 글만의 핵심 내용(장소, 대상어종, 장비 스펙, 결론 등)을 담은 고유한 요약이어야 합니다.
3. **영문 포스트 디스크립션**:
   - 150~160자의 자연스러운 영문 문장으로 작성하며 한국어 문자가 포함되지 않아야 합니다.
4. **포맷 안전성**:
   - YAML 파싱 에러를 방지하기 위해 줄바꿈 없는 한 줄 문자열로 작성하고 큰따옴표 내의 따옴표는 적절히 이스케이프합니다.

---

## 3. ✅ Mandatory Verification & Deployment Flow
1. **포스트 무결성 검증**:
   - 포스트 수정 또는 추가 후 반드시 `python engine/validate_posts.py`를 실행하여 에러(Errors)와 경고(Warnings)가 0건인지 확인합니다.
2. **Git Commit & Push**:
   - 원격 저장소(`main` 브랜치)에 커밋 및 푸시하여 GitHub Actions 배포를 완료합니다.
3. **IndexNow 즉시 색인 제출**:
   - 새 글 배포 후 `python engine/submit_indexnow.py`를 실행하여 Bing 및 IndexNow 검색엔진에 즉각 갱신을 알립니다.
