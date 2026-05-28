import urllib.request
def check(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        html = urllib.request.urlopen(req).read().decode('utf-8')
        print(url.split('/')[-1], "-> Redirected to Login?", "<title>ログイン</title>" in html)
    except Exception as e:
        print(url, "Error", e)

base = 'https://www.books-yagi.co.jp/bb/books'
check(f"{base}/book_detail/1405429860")
check(f"{base}/book_detail/item_code:1405429860")
check(f"{base}/detail/1405429860")
