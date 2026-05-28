import urllib.request
import urllib.parse
def check(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        html = urllib.request.urlopen(req).read().decode('utf-8')
        print(url.split('/')[-1])
        if html.find('全13525件') != -1 or html.find('全1352') != -1:
            print("Found ALL items")
        elif html.find('全') != -1:
            # find how many items
            import re
            m = re.search(r'全(\d+)件', html)
            if m: print(f"Found {m.group(1)} items")
            else: print("Results found but count regex failed.")
        else:
            print("No items text found.")
    except Exception as e:
        print(url, "Error", e)

base = 'https://www.books-yagi.co.jp/bb/books/search/search_criteria:yagi_parent_search'
check(f"{base}/page:1/keyword:{urllib.parse.quote('ベーコン')}")
