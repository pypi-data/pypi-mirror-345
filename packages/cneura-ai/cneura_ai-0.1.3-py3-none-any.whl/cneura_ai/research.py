import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
from html.parser import HTMLParser
from cneura_ai.logger import logger

class BodyTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        self.in_body = False
        self.ignored_tags = {"script", "style", "nav", "footer", "header", "aside", "form"}
        self.skip_content = False

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag == "body":
            self.in_body = True
        if tag in self.ignored_tags:
            self.skip_content = True

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == "body":
            self.in_body = False
        if tag in self.ignored_tags:
            self.skip_content = False

    def handle_data(self, data):
        if self.in_body and not self.skip_content:
            self.text.append(data)

    def get_text(self):
        return ' '.join(self.text)


class Research:
    def __init__(self, google_api_key, search_engine_id):
        self.google_api_key = google_api_key
        self.search_engine_id = search_engine_id
        self.driver = None

    def _init_selenium(self):
        """Initialize headless Selenium WebDriver with additional flags for better stability."""
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--ignore-certificate-errors")  
        options.add_argument("--enable-unsafe-swiftshader") 
        options.add_argument("--no-sandbox")  
        options.add_argument("--ignore-ssl-errors")
        options.add_argument("--disable-quic")
        options.add_argument("--ssl-version-min=tls1.2")
        options.add_argument("--ssl-version-max=tls1.3")
  
        
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")
        
        self.driver = webdriver.Chrome(options=options)
        
        self.driver.implicitly_wait(30) 
        
        self.driver.set_page_load_timeout(180) 

    def google_search(self, query, num_results=5):
        """Fetch search results using Google Programmable Search API."""
        url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={self.google_api_key}&cx={self.search_engine_id}&num={num_results}"
        try:
            response = requests.get(url, timeout=30)  
            response.raise_for_status()  
            data = response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching Google search results: {e}")
            return []

        search_results = []
        if "items" in data:
            for item in data["items"]:
                search_results.append((item["title"], item["link"]))

        return search_results

    def scrape_page(self, url):
        """Scrape the content of a page using Selenium."""
        try:
            self.driver.get(url)
            
            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )
           
            time.sleep(5)  

            page_content = self.driver.page_source
            return page_content

        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None
    def extract_body_text(self, html: str) -> str:
        """
        Extracts only the text content within the <body> tag from an HTML document without using BeautifulSoup.
        
        :param html: The HTML document as a string.
        :return: Extracted clean text content from the body.
        """
        parser = BodyTextExtractor()
        parser.feed(html)
        text = parser.get_text()
        
        cleaned_text = re.sub(r'\s+', ' ', text).strip()
        
        return cleaned_text
    def process_results(self, query):
        """Perform search and scrape results."""
        search_results = self.google_search(query)
        if not search_results:
            logger.info("No results found.")
            return
        
        for idx, (title, link) in enumerate(search_results):
            logger.info(f"Result {idx + 1}: {title}")
            logger.info(f"URL: {link}")
            
            page_content = self.scrape_page(link)
            page_content = self.extract_body_text(page_content)
            if page_content:
                logger.info(f"Content of {link}:")
                logger.info(page_content)  
                logger.info("token count : ", len(page_content.split()))
            logger.info("-" * 80)

    def close(self):
        """Close the Selenium WebDriver."""
        if self.driver:
            self.driver.quit()

