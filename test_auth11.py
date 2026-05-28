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

url = "https://www.books-yagi.co.jp/bb/books/search/search_criteria:keyword_search/page:1/keyword:9784389410438?data[Books][optionselect]=3"
driver.get(url)

html = driver.page_source
m = re.search(r'全(\d+)件', html)
if m: print("Count with GET data array:", m.group(1))
print("1件?", "全1件" in html)

url2 = "https://www.books-yagi.co.jp/bb/books/search/search_criteria:keyword_search/page:1/keyword:9784389410438?optionselect=3"
driver.get(url2)
html = driver.page_source
print("1件 (param2)?", "全1件" in html)

driver.quit()
