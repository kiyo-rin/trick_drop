import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import imaplib
import email
from email.header import decode_header
import time
import re
import datetime
from email.utils import parsedate_to_datetime

# from amazon_orders import render_amazon_orders_page

# ページ設定
st.set_page_config(page_title="TRICK DROP", page_icon="⚡️", layout="wide")


import os
import streamlit as st

@st.cache_resource
def setup_apple_icon():
    try:
        # Streamlitのインストールパスを取得
        st_dir = os.path.dirname(st.__file__)
        index_path = os.path.join(st_dir, 'static', 'index.html')
        
        with open(index_path, 'r', encoding='utf-8') as f:
            html = f.read()

        if 'apple-touch-icon' not in html:
            b64_icon = "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"
            tag = '<link rel="apple-touch-icon" href="data:image/png;base64,' + b64_icon + '">'
            # <head>タグの直後に追加
            new_html = html.replace('<head>', '<head>' + tag)
            
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(new_html)
    except Exception as e:
        print("Failed to patch index.html:", e)

setup_apple_icon()



# 未読メールを取得する関数
@st.cache_data(ttl=300) # 5分間は結果をキャッシュして再読み込みを高速化
def get_unread_count(account_type="muumuu"):
    try:
        # Secretsから情報を取得
        if account_type == "muumuu":
            user = st.secrets["email"]["muumuu_user"]
            password = st.secrets["email"]["muumuu_pass"]
            server = st.secrets["email"]["muumuu_server"]
        elif account_type == "gmail_kiyota":
            if "gmail_kiyota_user" not in st.secrets["email"]:
                return None, "Secretsにgmail_kiyota_userが設定されていません"
            user = st.secrets["email"]["gmail_kiyota_user"]
            password = st.secrets["email"]["gmail_kiyota_pass"]
            server = "imap.gmail.com"
        elif account_type == "gmail_kiyotaka":
            if "gmail_kiyotaka_user" not in st.secrets["email"]:
                return None, "Secretsにgmail_kiyotaka_userが設定されていません"
            user = st.secrets["email"]["gmail_kiyotaka_user"]
            password = st.secrets["email"]["gmail_kiyotaka_pass"]
            server = "imap.gmail.com"
        elif account_type == "yahoo":
            if "yahoo_user" not in st.secrets["email"]:
                return None, "Secretsにyahoo_userが設定されていません"
            user = st.secrets["email"]["yahoo_user"]
            password = st.secrets["email"]["yahoo_pass"]
            server = "imap.mail.yahoo.co.jp"
        else:
            return None, "未対応のアカウントタイプ"
        
        # IMAPサーバーに接続
        mail = imaplib.IMAP4_SSL(server)
        mail.login(user, password)
        mail.select("inbox")
        
        # 未読メールを検索
        status, response = mail.search(None, 'UNSEEN')
        if status == 'OK':
            unread_ids = response[0].split()
            count = len(unread_ids)
            mail.logout()
            return count, None
        return 0, None
    except Exception as e:
        return None, str(e)

# 未読数の取得を実行
muumuu_count, muumuu_error = get_unread_count("muumuu")
muumuu_badge = ""
if muumuu_error:
    st.sidebar.error(f"独自ドメイン連携エラー: {muumuu_error}")
elif muumuu_count is not None:
    muumuu_badge = f" 🔴 **{muumuu_count}**" if muumuu_count > 0 else " 🟢"

gmail_kiyota_count, gmail_kiyota_error = get_unread_count("gmail_kiyota")
gmail_kiyota_badge = ""
if gmail_kiyota_error:
    st.sidebar.error(f"Gmail(きよた)連携エラー: {gmail_kiyota_error}")
elif gmail_kiyota_count is not None:
    gmail_kiyota_badge = f" 🔴 **{gmail_kiyota_count}**" if gmail_kiyota_count > 0 else " 🟢"

gmail_kiyotaka_count, gmail_kiyotaka_error = get_unread_count("gmail_kiyotaka")
gmail_kiyotaka_badge = ""
if gmail_kiyotaka_error:
    st.sidebar.error(f"Gmail(清隆)連携エラー: {gmail_kiyotaka_error}")
elif gmail_kiyotaka_count is not None:
    gmail_kiyotaka_badge = f" 🔴 **{gmail_kiyotaka_count}**" if gmail_kiyotaka_count > 0 else " 🟢"

