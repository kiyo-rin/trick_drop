from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
opts = Options()
opts.add_argument('--headless')
driver = webdriver.Chrome(options=opts)
driver.get("https://www.books-yagi.co.jp/bb/")
driver.find_element("id", "loginID").send_keys(config.USER_ID)
driver.find_element("id", "loginPW").send_keys(config.PASSWORD)
driver.find_element("css selector", ".next").click()
time.sleep(2)
driver.get("https://www.books-yagi.co.jp/bb/books/search/search_criteria:yagi_parent_search/categorycd:92330/isbn:9784389410438")
print("isbn:", "全1件" in driver.page_source)
driver.get("https://www.books-yagi.co.jp/bb/books/search/search_criteria:yagi_parent_search/categorycd:92330/page:1/isbn:9784389410438")
print("page:1/isbn:", "全1件" in driver.page_source)
driver.get("https://www.books-yagi.co.jp/bb/books/search_detail/isbn:9784389410438")
print("search_detail:", "全1件" in driver.page_source)
driver.get("https://www.books-yagi.co.jp/bb/books/search/search_criteria:detail_search/isbn:9784389410438")
print("detail_search:", "全1件" in driver.page_source)
driver.quit()
