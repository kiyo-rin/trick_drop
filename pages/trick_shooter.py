import streamlit as st
import sqlite3
import pandas as pd
import os
import datetime
import math
import urllib.request
import xml.etree.ElementTree as ET
import re

try:
    from sp_api.api import Products
    from sp_api.base import Marketplaces
    from exports.amazon_sp_api_config import SP_API_CONFIG
    SP_API_AVAILABLE = True
except ImportError:
    SP_API_AVAILABLE = False
    
st.set_page_config(page_title="TRICK SHOOTER", layout="wide")
st.title("TRICK SHOOTER 🎯 - マルチ同時出品ツール")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "listings.db")
EXPORT_DIR = os.path.join(BASE_DIR, "exports")

# exportsディレクトリが存在しない場合は作成する
os.makedirs(EXPORT_DIR, exist_ok=True)

# DB初期化
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku TEXT UNIQUE,
            asin_isbn TEXT,
            shelf_location TEXT,
            base_price INTEGER,
            condition TEXT,
            description TEXT,
            amazon_status TEXT,
            mercari_status TEXT,
            qoo10_status TEXT,
            furuhon_status TEXT,
            created_at TEXT
        )
    ''')
    
    # schema update (shelf_locationカラムが無ければ追加する)
    try:
        c.execute("ALTER TABLE listings ADD COLUMN shelf_location TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass # 既にカラムが存在する場合は無視
        
    conn.commit()
    conn.close()

# 初期化処理
init_db()
if not os.path.exists(EXPORT_DIR):
    os.makedirs(EXPORT_DIR)

# 国会図書館APIや紀伊國屋用に、10桁ASINを13桁ISBNに変換する
def asin_to_isbn13(asin):
    asin = re.sub(r'[^0-9X]', '', str(asin).upper())
    if len(asin) == 13: return asin
    if len(asin) == 10:
        core = '978' + asin[:-1]
        sum_val = sum(int(core[i]) * (1 if i % 2 == 0 else 3) for i in range(12))
        check = (10 - (sum_val % 10)) % 10
        return core + str(check)
    return asin

# SKUからASINを逆引き (モック: 実装待ち)
def get_asin_from_sku(sku):
    import time
    time.sleep(0.5) 
    return "4865138005"  # 医者からもらった薬がわかる本 (テスト用)

# 自社出品情報の取得 (モック: 実装待ち)
def get_my_inventory_info(sku):
    import time
    time.sleep(0.5)
    return {
        "price": 2800,
        "condition": "良い"
    }

# 国会図書館APIによる書籍情報取得
def fetch_book_info_ndl(isbn):
    isbn_clean = asin_to_isbn13(isbn)
    if not isbn_clean: return None
    url = f"https://ndlsearch.ndl.go.jp/api/opensearch?isbn={isbn_clean}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req, timeout=10)
        tree = ET.fromstring(res.read())
        
        item = tree.find('.//item')
        if item is None:
            return None
            
        def get_text(node, suffix):
            for child in node.iter():
                if child.tag.endswith(suffix):
                    return child.text
            return ""
            
        title = get_text(item, 'title')
        author = get_text(item, 'creator') or get_text(item, 'author')
        publisher = get_text(item, 'publisher')
        date = get_text(item, 'date') or get_text(item, 'pubDate')
        
        # 著者名の簡易クリーニング（"鈴木, 大拙, 1870-1966" など）
        if author:
            parts = author.split(',')
            if len(parts) >= 2 and not any(char.isdigit() for char in parts[0]+parts[1]):
                author = (parts[0] + parts[1]).replace(' ', '').replace('　', '')
            else:
                author = parts[0].replace(' ', '').replace('　', '')
        
        # あらすじを紀伊國屋書店から取得 (補完)
        desc = ""
        try:
            kino_url = f"https://www.kinokuniya.co.jp/f/dsg-01-{isbn_clean}"
            kino_req = urllib.request.Request(kino_url, headers={'User-Agent': 'Mozilla/5.0'})
            kino_html = urllib.request.urlopen(kino_req, timeout=5).read().decode('utf-8')
            m_desc = re.search(r'<h3>内容説明</h3>.*?<p.*?>\s*(.*?)\s*</p>', kino_html, re.S)
            if m_desc:
                desc = m_desc.group(1).replace('<br />', '\n').strip()
        except Exception:
            pass # 取得失敗時はデフォルトテキストへフォールバック
            
        if not desc:
            desc = "※あらすじは自動取得できませんでした（必要に応じて手動で追記、またはアダルトにチェックを入れて省略してください）"

        return {
            "title": title or "",
            "author": author or "",
            "publisher": publisher or "",
            "date": date or "",
            "desc": desc
        }
    except Exception as e:
        print(f"API Error: {e}")
        return None

def isbn13_to_asin(isbn13):
    isbn = re.sub(r'[^0-9X]', '', str(isbn13).upper())
    if len(isbn) == 10: return isbn
    if len(isbn) == 13 and isbn.startswith('978'):
        core = isbn[3:12]
        total = sum((10 - i) * int(c) for i, c in enumerate(core))
        check = (11 - (total % 11)) % 11
        return core + ('X' if check == 10 else str(check))
    return isbn

# Amazon SP-APIからコンディション別最安値と出品者数を取得
def fetch_amazon_prices(asin_or_isbn):
    if not SP_API_AVAILABLE:
        return {}
    prices = {}
    asin = isbn13_to_asin(asin_or_isbn)
    try:
        p = Products(credentials=SP_API_CONFIG, marketplace=Marketplaces.JP)
        
        # 中古の最安値
        res_used = p.get_item_offers(asin, item_condition="Used")
        used_offers = res_used.payload.get("Offers", [])
        for o in used_offers:
            sub = o.get("SubCondition", "")
            amt = o.get("ListingPrice", {}).get("Amount", 0) + o.get("Shipping", {}).get("Amount", 0)
            if amt > 0:
                if sub not in prices:
                    prices[sub] = {"price": int(amt), "count": 1}
                else:
                    prices[sub]["count"] += 1
                    if amt < prices[sub]["price"]:
                        prices[sub]["price"] = int(amt)
                    
        # 新品の最安値
        res_new = p.get_item_offers(asin, item_condition="New")
        new_offers = res_new.payload.get("Offers", [])
        for o in new_offers:
            amt = o.get("ListingPrice", {}).get("Amount", 0) + o.get("Shipping", {}).get("Amount", 0)
            if amt > 0:
                if "new" not in prices:
                    prices["new"] = {"price": int(amt), "count": 1}
                else:
                    prices["new"]["count"] += 1
                    if amt < prices["new"]["price"]:
                        prices["new"]["price"] = int(amt)
                    
    except Exception as e:
        print("SP-API Pricing Error:", e)
    return prices

import requests
KEEPA_API_KEY = "2qcjs5p89b8ipqiofp65858a7q2702cnv6opo733rfsdbah6rb11o8bj9p7d0dm9"

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_keepa_data(asin):
    # 日本(domain=5)を指定してKeepa APIを叩く
    url = f"https://api.keepa.com/product?key={KEEPA_API_KEY}&domain=5&asin={asin}&stats=180"
    try:
        res = requests.get(url, timeout=10)
        data = res.json()
        if "products" in data and len(data["products"]) > 0:
            return data["products"][0]
    except Exception as e:
        print("Keepa API Error:", e)
    return None

# 価格計算（切り捨て・利益防衛ロジック）
def calc_amazon_price(base_price):
    return int(base_price - 345)

def calc_mercari_price(base_price):
    return int(base_price * 1.1)

def calc_qoo10_price(base_price):
    return int((base_price + 200) * 1.15)

def calc_furuhon_price(base_price):
    return int(base_price * 1.0)

# DB保存
def save_to_db(sku, asin_isbn, shelf_location, base_price, condition, description, targets):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    amz_status = 'Pending' if targets.get('Amazon', False) else 'Skipped'
    mer_status = 'Pending' if targets.get('Mercari', False) else 'Skipped'
    q10_status = 'Pending' if targets.get('Qoo10', False) else 'Skipped'
    fur_status = 'Pending' if targets.get('Furuhon', False) else 'Skipped'

    try:
        c.execute('''
            INSERT INTO listings (
                sku, asin_isbn, shelf_location, base_price, condition, description,
                amazon_status, mercari_status, qoo10_status, furuhon_status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (sku, asin_isbn, shelf_location, base_price, condition, description, amz_status, mer_status, q10_status, fur_status, now))
        conn.commit()
        return True, "DB保存成功"
    except sqlite3.IntegrityError:
        return False, f"SKU '{sku}' は既に存在します。"
    finally:
        conn.close()

