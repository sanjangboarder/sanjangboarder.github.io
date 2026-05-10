import requests
BLOG_ID = "sanjangboarder"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://m.blog.naver.com/",
}
url = f"https://m.blog.naver.com/api/blogs/{BLOG_ID}/post-list?page=1&pageSize=3&categoryNo=0&sortType=recentpost"
resp = requests.get(url, headers=HEADERS)
print(f"Status: {resp.status_code}")
print(resp.text[:500])
