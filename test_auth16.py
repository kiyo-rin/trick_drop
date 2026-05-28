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
    "https://www.books-yagi.co.jp/bb/books/search/search_criteria:isbn/page:1/keyword:9784323890210",
    "https://www.books-yagi.co.jp/bb/books/search/search_criteria:isbn_search/page:1/keyword:9784323890210",
    "https://www.books-yagi.co.jp/bb/books/search/isbn:9784323890210",
    "https://www.books-yagi.co.jp/bb/books/search/keyword:9784323890210/optionselect:3"
]

for url in urls_to_test:
    driver.get(url)
    soup = bs4.BeautifulSoup(driver.page_source, "html.parser")
    amount = soup.find('div', class_='amount')
    print("URL:", url, "Amount:", amount.text.strip() if amount else "None")

driver.quit()