def export_amazon_tsv(sku, price, condition, date_str):
    filepath = os.path.join(EXPORT_DIR, f"amazon_{date_str}.tsv")
    amazon_price = calc_amazon_price(price)
    min_price = amazon_price
    max_price = amazon_price * 2
    df = pd.DataFrame([{
        "sku": sku,
        "price": amazon_price,
        "minimum-seller-allowed-price": min_price,
        "maximum-seller-allowed-price": max_price,
        "item-condition": condition,
        "quantity": 1
    }])
    file_exists = os.path.isfile(filepath)
    df.to_csv(filepath, sep='\t', index=False, encoding="utf-8-sig", mode='a', header=not file_exists)
    return filepath, amazon_price, min_price, max_price

def export_mercari_csv(sku, asin_isbn, base_price, condition, description, date_str):
    filepath = os.path.join(EXPORT_DIR, f"mercari_shops_{date_str}.csv")
    mercari_price = calc_mercari_price(base_price)
    df = pd.DataFrame([{
        "SKU": sku,
        "Identifier": asin_isbn,
        "Price": mercari_price,
        "Condition": condition,
        "Description": description
    }])
    file_exists = os.path.isfile(filepath)
    df.to_csv(filepath, index=False, encoding="utf-8-sig", mode='a', header=not file_exists)
    return filepath

