import os
import re
import requests
from bs4 import BeautifulSoup
import markdownify

BLOG_ID = "sanjangboarder"
LOG_NO  = "224274812197"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

def test():
    url = f"https://m.blog.naver.com/{BLOG_ID}/{LOG_NO}"
    resp = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(resp.text, 'html.parser')
    content_div = (soup.select_one('div.se-main-container') or soup.select_one('div#postViewArea'))
    
    # OG Link 처리
    for og in content_div.select('.se-oglink, .se-module-oglink'):
        a = og.find('a')
        if a and a.get('href'):
            new_p = soup.new_tag('p')
            new_p.string = f"\n\n[OG_LINK: {a['href']}]\n\n"
            og.replace_with(new_tag if 'new_tag' in locals() else new_p)

    md = markdownify.markdownify(str(content_div), heading_style="ATX")
    with open("link_test_final.md", "w", encoding="utf-8") as f:
        f.write(md)
    
    if "naver.me/IGsGLAPT" in md:
        print("SUCCESS: Link preserved!")
    else:
        print("FAILED: Link lost.")

if __name__ == "__main__":
    test()
