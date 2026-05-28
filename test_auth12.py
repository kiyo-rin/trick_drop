from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import re
opts = Options()
opts.add_argument('--headless')
driver = webdriver.Chrome(options=opts)
driver.get("https://www.books-yagi.co.jp/bb/")
driver.find_element("id", "loginID").send_keys(config.USER_ID)
driver.find_element("id", "loginPW").send_keys(config.PASSWORD)
driver.find_element("css selector", ".next").click()
time.sleep(2)
url = "https://www.books-yagi.co.jp/bb/books/search/search_criteria:yagi_parent_search/categorycd:92330/page:1/isbn:9784323890210"
driver.get(url)
import bs4
soup = bs4.BeautifulSoup(driver.page_source, "html.parser")
h = soup.find('div', id='page-summary')
if h: print("Summary:", h.text.strip().replace('\n', ' '))
else: print("No page-summary found. Trying other ways to find count.")
driver.save_screenshot("test_yagi_real.png")
driver.quit()