def export_qoo10_csv(sku, asin_isbn, base_price, condition, description, date_str):
    filepath = os.path.join(EXPORT_DIR, f"qoo10_{date_str}.csv")
    qoo10_price = calc_qoo10_price(base_price)
    df = pd.DataFrame([{
        "SellerItemCode": sku,
        "StandardCode": asin_isbn,
        "SellPrice": qoo10_price,
        "Condition": condition,
        "ItemDescription": description
    }])
    file_exists = os.path.isfile(filepath)
    df.to_csv(filepath, index=False, encoding="utf-8-sig", mode='a', header=not file_exists)
    return filepath

def export_furuhon_tsv(sku, asin_isbn, base_price, condition, description, date_str):
    filepath = os.path.join(EXPORT_DIR, f"koshoten_{date_str}.csv")
    furuhon_price = calc_furuhon_price(base_price)
    df = pd.DataFrame([{
        "SKU": sku,
        "ISBN": asin_isbn,
        "Price": furuhon_price,
        "Condition": condition,
        "Memo": description
    }])
    file_exists = os.path.isfile(filepath)
    df.to_csv(filepath, index=False, encoding="utf-8-sig", mode='a', header=not file_exists)
    return filepath

st.markdown("""
### 概要
1回のデータ入力で、4つのプラットフォーム（Amazon、メルカリShops、Qoo10、日本の古本屋）向けに出品用データを同時生成・API送信する統合ツールです。
将来的にはここから在庫連携を行うマスターデータとなります。
""")

st.subheader("商品情報入力")

# 書籍情報のセッションステートを初期化（API取得用）
for key in ["mock_title", "mock_author", "mock_publisher", "mock_date", "mock_desc"]:
    if key not in st.session_state:
        st.session_state[key] = "(API自動取得予定)"
if "amz_prices" not in st.session_state:
    st.session_state["amz_prices"] = {}

# 出品モードの選択（ラジオボタンを操作した瞬間に画面を切り替えるため、formの外に配置します）
listing_mode = st.radio(
    "出品モード", 
    ["新規出品 (Amazon未出品 / 棚番号からSKU生成)", "既存Amazon在庫の横展開 (Amazonは出品済)"],
    horizontal=True
)

