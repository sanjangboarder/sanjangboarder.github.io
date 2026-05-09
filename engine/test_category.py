import requests, json

BLOG_ID = "sanjangboarder"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Referer": "https://m.blog.naver.com/",
}

print("=" * 60)
print("STEP 1: post-list 아이템의 전체 필드 확인")
print("=" * 60)
url = f"https://m.blog.naver.com/api/blogs/{BLOG_ID}/post-list?page=1&pageSize=3&categoryNo=0&sortType=recentpost"
r = requests.get(url, headers=HEADERS, timeout=10)
data = r.json()
items = data.get("result", {}).get("items", [])
if items:
    print("첫 번째 아이템의 모든 필드:")
    print(json.dumps(items[0], ensure_ascii=False, indent=2))
else:
    print("아이템 없음")

print("\n" + "=" * 60)
print("STEP 2: 카테고리 목록 대안 API 시도")
print("=" * 60)
alt_urls = [
    f"https://m.blog.naver.com/api/blogs/{BLOG_ID}/menu-list",
    f"https://m.blog.naver.com/api/blogs/{BLOG_ID}/info",
    f"https://m.blog.naver.com/{BLOG_ID}?isHttpsRedirect=true",
]
for url in alt_urls:
    print(f"\n시도: {url}")
    r = requests.get(url, headers=HEADERS, timeout=10)
    print(f"  Status: {r.status_code}")
    if r.status_code == 200:
        try:
            d = r.json()
            print(json.dumps(d, ensure_ascii=False, indent=2)[:1500])
        except:
            print("  (HTML 응답)")