yahoo_count, yahoo_error = get_unread_count("yahoo")
yahoo_badge = ""
if yahoo_error:
    st.sidebar.error(f"Yahoo!連携エラー: {yahoo_error}")
elif yahoo_count is not None:
    yahoo_badge = f" 🔴 **{yahoo_count}**" if yahoo_count > 0 else " 🟢"

# Google自動翻訳を無効化するメタタグを挿入
st.markdown('<meta name="google" content="notranslate">', unsafe_allow_html=True)

# カスタムCSS（クリーンなライトモードUI）
st.markdown("""
<style>
    /* アプリ全体の背景と基本文字色 */
    .stApp {
        background-color: #FFFFFF;
        color: #1F2937;
    }
    
    /* サイドバーの背景 */
    [data-testid="stSidebar"] {
        background-color: #F8F9FA;
        border-right: 1px solid #E5E7EB;
    }
    
    /* ヘッダーデザイン */
    .main-header {
        font-size: 2.4rem;
        font-weight: 700;
        color: #111827;
        letter-spacing: 1px;
        padding-bottom: 10px;
        margin-bottom: 20px;
        border-bottom: 1px solid #E5E7EB;
    }
    
    /* スローガン */
    .slogan {
        font-size: 1.1rem;
        font-weight: 500;
        color: #6B7280;
        font-style: italic;
        margin-bottom: 2rem;
        letter-spacing: 0.5px;
    }
    
    /* メトリック（KPI）の文字色 */
    [data-testid="stMetricValue"] {
        color: #1F2937 !important;
    }
    [data-testid="stMetricDelta"] {
        color: #10B981 !important;
    }
    
    /* テーブルのデザイン調整 */
    .stDataFrame {
        border: 1px solid #E5E7EB;
    }
</style>
""", unsafe_allow_html=True)

# サイドバー
st.sidebar.title("TRICK DROP ⚡️")
st.sidebar.markdown("**NAVIGATION**")

pages = [
    "🎰 司令室 (メイン)", 
    "📚 YGシステム (無在庫)", 
    # "未発送の注文 (Amazon)",
    "📖 国内有在庫 (千葉・神田)", 
    "🌐 B28コマンド (越境プレ値)"
]

# URLパラメータから現在のページを取得してデフォルト選択にする
default_index = 0
if "page" in st.query_params:
    try:
        default_index = pages.index(st.query_params["page"])
    except ValueError:
        pass

page = st.sidebar.radio("", pages, index=default_index)

# 選択されたページをURLパラメータに保存（リロード対策）
st.query_params["page"] = page

st.sidebar.markdown("---")
st.sidebar.markdown("**🔗 クイックアクセス**")
st.sidebar.markdown("- [📦 Amazon Seller Central](https://sellercentral.amazon.co.jp/)")
st.sidebar.markdown("- [🛍️ メルカリShops](https://mercari-shops.com/seller/shops)")
st.sidebar.markdown("- [📚 日本の古本屋](https://www.kosho.or.jp/koshoadmin/)")
st.sidebar.markdown("- [🔨 ヤフオク!](https://auctions.yahoo.co.jp/my)")
st.sidebar.markdown("- [⚙️ AppTool](https://apptool.jp/mypage)")
st.sidebar.markdown("- [🔴 メルカリ](https://jp.mercari.com/)")
st.sidebar.markdown("- [📊 Amazon KDP レポート](https://kdpreports.amazon.co.jp/dashboard)")
st.sidebar.markdown("- [🏷️ プライスター](https://jp3.pricetar.com/seller)")
st.sidebar.markdown("- [🖨️ ラベル屋さん](https://www.labelyasan.com/)")
st.sidebar.markdown("- [🔍 駿河屋あんしん買取](https://www.suruga-ya.jp/kaitori/search_buy?category=&search_word=)")

st.sidebar.markdown("---")
st.sidebar.markdown("**🛒 仕入れ先**")
st.sidebar.markdown("- [📖 八木書店バーゲンブック](https://www.books-yagi.co.jp/bb/)")
st.sidebar.markdown("- [🐟 魚住書店](https://www.uozumishoten.jp/cart.cgi)")
st.sidebar.markdown("- [🏢 三協社](http://book-sankyo.co.jp/)")