# 入力フォーム (リアルタイム反映のため st.form を廃止)
if True:
    if "target_asin" not in st.session_state:
        st.session_state["target_asin"] = ""
    if "trigger_fetch" not in st.session_state:
        st.session_state["trigger_fetch"] = False
        
    col_sku1, col_sku2 = st.columns(2)
    with col_sku1:
        if "新規出品" in listing_mode:
            shelf_location = st.text_input("棚番号 (必須, 例: DA)", max_chars=2).upper()
            input_sku = ""
        else:
            input_sku = st.text_input("Amazonの既存SKU (必須)")
            if st.button("🔍 SKUからASINを逆引きして取得", use_container_width=True):
                if not input_sku:
                    st.error("既存SKUを入力してください")
                else:
                    with st.spinner("APIで逆引き・自社在庫情報を取得中..."):
                        fetched_asin = get_asin_from_sku(input_sku)
                        my_info = get_my_inventory_info(input_sku)
                        
                        st.session_state["target_asin"] = fetched_asin
                        st.session_state["my_price"] = my_info["price"]
                        st.session_state["my_condition"] = my_info["condition"]
                        st.session_state["trigger_fetch"] = True
                    st.rerun()
            shelf_location = "既存"
            
    with col_sku2:
        asin_isbn = st.text_input("ASIN / ISBN (必須)", key="target_asin")
        fetch_clicked = st.button("🔍 ISBNから商品情報を取得", use_container_width=True)
        
        if fetch_clicked or st.session_state["trigger_fetch"]:
            if st.session_state["trigger_fetch"]:
                st.session_state["trigger_fetch"] = False  # フラグのリセット
                
            if not asin_isbn:
                st.error("ASIN / ISBN を入力してください。")
            else:
                with st.spinner("商品情報と価格を取得中..."):
                    book_data = fetch_book_info_ndl(asin_isbn)
                    amz_prices = fetch_amazon_prices(asin_isbn)
                    
                    st.session_state["amz_prices"] = amz_prices
                    
                    if book_data and book_data['title']:
                        st.session_state["mock_title"] = book_data['title']
                        st.session_state["mock_author"] = book_data['author']
                        st.session_state["mock_publisher"] = book_data['publisher']
                        st.session_state["mock_date"] = book_data['date']
                        st.session_state["mock_desc"] = book_data['desc']
                        st.success(f"✅ 「{book_data['title']}」を取得しました！")
                    else:
                        st.warning("⚠️ 該当する商品情報が見つかりませんでした。手動で入力するか別のISBNを試してください。")
                        st.session_state["mock_title"] = ""
                        st.session_state["mock_author"] = ""
                        st.session_state["mock_publisher"] = ""
                        st.session_state["mock_date"] = ""
                        st.session_state["mock_desc"] = ""
                st.rerun()

    # SKUの決定
    final_sku = input_sku
    if "新規出品" in listing_mode:
        if shelf_location and asin_isbn:
            today_str = datetime.datetime.now().strftime("%y%m%d")
            final_sku = f"{shelf_location}-{asin_isbn}-{today_str}"
        st.info(f"生成されるSKU: **{final_sku if final_sku else '棚番号とASINを入力すると自動で生成されます'}**")
    else:
        st.info(f"対象SKU: **{final_sku if final_sku else '既存のSKUを入力してください'}** (一文字も変えずに使用します)")
        st.info("※既存Amazon在庫の場合、Amazonへの価格更新リクエスト(上限・下限含む)が行われます。")
        # TODO: ここに「Amazonから商品情報を取得する」ボタンなどのロジックを追加予定
        
    col_price, col_cond, col_adult = st.columns([1, 1, 1])
    with col_cond:
        conditions = ["新品", "ほぼ新品", "非常に良い", "良い", "可", "全体的に状態が悪い"]
        
        default_index = 0
        if "既存" in listing_mode and "my_condition" in st.session_state:
            if st.session_state["my_condition"] in conditions:
                default_index = conditions.index(st.session_state["my_condition"])
                
        condition = st.selectbox("商品の状態 *必須", conditions, index=default_index)
        
    with col_price:
        # コンディションに応じたAmazon最安値を自動判定
        cond_map = {
            "新品": "new", "ほぼ新品": "like_new", "非常に良い": "very_good", 
            "良い": "good", "可": "acceptable", "全体的に状態が悪い": "acceptable"
        }
        cond_data = st.session_state["amz_prices"].get(cond_map.get(condition))
        auto_price = cond_data["price"] if cond_data else 0
        
        use_my_price = ("既存" in listing_mode and "my_price" in st.session_state)
        target_default_price = st.session_state["my_price"] if use_my_price else auto_price
        
        # 状態が切り替わるたびにnumber_inputを完全に再描画させるためのキー
        # 出品がない場合は fallback で勝手に1500円にせず、指定通り0にする
        widget_key = f"price_{condition}_{asin_isbn}"
        
        # 警告を消しつつ確実に反映させるため、session_stateに初期値をセットしますが、
        # number_input側の value パラメータは「指定しない」ことで干渉を防ぎます。
        if widget_key not in st.session_state:
            st.session_state[widget_key] = int(target_default_price) if target_default_price else 0
            
        base_price = st.number_input(
            "基準価格 (Amazonでの販売価格) *必須", 
            min_value=0, 
            step=1, 
            key=widget_key,
            placeholder="価格を入力..."
        )
        
        if use_my_price:
            st.caption(f"💼 現在の自社出品価格（{st.session_state['my_price']}円）を自動適用済")
        elif auto_price:
            st.caption(f"💡 {condition} のAmazon最安値（{int(auto_price)}円）を自動適用済")
        elif st.session_state.get("amz_prices"): # 価格取得はしたが、該当コンディションの出品がない場合
            st.caption(f"⚠️ {condition} の出品は現在Amazonにありません")

        # 全状態の価格と出品者数を表示
        if st.session_state.get("amz_prices"):
            html = "<div style='font-size: 0.85em; margin-top: 10px; color: #555; line-height: 1.6;'><strong>▼ コンディション別 最安値と出品者数 (上位20件中)</strong><br>"
            display_conds = [
                ("新品", "new"), ("ほぼ新品", "like_new"), 
                ("非常に良い", "very_good"), ("良い", "good"), ("可/悪い", "acceptable")
            ]
            for jpn, eng in display_conds:
                d = st.session_state["amz_prices"].get(eng)
                if d:
                    html += f"・ {jpn}: <b style='color:#222'>{d['price']}円</b> ({d['count']}人)<br>"
                else:
                    html += f"・ {jpn}: <span style='color:#aaa'>なし</span><br>"
            
            html += "</div>"
            st.markdown(html, unsafe_allow_html=True)
            
    with col_adult:
        st.write("") # 縦位置調整用
        st.write("") 
        is_adult = st.checkbox("🔞 アダルト対象 (長文説明を省略)", value=False)
        
    # KeepaグラフとAPIデータの表示
    if asin_isbn and st.session_state.get("amz_prices"):
        asin = isbn13_to_asin(asin_isbn)
        with st.expander("📈 Keepa データ解析 (価格推移・売れ行き)", expanded=True):
            # 1. JSONデータの解析と表紙・タイトルの表示
            with st.spinner("Keepa詳細データを解析中..."):
                keepa_product = fetch_keepa_data(asin)
            
            k_stats = None
            if keepa_product:
                k_stats = keepa_product.get("stats", {})
                
                k_title = keepa_product.get("title", "商品名不明")
                k_images_csv = keepa_product.get("imagesCSV")
                k_images_list = keepa_product.get("images")
                
                first_img = None
                if k_images_csv and isinstance(k_images_csv, str):
                    first_img = k_images_csv.split(",")[0].strip()
                elif k_images_list and isinstance(k_images_list, list) and len(k_images_list) > 0:
                    first_img = k_images_list[0].get("l") or k_images_list[0].get("m")
                
                col_img, col_title = st.columns([1, 3])
                with col_img:
                    if first_img:
                        cover_url = f"https://m.media-amazon.com/images/I/{first_img}"
                        st.image(cover_url, use_container_width=True)
                    else:
                        st.write("画像なし")
                with col_title:
                    st.subheader(k_title)
                    
            st.markdown("---")

            # 2. グラフ画像の直接表示 (認証キーつき・日本ドメイン=5)
            img_url = f"https://api.keepa.com/graphimage?key={KEEPA_API_KEY}&domain=5&asin={asin}&width=800&height=300&salesrank=1&new=1&used=1&bb=1&range=90"
            st.image(img_url, use_container_width=True)
            
            # Amazon商品ページへの直リンク
            st.markdown(f"<p style='font-size: 0.85em; color: gray; margin-top: -10px;'>※より詳細なデータを分析したい場合は <a href='https://www.amazon.co.jp/dp/{asin}' target='_blank'>Amazon商品ページを開く</a></p>", unsafe_allow_html=True)
            
            # 3. Metrics表示
            if k_stats:
                drops_90 = k_stats.get("salesRankDrops90", -1)
                buybox = k_stats.get("buyBoxPrice", -1)
                avg90_new = k_stats.get("avg90", [])[1] if len(k_stats.get("avg90", [])) > 1 else -1
                avg90_used = k_stats.get("avg90", [])[2] if len(k_stats.get("avg90", [])) > 2 else -1
                
                def fmt_val(v, unit, is_drop=False):
                    if v == -1 or v == -2: return "データなし"
                    if is_drop: return f"{v} 回"
                    return f"{v} {unit}"
                
                st.markdown("<div style='font-size: 0.9em; margin-top: 10px; font-weight: bold;'>▼ Keepa 解析データ</div>", unsafe_allow_html=True)
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("90日ドロップ (推定販売数)", fmt_val(drops_90, "回", True))
                c2.metric("カート価格 (BuyBox)", fmt_val(buybox, "円"))
                c3.metric("90日平均 (新品)", fmt_val(avg90_new, "円"))
                c4.metric("90日平均 (中古)", fmt_val(avg90_used, "円"))
                
                # エラーハンドリング（すべて-1や-2の場合）
                if drops_90 in (-1, -2) and buybox in (-1, -2) and avg90_new in (-1, -2) and avg90_used in (-1, -2):
                    st.info("💡 Keepa上の過去データなし（Amazonの現在価格を優先します）")
            else:
                st.warning("⚠️ Keepaデータの取得・解析に失敗しました。")
            
    st.markdown("---")
    st.write("##### 📝 商品説明（プラットフォーム別）")
    st.info("共通の特記事項を入力すると、各プラットフォームのテンプレに自動反映されます。個別タブで手直しも可能です。")
    
    common_note = st.text_area("共通の特記事項 (状態に関する補足など)", placeholder="例: カバー上部に軽微な折れがありますが、通読に支障はありません。")
    
    tab_amz, tab_mer, tab_q10, tab_fur = st.tabs(["Amazon", "メルカリShops", "Qoo10", "日本の古本屋"])

    # 共通の商品情報ブロック
    info_header = ""
    if st.session_state.get('mock_title', '') and st.session_state['mock_title'] != "(API自動取得予定)":
        info_header = f"【商品情報】\nタイトル：{st.session_state['mock_title']}\n著者名：{st.session_state['mock_author']}\n出版社：{st.session_state['mock_publisher']}\n発行日：{st.session_state['mock_date']}\nISBN：{asin_isbn}\n\n"
    
    # 共通のあらすじブロック
    desc_block_common = "" if is_adult else f"【内容紹介】\n{st.session_state.get('mock_desc', '')}\n\n------------------------------\n"
    
    # 動的キー（条件が変わるたびにテキストエリアを強制更新させるため）
    dynamic_key_suffix = f"{condition}_{is_adult}_{st.session_state.get('mock_title', '')}"

    with tab_amz:
        # Amazonのコンディション説明には「タイトル」「あらすじ」は不要（Amazonカタログに既存載っているため）
        amz_tpl = f"【状態: {condition}】\n{common_note}"
        desc_amz = st.text_area("Amazon用", value=amz_tpl, height=250, key=f"amz_{dynamic_key_suffix}")
        
    with tab_mer:
        if condition == "新品":
            condition_block = f"""【新品／バーゲンブック（自由価格本）】

本商品は、出版社の意思で定価販売から外れ、割引販売が可能になった「未使用の新品」です。古本ではありません。

【状態について】

裏表紙バーコード部分にBBシール、または本の「地」に赤丸・線引き・捺印等のマーキングがある場合があります。
帯は付属しない場合がございます。
発売から期間が経過している場合、表紙・カバー等に軽微なスレ、経年のヤケ・シミが見られることがあります。
いずれも読了に支障はありません。
マーキング・経年の程度には個体差があります。

{common_note}

【ご注意】

バーゲンブックの特性をご理解のうえご購入ください。
返品・交換はメルカリShopsのルールに準拠します（受取評価前にご連絡ください）。

検索用：
バーゲンブック 自由価格本 アウトレット 本 セール"""
        else:
            condition_block = f"""【中古本 / コンディション：{condition}】

本商品は中古品となります。

【状態について】

通常使用に伴う若干の傷み（スレ、キズ、ヤケ、汚れなど）がある場合がございますが、通読には問題ありません。
帯・付録・特典等は、特に記載がない限り原則付属いたしません。

{common_note}

【ご注意】

中古品の特性をご理解・ご納得いただいたうえでご購入ください。
万が一、記載されていない重大な欠陥（ページの欠落、読めないほどの汚れなど）があった場合は、受取評価前にご連絡ください。

検索用：
古本 中古本 本 古書"""

        mercari_tpl = f"""{info_header.strip()}

{desc_block_common}{condition_block}

------------------------------
【梱包・発送】

防水梱包にて発送します。
発送方法：メルカリBiz配送
発送目安：4〜7日以内"""
        desc_mer = st.text_area("メルカリShops用", value=mercari_tpl, height=250, key=f"mer_{dynamic_key_suffix}")
        
    with tab_q10:
        q10_tpl = f"{info_header}{desc_block_common}【コンディション: {condition}】\n{common_note}"
        desc_q10 = st.text_area("Qoo10用", value=q10_tpl, height=250, key=f"q10_{dynamic_key_suffix}")
        
    with tab_fur:
        fur_tpl = f"{info_header}{desc_block_common}{condition} / {common_note}"
        desc_fur = st.text_area("日本の古本屋用", value=fur_tpl, height=250, key=f"fur_{dynamic_key_suffix}")
    
    st.markdown("---")
    st.write("##### 📷 商品画像")
    if "新規出品" in listing_mode:
        uploaded_images = st.file_uploader("写真を選択またはドラッグ＆ドロップしてアップロード（複数可）", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    else:
        uploaded_images = []
        st.info("💡 **画像自動取得**: Amazonの既存カタログ画像や出品画像を自動で取得し、他プラットフォームへ流用するためアップロードは不要です。")
        
    st.markdown("---")
    st.write("##### 🚀 出品プラットフォームの選択")
    st.write("※エロ本や条件に合わない販売先はチェックを外して出品をスキップできます。")
    col_p1, col_p2, col_p3, col_p4 = st.columns(4)
    with col_p1:
        target_amazon = st.checkbox("Amazon", value=True)
    with col_p2:
        target_mercari = st.checkbox("メルカリShops", value=True)
    with col_p3:
        target_qoo10 = st.checkbox("Qoo10", value=True)
    with col_p4:
        target_furuhon = st.checkbox("日本の古本屋", value=True)
        
    st.markdown("---")
    submitted = st.button("出品データを生成・送信する", type="primary", use_container_width=True)

if submitted:
    if "新規出品" in listing_mode and (not final_sku or not asin_isbn):
        st.error("棚番号とASIN/ISBNは必須項目です。")
    elif "既存Amazon在庫" in listing_mode and not final_sku:
        st.error("既存のAmazon SKUを入力してください。")
    else:
        st.info("処理を開始します...")
        
        # 1. DB保存
        # (横展開の場合はASINが空になる可能性があるため、プレースホルダーを入れるか、将来的に取得したASINを入れる)
        save_asin = asin_isbn if asin_isbn else "待機中"
        targets = {
            'Amazon': target_amazon,
            'Mercari': target_mercari,
            'Qoo10': target_qoo10,
            'Furuhon': target_furuhon
        }
        success, msg = save_to_db(final_sku, save_asin, shelf_location, base_price, condition, common_note, targets)
        if not success:
            st.error(msg)
        else:
            st.success("✅ マスターデータベース(SQLite)への保存が完了しました。")
            
            # 画像の保存/処理状況のアナウンス
            if uploaded_images:
                img_dir = os.path.join(EXPORT_DIR, "images", final_sku)
                os.makedirs(img_dir, exist_ok=True)
                for i, img_file in enumerate(uploaded_images):
                    with open(os.path.join(img_dir, f"{i+1}_{img_file.name}"), "wb") as f:
                        f.write(img_file.getbuffer())
                st.success(f"🖼️ {len(uploaded_images)}枚の商品画像を一時保存しました。(保存先: {img_dir})")
            elif "既存Amazon在庫" in listing_mode:
                st.info("🖼️ 画像はAPI連携時にAmazonから自動的に取得・ダウンロードして使用します。")
                
            st.markdown("---")
            
            # 2. 各プラットフォームへの処理
            st.markdown("---")
            st.subheader("🚀 一斉出品処理ログ")
            
            run_date = datetime.datetime.now().strftime("%Y%m%d")
            
            summary_data = []

            # Amazon
            amz_calc = calc_amazon_price(base_price)
            if not target_amazon:
                summary_data.append({"販路": "Amazon", "計算価格": "-", "状態": "🚫 スキップ"})
            elif "新規出品" in listing_mode:
                # 【確認済み】新規モードでも確実にTSV出力関数を呼び出しています
                amz_file, p, p_min, p_max = export_amazon_tsv(final_sku, base_price, condition, run_date)
                st.success(f"📦 [Amazon] CSVを出力しました: `{os.path.basename(amz_file)}` (本体 {p}円 / 下限: {p_min} / 上限: {p_max})")
                summary_data.append({"販路": "Amazon (新規)", "計算価格": f"¥{amz_calc}", "状態": "✅ CSV追記"})
            else:
                # 【確認済み】既存モードでも確実にTSV出力関数を呼び出しています
                amz_file, p, p_min, p_max = export_amazon_tsv(final_sku, base_price, condition, run_date)
                st.success(f"📦 [Amazon] CSVを出力しました: `{os.path.basename(amz_file)}` (本体 {p}円 / 下限: {p_min} / 上限: {p_max})")
                summary_data.append({"販路": "Amazon (価格更新)", "計算価格": f"¥{amz_calc}", "状態": "✅ CSV追記"})
                
            # メルカリShops
            mer_calc = calc_mercari_price(base_price)
            if not target_mercari:
                summary_data.append({"販路": "メルカリShops", "計算価格": "-", "状態": "🚫 スキップ"})
            else:
                mer_file = export_mercari_csv(final_sku, asin_isbn, base_price, condition, desc_mer, run_date)
                st.success(f"🛍 [メルカリShops] CSVを出力しました: `{os.path.basename(mer_file)}` (追記)")
                summary_data.append({"販路": "メルカリShops", "計算価格": f"¥{mer_calc}", "状態": "✅ CSV追記"})
                
            # Qoo10
            q_calc = calc_qoo10_price(base_price)
            if not target_qoo10:
                summary_data.append({"販路": "Qoo10", "計算価格": "-", "状態": "🚫 スキップ"})
            else:
                q_file = export_qoo10_csv(final_sku, asin_isbn, base_price, condition, desc_q10, run_date)
                st.success(f"🛒 [Qoo10] CSVを出力しました: `{os.path.basename(q_file)}` (追記)")
                summary_data.append({"販路": "Qoo10", "計算価格": f"¥{q_calc}", "状態": "✅ CSV追記"})
                
            # 日本の古本屋
            fur_calc = calc_furuhon_price(base_price)
            if not target_furuhon:
                summary_data.append({"販路": "日本の古本屋", "計算価格": "-", "状態": "🚫 スキップ"})
            else:
                fur_file = export_furuhon_tsv(final_sku, asin_isbn, base_price, condition, desc_fur, run_date)
                st.success(f"📚 [日本の古本屋] CSVを出力しました: `{os.path.basename(fur_file)}` (追記)")
                summary_data.append({"販路": "日本の古本屋", "計算価格": f"¥{fur_calc}", "状態": "✅ CSV追記"})
                
            st.markdown("---")
            st.success(f"### 🎯 射撃完了！ `exports` フォルダにデータが生成されました")
            
            # 結果プレビューをTableで見やすく表示
            st.table(pd.DataFrame(summary_data))

st.markdown("---")
st.subheader("データベース登録状況 (最新10件)")
if os.path.exists(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    df_db = pd.read_sql_query("SELECT id, sku, asin_isbn, shelf_location, base_price, condition, amazon_status, created_at FROM listings ORDER BY id DESC LIMIT 10", conn)
    conn.close()
    st.dataframe(df_db, use_container_width=True)
