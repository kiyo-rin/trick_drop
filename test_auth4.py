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

url = "https://www.books-yagi.co.jp/bb/books/search/search_criteria:yagi_parent_search/categorycd:92330/page:1/isbn:9784323890210"
driver.get(url)
print("URL accessed:", url)
print("13525件?", "全13525件" in driver.page_source)
print("全1件?", "全1件" in driver.page_source)
driver.save_screenshot("test_yagi.png")

driver.quit()
