from auth_manager import AuthManager
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

opts = Options()
opts.add_argument('--headless')
driver = webdriver.Chrome(options=opts)
auth = AuthManager(driver)

driver.get("https://www.books-yagi.co.jp/bb/")
# Just do a manual POST request using requests for speed?