st.sidebar.markdown("---")
st.sidebar.markdown("**✉️ メールボックス**")
st.sidebar.markdown(f"- [✉️ 独自ドメイン (メイン)]({f'https://webmail.muumuu-domain.com/mail/INBOX'}){muumuu_badge}")
st.sidebar.markdown(f"- [📧 Gmail (きよた書店)](https://mail.google.com/mail/u/0/){gmail_kiyota_badge}")
st.sidebar.markdown(f"- [📧 Gmail (清隆)](https://mail.google.com/mail/u/1/){gmail_kiyotaka_badge}")

st.sidebar.markdown(f"- [ Yahoo!メール](https://mail.yahoo.co.jp/){yahoo_badge}")

st.sidebar.markdown("---")
st.sidebar.markdown("**🏦 銀行・財務**")
st.sidebar.markdown("- [🏧 GMOあおぞらネット銀行](https://sso.gmo-aozora.com/b2c/login?service=https%3A%2F%2Fbank.gmo-aozora.com%2Fbank)")
st.sidebar.markdown("- [📁 財務フォルダ (Google Drive)](https://drive.google.com/drive/u/0/folders/1lxnbNFHyLMLjL0RfcwvL3xqufuotdNAT)")

st.sidebar.markdown("---")
st.sidebar.markdown("**🚚 配送・物流**")
st.sidebar.markdown("- [🐈‍⬛ ヤマトビジネスメンバーズ](https://bmypage.kuronekoyamato.co.jp/bmypage/servlet/jp.co.kuronekoyamato.wur.hmp.servlet.user.HMPLGI0010JspServlet)")
st.sidebar.markdown("- [📮 クリックポスト](https://clickpost.jp/)")
st.sidebar.markdown("- [🏣 郵便局 (荷物問合せ)](https://www.post.japanpost.jp/)")
st.sidebar.markdown("- [🏣 郵便局集荷サービス](https://mgr.post.japanpost.jp/C20P02Action_Login_PC.do?ssoparam=1&termtype=0)")
st.sidebar.markdown("- [🚛 西濃運輸](https://www.seino.co.jp/seino/)")
st.sidebar.markdown("- [🏃 佐川急便](https://www.sagawa-exp.co.jp/)")

st.sidebar.markdown("---")
st.sidebar.markdown("**🌍 越境EC**")
st.sidebar.markdown("- [🇸🇬 Shopee SG](https://seller.shopee.sg/)")
st.sidebar.markdown("- [🇹🇼 Shopee TW](https://seller.shopee.tw/)")
st.sidebar.markdown("- [🌎 eBay](https://www.ebay.com/)")

# 共通データ生成用
np.random.seed(42)
months = [f"2026-{m:02d}" for m in range(1, 6)]

