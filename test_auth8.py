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

# First go to the URL directly
url = "https://www.books-yagi.co.jp/bb/books/search/search_criteria:yagi_parent_search/optionselect:3/keyword:9784389410438"
driver.get(url)
print("Initial GET URL:", driver.current_url)
print("Initial 1件?", "全1件" in driver.page_source)

# Now find the search button and click it
driver.find_element("id", "headsearch-button").click()
time.sleep(2)
print("After click URL:", driver.current_url)
print("After click 1件?", "全1件" in driver.page_source)

driver.quit()
