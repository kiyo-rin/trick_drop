import requests
from test_post2 import get_cookies

cookies = get_cookies()
params = {
    "_method": "POST",
    "data[Books][keyword]": "9784389410438",
    "data[Books][optionselect]": "3",
    "data[Books][search_connect]": "A",
    "data[Books][search_criteria]": "keyword_search"
}

r = requests.post("https://www.books-yagi.co.jp/bb/books/search", data=params, cookies=cookies)
html = r.text
print("Result text length:", len(html))
print("全1件" in html, html[:200])

import re
m = re.search(r'全(\d+)件', html)
if m: print("Found count:", m.group(1))

