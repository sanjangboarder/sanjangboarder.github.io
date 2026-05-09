import os
import re
import requests
from bs4 import BeautifulSoup
import markdownify

BLOG_ID = "sanjangboarder"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def test_links(log_no):
    url = f"https://m.blog.naver.com/{BLOG_ID}/{log_no}"
    resp = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(resp.text, 'html.parser')
    content_div = (soup.select_one('div.se-main-container') or soup.select_one('div#postViewArea'))
    
    # OG 링크 처리
    for og in content_div.select('.se-oglink, .se-module-oglink'):
        a = og.find('a')
        if a and a.get('href'):
            new_p = soup.new_tag('p')
            new_p.string = f"\n\n[AFFILIATE_LINK: {a['href']}]\n\n"
            og.replace_with(new_p)

    md = markdownify.markdownify(str(content_div), heading_style="ATX")
    
    # 정규표현식으로 링크 추출 (전체 출력)
    found = re.findall(r'https?://[^\s\)\>\]]+', md)
    
    print(f"--- LOG_NO: {log_no} ---")
    for l in found:
        if 'coupang.com' in l or 'aliexpress.com' in l or 'naver.me' in l:
            print(f"FOUND LINK: {l}")

if __name__ == "__main__":
    test_links("224266605150")
    test_links("223940541814")
