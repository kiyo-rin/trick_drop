from auth_manager import YagiAuth
import urllib.parse
session = YagiAuth().get_session()
base = 'https://www.books-yagi.co.jp/bb/books/search/search_criteria:yagi_parent_search'

def check(url):
    print(url)
    res = session.get(url)
    html = res.text
    if '全13525件' in html or '全135' in html: print("Found all items")
    elif '全' in html:
        import re
        m = re.search(r'全(\d+)件', html)
        if m: print(f"Found {m.group(1)} items")
        else: print("Results but no count regex")
    elif '一致する商品はありません' in html:
        print("0 items")
    else:
        print("Unknown")

check(f"{base}/optionselect:3/page:1/keyword:9784389410438")
check(f"{base}/page:1/keyword:9784389410438?optionselect=3")
check(f"{base}/page:1/keyword:%E3%83%99%E3%83%BC%E3%82%B3%E3%83%B3")
