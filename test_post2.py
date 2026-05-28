import requests
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import sys
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

# we need to simulate the POST request to /bb/books/search
cookies = get_cookies()
params = {
    "_method": "POST",
    "data[Books][keyword]": "9784389410438",
    "data[Books][optionselect]": "3",
    "data[Books][search_connect]": "A",
    "data[Books][search_criteria]": "keyword_search"
}

r = requests.post("https://www.books-yagi.co.jp/bb/books/search", data=params, cookies=cookies)
print("POST STATUS:", r.status_code)
html = r.text
print("Found 1件?", "全1件" in html)

# Then check if a GET request with right params remembers the session data?
r2 = requests.get("https://www.books-yagi.co.jp/bb/books/search/search_criteria:yagi_parent_search/optionselect:3/keyword:9784389410438", cookies=cookies)
print("GET STATUS:", r2.status_code, "Found 1件?", "全1件" in r2.text)

