import urllib.request
req = urllib.request.Request('https://www.books-yagi.co.jp/bb/books/search/search_criteria:yagi_parent_search/optionselect:3/page:1/keyword:9784389410438', headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req).read().decode('utf-8')
print("<title>" in html, html.find('全1件') != -1)
