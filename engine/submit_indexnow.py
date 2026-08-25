import sys
import os
import json
import urllib.request
from pathlib import Path

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

HOST = "sanjangboarder.github.io"
KEY = "0b8065346f466a67ff399341b34f7667"
KEY_LOCATION = f"https://{HOST}/{KEY}.txt"
INDEXNOW_ENDPOINT = "https://api.indexnow.org/indexnow"

def get_all_urls():
    urls = [f"https://{HOST}/"]
    posts_dir = Path(__file__).parent.parent / "src" / "content" / "posts"
    
    for md_file in posts_dir.rglob("*.md"):
        rel_parts = md_file.relative_to(posts_dir).parts
        # Construct Astro slug path format
        # If english: /posts/en/category/filename-slug/
        # Astro slug replaces spaces and special characters with hyphens
        slug_parts = []
        for part in rel_parts:
            # strip .md extension on last part
            if part.endswith('.md'):
                part = part[:-3]
            # Replace spaces and underscores appropriately for Astro routing
            part_slug = part.lower().replace(' ', '-').replace('_', '-')
            slug_parts.append(part_slug)
            
        url = f"https://{HOST}/posts/" + "/".join(slug_parts) + "/"
        urls.append(url)
        
    return urls

def submit_indexnow(urls):
    print(f"🚀 IndexNow API에 총 {len(urls)}개 URL 제출을 시작합니다...")
    
    # IndexNow API limits up to 10,000 URLs per request
    chunk_size = 1000
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
            INDEXNOW_ENDPOINT,
            data=json_data,
            headers={'Content-Type': 'application/json; charset=utf-8'}
        )
        
        try:
            with urllib.request.urlopen(req) as response:
                status = response.getcode()
                print(f"✅ Chunk [{i//chunk_size + 1}] 제출 성공! HTTP 상태 코드: {status}")
        except urllib.error.HTTPError as e:
            print(f"❌ Chunk [{i//chunk_size + 1}] 제출 실패 (HTTP Error {e.code}): {e.read().decode('utf-8')}")
        except Exception as e:
            print(f"❌ 제출 중 오류 발생: {e}")

if __name__ == "__main__":
    url_list = get_all_urls()
    submit_indexnow(url_list)
