import urllib.request
import urllib.parse
req = urllib.request.Request('https://www.books-yagi.co.jp/bb/books/search/search_criteria:yagi_parent_search/page:1/keyword:GOGH', headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req).read().decode('utf-8')
print("全" in html, html[:200])
