import requests
from bs4 import BeautifulSoup

def test_naver_mobile():
    url = "https://m.blog.naver.com/PostList.naver?blogId=sanjangboarder"
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # 글 제목이나 링크가 있는지 확인
            titles = soup.select('.name__3796X') # 모바일 제목 클래스 예시
            print(f"수집된 제목 개수: {len(titles)}")
            for t in titles[:5]:
                print(f"- {t.get_text()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_naver_mobile()
