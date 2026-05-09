"""
알리익스프레스/쿠팡 링크 보존 정밀 테스트 (경로 수정 버전)
"""
import os
import re
import time
import requests
from bs4 import BeautifulSoup
import markdownify

BLOG_ID = "sanjangboarder"
BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "src", "content", "posts", "_affiliate_test")
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Safari/537.36"}

def get_post_content(log_no):
    url = f"https://m.blog.naver.com/{BLOG_ID}/{log_no}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        content_div = (soup.select_one('div.se-main-container') or soup.select_one('div#postViewArea'))
        if not content_div: return None

        # OG 링크 처리
        for og in content_div.select('.se-oglink, .se-module-oglink'):
            a = og.find('a')
            if a and a.get('href'):
                href = a['href']
                new_p = soup.new_tag('p')
                new_p.string = f"\n\n[AFFILIATE_LINK: {href}]\n\n"
                og.replace_with(new_p)

        return markdownify.markdownify(str(content_div), heading_style="ATX")
    except: return None

if __name__ == "__main__":
    os.makedirs(BASE_DIR, exist_ok=True)
    resp = requests.get(f"https://m.blog.naver.com/api/blogs/{BLOG_ID}/post-list?pageSize=100", headers=HEADERS)
    items = resp.json().get("result", {}).get("items", [])
    
    # 카테고리 필터링
    targets = [i for i in items if any(k in i.get('categoryName', '') for k in ['알리', '낚시용품', '리뷰'])]
    
    for i, item in enumerate(targets[:10], 1):
        log_no = item.get("logNo")
        print(f"  [{i}/10] {log_no} 수집 중...")
        c = get_post_content(log_no)
        if c:
            with open(os.path.join(BASE_DIR, f"{log_no}.md"), "w", encoding="utf-8") as f:
                f.write(c)
        time.sleep(0.3)
