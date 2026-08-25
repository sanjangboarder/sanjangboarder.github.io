import sys
import os
import json
import urllib.request
import urllib.parse
from pathlib import Path

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

HOST = "sanjangboarder.github.io"
KEY = "b0d7426bd0eb4753914b62c418457275"
KEY_LOCATION = f"https://{HOST}/{KEY}.txt"
INDEXNOW_ENDPOINT = "https://api.indexnow.org/indexnow"
BING_ENDPOINT = "https://www.bing.com/indexnow"

def get_all_urls():
    urls = [f"https://{HOST}/"]
    posts_dir = Path(__file__).parent.parent / "src" / "content" / "posts"
    
    for md_file in posts_dir.rglob("*.md"):
        rel_parts = md_file.relative_to(posts_dir).parts
        slug_parts = []
        for part in rel_parts:
            if part.endswith('.md'):
                part = part[:-3]
            part_slug = part.lower().replace(' ', '-').replace('_', '-')
            slug_parts.append(part_slug)
            
        url = f"https://{HOST}/posts/" + "/".join(slug_parts) + "/"
        urls.append(url)
        
    return urls

def submit_single_url(target_url):
    """Option 3-1: Send one URL via HTTP GET request"""
    params = urllib.parse.urlencode({
        "url": target_url,
        "key": KEY,
        "keyLocation": KEY_LOCATION
    })
    req_url = f"{BING_ENDPOINT}?{params}"
    print(f"🔗 [GET 단일 제출] {target_url}")
    try:
        req = urllib.request.Request(req_url)
        with urllib.request.urlopen(req) as response:
            print(f"  ✅ 성공! HTTP 상태 코드: {response.getcode()}")
    except urllib.error.HTTPError as e:
        print(f"  ⚠️ HTTP Error {e.code}: {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"  ⚠️ Error: {e}")

def submit_bulk_urls(urls):
    """Option 3-2: Submit bulk URLs via HTTP POST request"""
    print(f"🔑 Bing API Key: {KEY}")
    print(f"📍 Key Location: {KEY_LOCATION}")
    print(f"🚀 IndexNow API에 총 {len(urls)}개 Bulk URL 제출을 시작합니다...\n")
    
    chunk_size = 1000
    endpoints = [INDEXNOW_ENDPOINT, BING_ENDPOINT]
    
    for endpoint in endpoints:
        print(f"👉 Endpoint: {endpoint}")
        for i in range(0, len(urls), chunk_size):
            chunk = urls[i:i + chunk_size]
            payload = {
                "host": HOST,
                "key": KEY,
                "keyLocation": KEY_LOCATION,
                "urlList": chunk
            }
            
            json_data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                endpoint,
                data=json_data,
                headers={'Content-Type': 'application/json; charset=utf-8'}
            )
            
            try:
                with urllib.request.urlopen(req) as response:
                    status = response.getcode()
                    print(f"  ✅ [Chunk {i//chunk_size + 1}] 제출 성공! HTTP 상태 코드: {status}")
            except urllib.error.HTTPError as e:
                err_msg = e.read().decode('utf-8')
                print(f"  ⚠️ [Chunk {i//chunk_size + 1}] HTTP Error {e.code}: {err_msg}")
            except Exception as e:
                print(f"  ⚠️ [Chunk {i//chunk_size + 1}] 오류 발생: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # If single URL passed via CLI
        single_target = sys.argv[1]
        submit_single_url(single_target)
    else:
        # Default: Bulk submit all URLs
        url_list = get_all_urls()
        submit_bulk_urls(url_list)
