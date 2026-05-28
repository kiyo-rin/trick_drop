from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def get_cookies():
    opts = Options()
    opts.add_argument('--headless')
    driver = webdriver.Chrome(options=opts)
    driver.get("https://www.books-yagi.co.jp/bb/")
    driver.find_element("id", "loginID").send_keys(config.USER_ID)
    driver.find_element("id", "loginPW").send_keys(config.PASSWORD)
    driver.find_element("css selector", ".next").click()
    time.sleep(2)
    cookies = driver.get_cookies()
    driver.quit()
    return {c['name']: c['value'] for c in cookies}

import requests
cookies = get_cookies()
base = 'https://www.books-yagi.co.jp/bb/books/search/search_criteria:yagi_parent_search'
urls = [
    f"{base}/optionselect:3/categorycd:92330/page:1/keyword:9784389410438",
    f"https://www.books-yagi.co.jp/bb/books/search/search_criteria:keyword_search/optionselect:3/page:1/keyword:9784389410438",
    f"https://www.books-yagi.co.jp/bb/books/search_detail/isbn:9784389410438",
    f"https://www.books-yagi.co.jp/bb/books/search/search_criteria:detail_search/isbn:9784389410438",
    f"https://www.books-yagi.co.jp/bb/books/search/search_criteria:detail_search/isbn:9784389410438/page:1"
]
for u in urls:
    r = requests.get(u, cookies=cookies)
    print(u)
    print("Found 1件:", "全1件" in r.text, "| All items:", "全1352" in r.text, "| Found title?", "<title>ログイン" not in r.text)

r = requests.get("https://www.books-yagi.co.jp/bb/books/search/search_criteria:yagi_parent_search/optionselect:3/categorycd:92330/page:1/keyword:9784389410438", cookies=cookies)
print(r.text[:500])
