import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import re

def check_keyword(k):
    url = f"https://www.books-yagi.co.jp/bb/books/search/search_criteria:yagi_parent_search/keyword:{urllib.parse.quote(k)}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        html = urllib.request.urlopen(req).read().decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        results = soup.find(text=re.compile("全.*?件"))
        print(f"[{k}] -> {results.strip() if results else 'No match text found'}")
    except Exception as e:
        print(f"[{k}] -> Error: {e}")

check_keyword("へんしんポスト：組み立て式 へんしんカードゲーム デラックス版")
check_keyword("へんしんポスト")
check_keyword("自律神経を整える「長生き呼吸法」")
check_keyword("自律神経を整える 長生き呼吸法")
check_keyword("自律神経を整える")
check_keyword("長生き呼吸法")
check_keyword("ベーコン")