# 自動で注文メールを取得する関数
@st.cache_data(ttl=600)  # 10分間キャッシュ
def get_recent_orders():
    orders = []
    try:
        user = st.secrets["email"]["gmail_kiyota_user"]
        password = st.secrets["email"]["gmail_kiyota_pass"]
        server = "imap.gmail.com"
        
        mail = imaplib.IMAP4_SSL(server)
        mail.login(user, password)
        mail.select("inbox")
        
        # 過去2週間分のメールIDをサーバー側で絞り込んで取得
        from datetime import datetime, timedelta
        search_date = (datetime.now() - timedelta(days=14)).strftime("%d-%b-%Y")
        status, response = mail.search(None, 'SINCE', search_date)
        
        if status == 'OK':
            email_ids = response[0].split()
            latest_ids = email_ids[-1000:]
            
            # まとめて取得 (1度に100件ずつリクエストして高速化)
            chunk_size = 100
            for i in range(len(latest_ids)-1, -1, -chunk_size):
                start_idx = max(0, i - chunk_size + 1)
                chunk_ids = latest_ids[start_idx : i + 1]
                
                # 新しい順に処理するためチャンク内を反転
                chunk_ids = chunk_ids[::-1]
                ids_str = b",".join(chunk_ids)
                
                # RFC822でメール本文をまとめて取得
                status, data = mail.fetch(ids_str, '(BODY.PEEK[])')
                if status != 'OK': continue
                
                for response_part in data:
                    if isinstance(response_part, tuple):
                        raw_email = response_part[1]
                        msg = email.message_from_bytes(raw_email)
                        
                        # 件名のデコード
                        subject_tuple = decode_header(msg['Subject'])[0]
                        subject = subject_tuple[0]
                        encoding = subject_tuple[1]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding if encoding else 'utf-8', errors='ignore')
                            
                        # 日付のフォーマット
                        date_str = msg.get('Date', '')
                        try:
                            dt = parsedate_to_datetime(date_str)
                            from datetime import timezone
                            jst = timezone(timedelta(hours=9))
                            dt_jst = dt.astimezone(jst)
                            formatted_date = dt_jst.strftime('%Y/%m/%d %H:%M')
                        except:
                            formatted_date = date_str
                        
                        # 送信元の確認
                        from_addr = msg.get('From', '')
                        
                        # 本文を取得 (メルカリ等の商品管理コード確認用)
                        body = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == 'text/plain':
                                    body_bytes = part.get_payload(decode=True)
                                    if body_bytes:
                                        charset = part.get_content_charset() or 'utf-8'
                                        try:
                                            body = body_bytes.decode(charset, errors='ignore')
                                        except:
                                            body = body_bytes.decode('utf-8', errors='ignore')
                                    break
                        else:
                            body_bytes = msg.get_payload(decode=True)
                            if body_bytes:
                                charset = msg.get_content_charset() or 'utf-8'
                                try:
                                    body = body_bytes.decode(charset, errors='ignore')
                                except:
                                    body = body_bytes.decode('utf-8', errors='ignore')
                        
                        # ① Amazonの注文判定
                        if '注文確定' in subject and 'amazon.co.jp' in from_addr.lower():
                            # YGから始まるSKUのみを対象とする
                            if not re.search(r'[:\s]YG', subject) and 'YG' not in body:
                                continue
                                
                            # SKUの抽出
                            sku = ""
                            sku_match = re.search(r'(YG[A-Za-z0-9\-]+)', subject)
                            if not sku_match:
                                sku_match = re.search(r'(YG[A-Za-z0-9\-]+)', body)
                            if sku_match:
                                sku = sku_match.group(1)
                                
                            # メール本文から商品名を抽出 (一番確実なため)
                            product_name = ""
                            body_match = re.search(r'(?:商品|商品名)\s*[:：]\s*([^\n\r]+)', body)
                            if body_match:
                                product_name = body_match.group(1).strip()
                            else:
                                # 何らかの理由で本文から取れない場合は件名から綺麗に抽出
                                product_name = subject
                                if '注文確定' in product_name:
                                    product_name = product_name.split('注文確定')[-1]
                                product_name = re.sub(r'^\s*[\-\:]?\s*出品者出荷のご注文\s*[\-\:]?\s*', '', product_name)
                                product_name = re.sub(r'^[\s:\-]*', '', product_name)
                                product_name = re.sub(r'^(?:SKU\s*[:\-]?\s*)?[A-Za-z0-9\-_]+\s+', '', product_name)
                                
                            # 商品名から "[Tankobon Hardcover] [2022] 著者名" のような不要なAmazonの装飾タグを一掃する
                            product_name = re.sub(r'\s*\[Tankobon.*', '', product_name, flags=re.IGNORECASE)
                            product_name = re.sub(r'\s*\[JP Oversized.*', '', product_name, flags=re.IGNORECASE)
                            product_name = re.sub(r'\s*\[(?:単行本|文庫|ペーパーバック|大型本|新書)\].*', '', product_name)
                            product_name = re.sub(r'\s*\((?:単行本|文庫|ペーパーバック|大型本|新書)\).*', '', product_name)
                            
                            # 商品名の先頭に万が一SKUが残っていたら、正規表現で強力に消す
                            product_name = re.sub(r'^[:：\s]*(?:SKU)?[:：\s]*YG[A-Za-z0-9\-]+[\s:：\-]*', '', product_name, flags=re.IGNORECASE)
                            
                            # さらにもう一度、先頭に残った不要な記号(:や-など)を確実に消す
                            product_name = re.sub(r'^[:：\-\s]+', '', product_name).strip()
                            
                            # 数量の抽出
                            quantity = "1"
                            qty_match = re.search(r'数量\s*[:：]\s*(\d+)', body)
                            if qty_match:
                                quantity = qty_match.group(1)
                                
                            if int(quantity) > 1:
                                quantity_display = f"🚨 {quantity}冊"
                            else:
                                quantity_display = "1"
                            
                            orders.append({
                                "受信日時": formatted_date,
                                "プラットフォーム": "📦 Amazon",
                                "SKU": sku,
                                "数量": quantity_display,
                                "商品名": product_name.strip(),
                                "ステータス": "🔴 未発注_八木"
                            })
                            
                        # ② メルカリShopsの注文判定
                        elif '【メルカリShops】' in subject:
                            if ('発送' in subject or '購入' in subject) and 'メッセージ' not in subject:
                                if 'YG' not in body and '商品管理コード : YG' not in body:
                                    continue
                                    
                                # SKUの抽出
                                sku = ""
                                sku_match = re.search(r'(YG[A-Za-z0-9\-]+)', body)
                                if sku_match:
                                    sku = sku_match.group(1)
                                    
                                match = re.search(r'「(.*?)」', subject)
                                product_name = match.group(1) if match else subject.replace('【メルカリShops】', '')
                                
                                # 数量の抽出 (メルカリShops)
                                quantity = "1"
                                qty_match = re.search(r'(?:数量|購入数|商品個数)\s*[:：]\s*(\d+)', body)
                                if qty_match:
                                    quantity = qty_match.group(1)
                                    
                                if int(quantity) > 1:
                                    quantity_display = f"🚨 {quantity}冊"
                                else:
                                    quantity_display = "1"
                                
                                orders.append({
                                    "受信日時": formatted_date,
                                    "プラットフォーム": "🔴 メルカリShops",
                                    "SKU": sku,
                                    "数量": quantity_display,
                                    "商品名": product_name,
                                    "ステータス": "🔴 未発注_八木"
                                })
                        
        mail.logout()
    except Exception as e:
        st.error(f"注文リスト取得エラー: {e}")
        
    return pd.DataFrame(orders)

