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

url = "https://www.books-yagi.co.jp/bb/books/search/search_criteria:yagi_parent_search/categorycd:92330/page:1"
driver.get(url)

html = driver.page_source
m = re.search(r'全(\d+)件', html)
if m: print("Count without keyword:", m.group(1))

driver.quit()
