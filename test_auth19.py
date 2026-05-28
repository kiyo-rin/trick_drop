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

url = "https://www.books-yagi.co.jp/bb/books/search/search_criteria:detail_search/isbn:9784323890210"
driver.get(url)
soup = bs4.BeautifulSoup(driver.page_source, "html.parser")
amount = soup.find('div', class_='amount')
print("Detail ISBN search 9784323890210:", amount.text.strip() if amount else "None")

driver.quit()