# グラフの共通設定用関数
def update_modern_layout(fig):
    fig.update_layout(
        template="plotly_white",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#1F2937"),
        margin=dict(t=40, b=40, l=40, r=40)
    )
    return fig

if page == "🎰 司令室 (メイン)":
    st.markdown('<div class="main-header">🎰 司令室 (Command Center)</div>', unsafe_allow_html=True)
    st.markdown('<div class="slogan">TRICK DROP — 「ありえない成功を生み出す、仕掛けられた自販機」 ⚡️🎰</div>', unsafe_allow_html=True)
    
    # --- 1. 横断検索ツール ---
    st.markdown("### 🔍 最速！一括横断検索")
    search_query = st.text_input("本・商品のタイトルやISBNを入力", placeholder="例: 9784001111111 (Enterキーを押すと各検索ボタンが出現します)")
    
    if search_query:
        import urllib.parse
        q_url = urllib.parse.quote(search_query)
        
        amazon_url = f"https://www.amazon.co.jp/s?k={q_url}"
        mercari_url = f"https://jp.mercari.com/search?keyword={q_url}"
        yahoo_url = f"https://auctions.yahoo.co.jp/search/search?p={q_url}"
        takara_url = f"https://www.kosho.or.jp/products/list.php?mode=search&name={q_url}"
        
        st.markdown(f"""
        <div style="display: flex; gap: 15px; margin-bottom: 30px; flex-wrap: wrap;">
            <a href="{amazon_url}" target="_blank" style="padding: 10px 20px; background-color: #232F3E; color: white; border-radius: 5px; text-decoration: none; font-weight: bold; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">📦 Amazon</a>
            <a href="{mercari_url}" target="_blank" style="padding: 10px 20px; background-color: #E32B36; color: white; border-radius: 5px; text-decoration: none; font-weight: bold; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">🔴 メルカリ</a>
            <a href="{yahoo_url}" target="_blank" style="padding: 10px 20px; background-color: #FF0033; color: white; border-radius: 5px; text-decoration: none; font-weight: bold; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">🔨 ヤフオク</a>
            <a href="{takara_url}" target="_blank" style="padding: 10px 20px; background-color: #2E8B57; color: white; border-radius: 5px; text-decoration: none; font-weight: bold; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">📚 日本の古本屋</a>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    
    # --- 2. メモと定型文の2段組み ---
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📝 保存されるメモ帳")
        import os
        MEMO_FILE = "memo.txt"
        if os.path.exists(MEMO_FILE):
            with open(MEMO_FILE, "r", encoding="utf-8") as f:
                default_memo = f.read()
        else:
            default_memo = "【今日のTODO】\n・\n\n【仕入れメモ】\n・"
            
        new_memo = st.text_area("文字を書いて枠外をクリックすると自動で保存されます💡", value=default_memo, height=300)
        if new_memo != default_memo:
            with open(MEMO_FILE, "w", encoding="utf-8") as f:
                f.write(new_memo)
                
    with col2:
        st.markdown("### 📋 定型文・コピーパッド")
        st.caption("右上のコピーマーク(❐)をクリックすれば一発でコピーできます。")
        
        st.caption("▼ 発送完了メッセージ (顧客用)")
        st.code("ご購入ありがとうございます！\n本日、商品を発送いたしました。\n到着まで今しばらくお待ちくださいませ。\n引き続きよろしくお願いいたします。", language="text")
        
        st.caption("▼ 指示メッセージ (作業スタッフ用)")
        st.code("お疲れ様です！\n本日のデータを確認し、作業ファイルを更新しました。\n不明点があればチャットでご連絡ください。\nよろしくお願いします。", language="text")

elif page == "📚 YGシステム (無在庫)":
    st.markdown('<div class="main-header">📚 YGシステム (自動受注リスト)</div>', unsafe_allow_html=True)
    st.markdown("きよた書店のGmailから、最新のAmazonとメルカリShopsの注文を自動抽出しています。")
    
    with st.spinner('最新の注文メールを読み込んでいます...'):
        orders_df = get_recent_orders()
        
    if not orders_df.empty:
        st.success(f"最新の注文データを {len(orders_df)} 件 自動取得しました！")
        
        # DataFrameが空ではないが、特定の列が欠けている場合の対策
        for col in ["SKU", "数量", "商品名", "受信日時", "プラットフォーム", "🔗 八木リンク"]:
            if col not in orders_df.columns:
                orders_df[col] = ""
        
        import os
        import json
        STATUS_FILE = ".yg_order_status.json"  # 隠しファイルにしてStreamlitの監視対象から外す（これではじきを防止）
        
        status_dict = {}
        if os.path.exists(STATUS_FILE):
            with open(STATUS_FILE, "r", encoding="utf-8") as f:
                try:
                    status_dict = json.load(f)
                except:
                    pass
                    
        # 以前の巨大な isbn_sku_map.json はStreamlitエラーになるため、
        # 必要な SKU -> ISBN の紐付けだけを抽出した軽量な辞書ファイルを読み込む
        @st.cache_data(ttl=3600)
        def load_sku_isbn_map():
            import json, os
            sku_to_isbn = {}
            try:
                json_path = os.path.join(os.path.dirname(__file__), "sku_to_isbn.json")
                if os.path.exists(json_path):
                    with open(json_path, "r", encoding="utf-8") as f:
                        sku_to_isbn = json.load(f)
            except:
                pass
            return sku_to_isbn
            
        sku_to_isbn = load_sku_isbn_map()
        
        # チェック状態を保持するための列を用意
        orders_df["_id"] = orders_df["受信日時"] + "_" + orders_df["商品名"]
        orders_df["✅ 発注済"] = orders_df["_id"].map(lambda x: status_dict.get(x, False))
        
        # URL作成用関数 (ISBNがわかればそれを使う、わからなければクリーンな別名を使う)
        import urllib.parse
        import re
        def make_yagi_link(row):
            sku = row.get("SKU", "")
            isbn = sku_to_isbn.get(sku)
            if isbn:
                # ISBNがあれば100%ヒットする
                # URLパラメーターで optionselect:3 とすることで、上部のメイン検索窓にISBNを入れた状態で「ISBN」検索として処理されます
                return f"https://www.books-yagi.co.jp/bb/books/search/search_criteria:keyword_search/keyword:{isbn}/optionselect:3"
            
            # フォールバック：ISBNがない場合はタイトル検索
            # 余計な記号を省いて最初の単語だけにする（八木書店の検索システムへの対策）
            title = row.get("商品名", "")
            if not title:
                return ""
            
            clean = title.replace('「', ' ').replace('」', ' ')
            parts = re.split(r'[ 　：:\(（\-]', clean)
            parts = [p for p in parts if p.strip()]
            
            if parts:
                q = urllib.parse.quote(parts[0])
                return f"https://www.books-yagi.co.jp/bb/books/search/search_criteria:keyword_search/page:1/keyword:{q}"
                
            q = urllib.parse.quote(title.strip())
            return f"https://www.books-yagi.co.jp/bb/books/search/search_criteria:keyword_search/page:1/keyword:{q}"
            
        orders_df["🔗 八木リンク"] = orders_df.apply(make_yagi_link, axis=1)
        
        # --- 期間で絞り込み (八木発注の締め切り: 月曜8:30 / 木曜8:30) ---
        from datetime import datetime, timedelta, timezone

        def get_last_weekday(dt, target_weekday, hour=8, minute=30):
            days_ago = (dt.weekday() - target_weekday) % 7
            target = dt - timedelta(days=days_ago)
            target = target.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if target > dt:
                target -= timedelta(days=7)
            return target

        def get_next_weekday(dt, target_weekday, hour=8, minute=30):
            days_ahead = (target_weekday - dt.weekday()) % 7
            target = dt + timedelta(days=days_ahead)
            target = target.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if target <= dt:
                target += timedelta(days=7)
            return target

        JST = timezone(timedelta(hours=9))
        dt_now = datetime.now(JST)

        last_mon = get_last_weekday(dt_now, 0)
        last_thu = get_last_weekday(dt_now, 3)

        if last_mon > last_thu:
            # 現在は月曜8:30〜木曜8:30の間 (次は木曜締め)
            start_dt = get_last_weekday(dt_now, 6) # 前週の日曜
            end_dt = get_next_weekday(dt_now, 3)   # 今週の木曜
            period_str = f"{start_dt.strftime('%m/%d')} (日) 08:30 〜 {end_dt.strftime('%m/%d')} (木) 08:30"
        else:
            # 現在は木曜8:30〜月曜8:30の間 (次は月曜締め)
            start_dt = get_last_weekday(dt_now, 2) # その週の水曜
            end_dt = get_next_weekday(dt_now, 0)   # 次の月曜
            period_str = f"{start_dt.strftime('%m/%d')} (水) 08:30 〜 {end_dt.strftime('%m/%d')} (月) 08:30"

        orders_df['dt'] = pd.to_datetime(orders_df['受信日時'], format='%Y/%m/%d %H:%M', errors='coerce')
        orders_df['dt'] = orders_df['dt'].dt.tz_localize(JST)

        mask = (orders_df['dt'] >= start_dt) & (orders_df['dt'] <= end_dt) | orders_df['dt'].isna()
        filtered_df = orders_df[mask].copy()

        st.info(f"📅 現在の表示期間: **{period_str}**")

        # 画面表示用に並び替え (SKUをプラットフォームと商品名の間に追加、リンクも追加)
        view_cols = ["✅ 発注済", "受信日時", "プラットフォーム", "🔗 八木リンク", "SKU", "数量", "商品名"]
        
        import json, os
        STATUS_FILE = ".yg_order_status.json"
        
        # 毎回の読み込みでJSONから最新状態を取得する（セッションステートの固定は不要）
        status_dict = {}
        if os.path.exists(STATUS_FILE):
            try:
                with open(STATUS_FILE, "r", encoding="utf-8") as f:
                    status_dict = json.load(f)
            except:
                pass
        
        df = filtered_df[view_cols].copy()
        df["✅ 発注済"] = df.apply(lambda row: status_dict.get(f"{row['受信日時']}_{row['商品名']}", False), axis=1)
        
        st.markdown("<h3 style='color: #E32B36;'>⚠️ 【重要】チェック後の弾かれを完全に防ぐフォーム形式</h3>", unsafe_allow_html=True)
        st.markdown("👇 **チェックを入れてもすぐには裏で保存されません。ポンポン連続でチェックを入れて、最後に下の「💾 変更を確定する」ボタンを押してください💡**")
        st.info("※この枠組み（フォーム）の中でのクリックはシステム側と通信しないため、**絶対に弾かれたりカクついたりしません。**")

        with st.form("yg_order_form"):
            edited_df = st.data_editor(
                df,
                key="yg_orders_editor_form_final",
                column_config={
                    "✅ 発注済": st.column_config.CheckboxColumn("✅ 発注済", help="発注が終わったらチェック"),
                    "受信日時": st.column_config.TextColumn("受信日時", disabled=True),
                    "プラットフォーム": st.column_config.TextColumn("プラットフォーム", disabled=True),
                    "🔗 八木リンク": st.column_config.LinkColumn("🔗 八木リンク", help="八木書店のページを開く", display_text="発注ページへ", disabled=True),
                    "SKU": st.column_config.TextColumn("SKU", disabled=True),
                    "数量": st.column_config.TextColumn("数量", disabled=True),
                    "商品名": st.column_config.TextColumn("商品名", disabled=True),
                },
                hide_index=True,
                use_container_width=True,
                height=700,
            )
            
            # フォームの送信ボタン
            submit_btn = st.form_submit_button("💾 変更を確定する（カクつきゼロ👍）", type="primary", use_container_width=True)
            
            if submit_btn:
                # 確定されたときだけJSONを上書き保存する
                latest_status = {}
                if os.path.exists(STATUS_FILE):
                    try:
                        with open(STATUS_FILE, "r", encoding="utf-8") as f:
                            latest_status = json.load(f)
                    except:
                        pass
                        
                changed = False
                for index, row in edited_df.iterrows():
                    row_id = f"{row['受信日時']}_{row['商品名']}"
                    new_val = bool(row['✅ 発注済'])
                    if latest_status.get(row_id, False) != new_val:
                        latest_status[row_id] = new_val
                        changed = True
                        
                if changed:
                    with open(STATUS_FILE, "w", encoding="utf-8") as f:
                        json.dump(latest_status, f, ensure_ascii=False, indent=2)
                
                st.success("✅ チェック状態を保存しました！")
                st.rerun()
                
    else:
        st.info("直近100件のメールに新しい注文は見つかりませんでした。")

# elif page == " 未発送の注文 (Amazon)":
#     render_amazon_orders_page()

elif page == "📖 国内有在庫 (千葉・神田)":
    st.markdown('<div class="main-header">📖 国内有在庫 (千葉古書・神田)</div>', unsafe_allow_html=True)
    
    st.markdown("### 売上推移")
    sales_data = pd.DataFrame({"月": months, "売上": [150000, 180000, 120000, 220000, 300000]})
    fig = px.line(sales_data, x="月", y="売上", markers=True, color_discrete_sequence=["#10B981"])
    fig.update_traces(line=dict(width=3), marker=dict(size=8))
    st.plotly_chart(update_modern_layout(fig), use_container_width=True)
    
    st.markdown("### 未発送リスト")
    inventory_tasks = pd.DataFrame({
        "プラットフォーム": ["メルカリ", "Amazon", "ヤフオク", "メルカリ"],
        "書籍名": ["江戸名所図会", "医学大辞典", "浮世絵大全", "日本刀大鑑"],
        "保管場所": ["A棚-01", "C棚-05", "B棚-02", "A棚-03"],
        "ステータス": ["📦 梱包待ち", "🛒 ピッキング待ち", "📦 梱包待ち", "🛒 ピッキング待ち"]
    })
    st.dataframe(inventory_tasks, use_container_width=True)

elif page == "🌐 B28コマンド (越境プレ値)":
    st.markdown('<div class="main-header">🌐 B28コマンド (越境・超高利益)</div>', unsafe_allow_html=True)
    
    st.markdown("### 売上推移")
    sales_data = pd.DataFrame({"月": months, "売上": [2800000, 3500000, 3200000, 4800000, 5200000]})
    fig = px.area(sales_data, x="月", y="売上", color_discrete_sequence=["#8B5CF6"])
    st.plotly_chart(update_modern_layout(fig), use_container_width=True)
    
    st.markdown("### 未発送タスクリスト (JDM釣具 等)")
    b28_tasks = pd.DataFrame({
        "プラットフォーム": ["Shopee SG", "Shopee SG", "Shopee SG"],
        "商品名": ["Shimano Stella SW 18000HG", "Daiwa Saltiga 20000-H", "Gamakatsu Master Model II"],
        "想定利益 (JPY)": ["¥ 45,000", "¥ 52,000", "¥ 68,000"],
        "タスク": ["輸出インボイス作成", "DHL集荷予約", "パッキング（厳重）"],
        "ステータス": ["⚠️ 手配中", "🔴 未着手", "🟢 完了"]
    })
    st.dataframe(b28_tasks, use_container_width=True)
