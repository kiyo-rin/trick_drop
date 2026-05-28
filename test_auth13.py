from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import bs4

opts = Options()
opts.add_argument('--headless')
driver = webdriver.Chrome(options=opts)
driver.get("https://www.books-yagi.co.jp/bb/")
driver.find_element("id", "loginID").send_keys(config.USER_ID)
driver.find_element("id", "loginPW").send_keys(config.PASSWORD)
driver.find_element("css selector", ".next").click()
time.sleep(2)

urls_to_test = [
    # 1. Normal keyword search without optionselect
    "https://www.books-yagi.co.jp/bb/books/search/search_criteria:keyword_search/page:1/keyword:9784323890210",
    
    # 2. Keyword search WITH GET param
    "https://www.books-yagi.co.jp/bb/books/search/search_criteria:keyword_search/page:1/keyword:9784323890210?data%5BBooks%5D%5Boptionselect%5D=3",
    
    # 3. yagi_parent_search WITH GET param
    "https://www.books-yagi.co.jp/bb/books/search/search_criteria:yagi_parent_search/page:1/keyword:9784323890210?data%5BBooks%5D%5Boptionselect%5D=3",
]

for i, url in enumerate(urls_to_test):
    print(f"\nTesting URL {i+1}:")
    driver.get(url)
    soup = bs4.BeautifulSoup(driver.page_source, "html.parser")
    amount = soup.find('div', class_='amount')
    if amount:
        print("Amount:", amount.text.strip())
    else:
        print("Amount not found")
        
    keyword_input = soup.find('input', id='headsearch-text')
    if keyword_input:
        print(f"Keyword input value: '{keyword_input.get('value', '')}'")

driver.quit()
