"""
무조건 최근 10개 수집 (링크 보존 로직 포함)
"""
import os
import re
import time
import requests
from bs4 import BeautifulSoup
import markdownify

BLOG_ID   = "sanjangboarder"
BASE_DIR  = os.path.join(os.path.dirname(__file__), "..", "src", "content", "posts", "_test_links")
HEADERS   = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

def get_post_content(log_no):
    url = f"https://m.blog.naver.com/{BLOG_ID}/{log_no}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        content_div = (soup.select_one('div.se-main-container') or soup.select_one('div#postViewArea'))
        if not content_div: return None

        # OG 링크 처리 (가장 중요)
        for og in content_div.select('.se-oglink, .se-module-oglink'):
            a = og.find('a')
            if a and a.get('href'):
                new_p = soup.new_tag('p')
                new_p.string = f"\n\n[LINK_FOUND: {a.get('href')}]\n\n"
                og.replace_with(new_p)

        return markdownify.markdownify(str(content_div), heading_style="ATX")
    except: return None

if __name__ == "__main__":
    os.makedirs(BASE_DIR, exist_ok=True)
    resp = requests.get(f"https://m.blog.naver.com/api/blogs/{BLOG_ID}/post-list?pageSize=10", headers=HEADERS)
    items = resp.json().get("result", {}).get("items", [])
    
    for i, item in enumerate(items, 1):
        log_no = item.get("logNo")
        print(f"  [{i}/10] {log_no} 수집 중...")
        c = get_post_content(log_no)
        if c:
            with open(os.path.join(BASE_DIR, f"{log_no}.md"), "w", encoding="utf-8") as f:
                f.write(c)
        time.sleep(0.5)
