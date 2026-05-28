import urllib.request
def check(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        html = urllib.request.urlopen(req).read().decode('utf-8')
        print(url.split('/')[-1], "-> Found 1件?", html.find('全1件') != -1)
    except Exception as e:
        print(url, "Error", e)

base = 'https://www.books-yagi.co.jp/bb/books/search/search_criteria:yagi_parent_search'
check(f"{base}/categorycd:92330/page:1/keyword:9784389410438")
