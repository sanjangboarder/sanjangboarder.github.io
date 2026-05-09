import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import markdownify

class NaverBlogMigrator:
    def __init__(self, blog_id):
        self.blog_id = blog_id
        self.base_url = f"https://blog.naver.com/{blog_id}"
        self.setup_driver()

    def setup_driver(self):
        chrome_options = Options()
        # 네이버의 봇 탐지를 피하기 위한 설정들
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        # chrome_options.add_argument("--headless") # 필요 시 헤드리스 모드 활성화
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        # 웹드라이버 속성 제거로 봇 감지 우회
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    def get_post_list(self, page_num=1):
        """블로그 글 목록을 가져오는 로직 (추후 구현)"""
        print(f"Page {page_num} 글 목록 수집 중...")
        # 네이버 블로그는 iframe 구조이므로 전환이 필요함
        # self.driver.get(self.base_url)
        # self.driver.switch_to.frame("mainFrame")
        pass

    def extract_post_content(self, post_url):
        """특정 포스트의 제목과 본문을 추출하여 마크다운으로 변환"""
        self.driver.get(post_url)
        time.sleep(2) # 로딩 대기
        
        try:
            self.driver.switch_to.frame("mainFrame")
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # 네이버 스마트에디터 ONE 기준 선택자 (변동 가능)
            title = soup.select_one('.se-title-text').get_text() if soup.select_one('.se-title-text') else "No Title"
            content_div = soup.select_one('.se-main-container')
            
            if content_div:
                markdown_content = markdownify.markdownify(str(content_div), heading_style="ATX")
                return {
                    "title": title,
                    "content": markdown_content
                }
        except Exception as e:
            print(f"Error extracting {post_url}: {e}")
        return None

    def close(self):
        self.driver.quit()

if __name__ == "__main__":
    # 테스트 실행 (본인의 블로그 ID로 테스트 가능)
    # migrator = NaverBlogMigrator("your_blog_id")
    # print(migrator.extract_post_content("https://blog.naver.com/your_blog_id/post_number"))
    # migrator.close()
    pass
