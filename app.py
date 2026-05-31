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
import os

from amazon_orders import render_amazon_orders_page

# ページ設定
st.set_page_config(
    page_title="TRICK DROP", 
    page_icon="⚡️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# サイドバーのデフォルトのページナビゲーションを隠す
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {
            display: none;
        }
        /* モバイル環境でハンバーガーメニュー（>）を目立たせる */
        @media (max-width: 768px) {
            [data-testid="collapsedControl"] {
                background-color: #ff4b4b !important;
                border-radius: 50% !important;
                color: white !important;
                width: 48px !important;
                height: 48px !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                box-shadow: 0 4px 6px rgba(0,0,0,0.3) !important;
                top: 10px !important;
                left: 10px !important;
            }
            [data-testid="collapsedControl"] svg {
                width: 28px !important;
                height: 28px !important;
                fill: white !important;
            }
            .stApp > header {
                background-color: transparent !important;
            }
        }
        /* サイドバー上部の余白を限界まで削る */
        section[data-testid="stSidebar"] > div {
            padding-top: 0rem !important;
        }
        [data-testid="stSidebarUserContent"] {
            padding-top: 0rem !important;
            margin-top: -4rem !important; /* -2remから-4remに拡大して限界突破 */
        }
        /* ストリームリットのヘッダー領域（ここにスマホ用メニューボタンが存在する） */
        header[data-testid="stHeader"] {
            background: transparent !important;
        }
        /* メイン画面上部の余白を削る */
        .block-container {
            padding-top: 0rem !important;
            margin-top: -1.5rem !important; /* PC用 */
            padding-bottom: 0rem !important;
        }
        /* スマホ向けのレイアウト微調整（メニューボタンとコンテンツの被りを防ぐ） */
        @media (max-width: 768px) {
            .block-container {
                margin-top: 3.5rem !important; /* スマホでは司令室などのコンテンツを少し下げる */
            }
            header[data-testid="stHeader"] {
                background: white !important; /* メニューボタンを見やすくするために背景を白に */
                border-bottom: 1px solid #eee;
            }
            /* スマホでサイドバー内の「<<」ボタンにコンテンツが被って押せなくなる現象を解消 */
            [data-testid="stSidebarUserContent"] {
                margin-top: 0rem !important;
                padding-top: 1rem !important;
            }
        }
    </style>
""", unsafe_allow_html=True)

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
        
        # ダミー設定や日本語文字（非ASCII）による接続エラー(socket.gaierror, UnicodeEncodeError)を回避
        if "テスト" in user or "テスト" in password or "test" in server.lower():
            return None, "連携未設定（設定をお待ちしています）"
        try:
            user.encode('ascii')
            password.encode('ascii')
            server.encode('ascii')
        except UnicodeEncodeError:
            return None, "無効な文字が含まれています（連携未設定）"

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
    "📚 YGシステム (自動受注リスト)",
    "📦 未発送の注文 (Amazon)",
    "🎯 TRICK SHOOTER (出品ツール)",
    "⚙️ テンプレート管理",
    "⚡ TRICK RADAR",
]

# URLパラメータから現在のページを取得してデフォルト選択にする
default_index = 0
if "page" in st.query_params:
    try:
        default_index = pages.index(st.query_params["page"])
    except ValueError:
        pass

page = st.sidebar.radio("メニュー", pages, index=default_index, label_visibility="collapsed")

# 選択されたページをURLパラメータに保存（リロード対策）
st.query_params["page"] = page

st.sidebar.markdown("---")
st.sidebar.markdown("**🔗 クイックアクセス**")
st.sidebar.markdown("- [📦 Amazon Seller Central](https://sellercentral.amazon.co.jp/)")
st.sidebar.markdown("- [🛍️ メルカリShops](https://mercari-shops.com/seller/shops)")
st.sidebar.markdown("- [🛒 Qoo10（QSM）](https://qsm.qoo10.jp/gmkt.inc.gsm.web/default.aspx)")
st.sidebar.markdown("- [📚 日本の古本屋](https://www.kosho.or.jp/koshoadmin/)")
st.sidebar.markdown("- [🔨 ヤフオク!](https://auctions.yahoo.co.jp/my)")
st.sidebar.markdown("- [⚙️ AppTool](https://apptool.jp/mypage)")
st.sidebar.markdown("- [🔴 メルカリ](https://jp.mercari.com/)")
st.sidebar.markdown("- [📊 Amazon KDP レポート](https://kdpreports.amazon.co.jp/dashboard)")
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
        user = st.secrets.get("email", {}).get("gmail_kiyota_user", "テスト用")
        password = st.secrets.get("email", {}).get("gmail_kiyota_pass", "テスト用")
        server = "imap.gmail.com"
        
        # ダミー設定や日本語文字（非ASCII）による接続エラーを回避
        if "テスト" in user or "テスト" in password:
            return []  # 未設定時は空リストを返してエラーを回避
        try:
            user.encode('ascii')
            password.encode('ascii')
        except UnicodeEncodeError:
            return []

        mail = imaplib.IMAP4_SSL(server)
        mail.login(user, password)
        mail.select("inbox")
        
        # 過去60日分のメールIDをサーバー側で絞り込んで取得
        from datetime import datetime, timedelta
        search_date = (datetime.now() - timedelta(days=60)).strftime("%d-%b-%Y")
        status, response = mail.search(None, 'SINCE', search_date)
        
        if status == 'OK':
            email_ids = response[0].split()
            latest_ids = email_ids[-4000:]
            
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
                                if part.get_content_type() in ['text/plain', 'text/html']:
                                    body_bytes = part.get_payload(decode=True)
                                    if body_bytes:
                                        charset = part.get_content_charset() or 'utf-8'
                                        try:
                                            body += body_bytes.decode(charset, errors='ignore') + "\n"
                                        except:
                                            body += body_bytes.decode('utf-8', errors='ignore') + "\n"
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
                            if not re.search(r'[:\s]YG', subject) and 'YG' not in body:
                                continue
                                
                            # メール本文から「商品：」などで行を分割して複数商品（合わせ買い）をすべて抽出する
                            blocks = re.split(r'(?:商品|商品名)\s*(?:<[^>]*>\s*)*[:：]', body)
                            
                            # 万が一「商品：」で分割できなかった場合の救済措置
                            if len(blocks) <= 1:
                                blocks = ["", body]
                                
                            for block in blocks[1:]:
                                # SKUの抽出
                                sku_match = re.search(r'SKU(?:<[^>]*>)*[\s　]*(?:<[^>]*>)*[:：](?:<[^>]*>)*[\s　]*(?:<[^>]*>)*([A-Za-z0-9\-]+)', block)
                                if not sku_match:
                                    sku_match = re.search(r'(YG[A-Za-z0-9\-]+)', block)
                                    if not sku_match:
                                        # 件名からのフォールバック（分割できなかった単一注文などのため）
                                        sku_match_subj = re.search(r'(YG[A-Za-z0-9\-]+)', subject)
                                        if sku_match_subj and len(blocks) <= 2:
                                            sku = sku_match_subj.group(1).strip()
                                        else:
                                            continue
                                    else:
                                        sku = sku_match.group(1).strip()
                                else:
                                    sku = sku_match.group(1).strip()
                                    
                                if not sku.startswith('YG'):
                                    continue
                                
                                # 商品名の抽出 (ブロックの先頭)
                                product_name = ""
                                if len(blocks) > 1:
                                    p_match = re.match(r'[\s　]*(?:<[^>]*>)*([^\n\r<]+)', block)
                                    if p_match:
                                        product_name = p_match.group(1).strip()
                                        
                                if not product_name:
                                    # 以前のフォールバック
                                    p_match = re.search(r'(?:商品|商品名)\s*[:：]\s*([^\n\r]+)', body)
                                    if p_match:
                                        product_name = p_match.group(1).strip()
                                    else:
                                        product_name = subject
                                        if '注文確定' in product_name:
                                            product_name = product_name.split('注文確定')[-1]
                                            
                                # 商品名クリーニング
                                product_name = re.sub(r'^\s*[\-\:]?\s*出品者出荷のご注文\s*[\-\:]?\s*', '', product_name)
                                product_name = re.sub(r'^[\s:\-]*', '', product_name)
                                product_name = re.sub(r'^(?:SKU\s*[:\-]?\s*)?[A-Za-z0-9\-_]+\s+', '', product_name)
                                product_name = re.sub(r'\s*\[Tankobon.*', '', product_name, flags=re.IGNORECASE)
                                product_name = re.sub(r'\s*\[JP Oversized.*', '', product_name, flags=re.IGNORECASE)
                                product_name = re.sub(r'\s*\[(?:単行本|文庫|ペーパーバック|大型本|新書)\].*', '', product_name)
                                product_name = re.sub(r'\s*\((?:単行本|文庫|ペーパーバック|大型本|新書)\).*', '', product_name)
                                product_name = re.sub(r'^[:：\s]*(?:SKU)?[:：\s]*YG[A-Za-z0-9\-]+[\s:：\-]*', '', product_name, flags=re.IGNORECASE)
                                product_name = re.sub(r'^[:：\-\s]+', '', product_name).strip()
                                product_name = re.sub(r'<[^>]+>', '', product_name).strip()
                                
                                # 数量の抽出
                                qty_match = re.search(r'数\s*量(?:<[^>]*>|[^0-9])*?([0-9]+)', block)
                                if qty_match:
                                    quantity_val = int(qty_match.group(1))
                                    if quantity_val > 1:
                                        quantity_display = f"🚨 {quantity_val}冊"
                                    else:
                                        quantity_display = "1"
                                else:
                                    idx = block.find('数')
                                    if idx != -1:
                                        debug_text = block[idx:idx+40].replace('\n', ' ')
                                        quantity_display = f"⚠️ {debug_text}"
                                    else:
                                        quantity_display = "⚠️ 本文に'数'が存在しません"
                                        
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
                            if '発送をお願いします' in subject and 'メッセージ' not in subject:
                                if 'YG' not in body and '商品管理コード : YG' not in body:
                                    continue
                                    
                                # メルカリも複数商品を考慮して分割
                                blocks = re.split(r'(?:商品名)\s*(?:<[^>]*>\s*)*[:：]', body)
                                
                                if len(blocks) <= 1:
                                    blocks = ["", body]
                                    
                                for block in blocks[1:]:
                                    # SKUの抽出
                                    sku_match = re.search(r'(YG[A-Za-z0-9\-]+)', block)
                                    if not sku_match:
                                        if len(blocks) <= 2:
                                            sku_match = re.search(r'(YG[A-Za-z0-9\-]+)', body)
                                            if not sku_match:
                                                continue
                                        else:
                                            continue
                                            
                                    sku = sku_match.group(1).strip()
                                    if not sku.startswith('YG'):
                                        continue
                                        
                                    p_match = re.match(r'[\s　]*(?:<[^>]*>)*([^\n\r]+)', block)
                                    if p_match and len(blocks) > 1:
                                        product_name = p_match.group(1).strip()
                                    else:
                                        subj_match = re.search(r'「(.*?)」', subject)
                                        product_name = subj_match.group(1) if subj_match else subject.replace('【メルカリShops】', '')

                                    product_name = re.sub(r'<[^>]+>', '', product_name).strip()
                                    
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
    st.markdown('<div class="main-header">🎰 司令室</div>', unsafe_allow_html=True)
    st.markdown('<div class="slogan">TRICK DROP — 「ありえない成功を生み出す、仕掛けられた自販機」 ⚡️🎰</div>', unsafe_allow_html=True)
    
    # === バズ検知アラート機能 ===
    import pandas as pd
    from datetime import datetime, timedelta
    import os, json, glob

    now = datetime.now()
    threshold_time = now - timedelta(hours=48)
    threshold_30d = now - timedelta(days=30)
    threshold_60d = now - timedelta(days=60)
    
    with st.spinner("アラート用のデータを集計中..."):
        # 1. 実際の注文データを取得
        try:
            raw_orders_df = get_recent_orders()
            if not raw_orders_df.empty:
                raw_orders_df = raw_orders_df.drop_duplicates(subset=["受信日時", "SKU"], keep='first')
                raw_orders_df['受注日時'] = pd.to_datetime(raw_orders_df['受信日時'], format='%Y/%m/%d %H:%M', errors='coerce')
                
                # SKUからISBNをマッピング
                sku_to_isbn = {}
                json_path = os.path.join(os.path.dirname(__file__), "sku_to_isbn.json")
                if os.path.exists(json_path):
                    with open(json_path, "r", encoding="utf-8") as f:
                        sku_to_isbn = json.load(f)
                
                raw_orders_df['ISBN'] = raw_orders_df['SKU'].map(sku_to_isbn).fillna('')
                # 数量から数値のみを抽出（「🚨 2冊」などへの対応）、抽出できない場合は1とする
                raw_orders_df['販売数'] = raw_orders_df['数量'].astype(str).str.extract(r'(\d+)').astype(float).fillna(1).astype(int)
                
                # ISBNが存在するものに絞る
                valid_orders = raw_orders_df[raw_orders_df['ISBN'] != '']
                recent_orders = valid_orders[valid_orders['受注日時'] >= threshold_time]
                orders_30d = valid_orders[valid_orders['受注日時'] >= threshold_30d]
                orders_60d = valid_orders[valid_orders['受注日時'] >= threshold_60d]
            else:
                recent_orders = pd.DataFrame()
                orders_30d = pd.DataFrame()
                orders_60d = pd.DataFrame()
                valid_orders = pd.DataFrame()
        except Exception as e:
            recent_orders = pd.DataFrame()
            orders_30d = pd.DataFrame()
            orders_60d = pd.DataFrame()
            valid_orders = pd.DataFrame()
            st.warning("注文データの取得に失敗しました。")

        # 2. 最新の八木書店在庫データを取得
        yagi_df = pd.DataFrame()
        base_dir = os.path.dirname(os.path.abspath(__file__))
        try:
            # Yagiスクレイピング結果の json を探す (books_all_*.json または books_upload_*.json)
            json_files = glob.glob(os.path.join(base_dir, "books_all_*.json"))
            if not json_files:
                json_files = glob.glob(os.path.join(base_dir, "books_upload_*.json"))
                
            if not json_files:
                st.error(f"ファイルが見つかりません。探索先: {base_dir}")
                
            if json_files:
                latest_json = max(json_files, key=os.path.getctime)
                with open(latest_json, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        if "items" in data:
                            yagi_df = pd.DataFrame(data["items"])
                        elif "messages" in data:
                            yagi_df = pd.DataFrame(data["messages"])
                        else:
                            yagi_df = pd.DataFrame.from_dict(data, orient='index').reset_index(drop=True)
                    elif isinstance(data, list):
                        yagi_df = pd.DataFrame(data)
                        
                    if not yagi_df.empty:
                        if 'isbn' in yagi_df.columns:
                            yagi_df.rename(columns={'isbn': 'ISBN'}, inplace=True)
                        if 'stock' in yagi_df.columns:
                            yagi_df.rename(columns={'stock': '在庫数'}, inplace=True)
                            yagi_df['在庫数'] = pd.to_numeric(yagi_df['在庫数'], errors='coerce').fillna(0)
                        if 'ISBN' in yagi_df.columns:
                            # 共通の発注URLフォーマット
                            yagi_df['発注URL'] = yagi_df['ISBN'].apply(lambda x: f"https://www.books-yagi.co.jp/bb/books/search/search_criteria:keyword_search/keyword:{x}/optionselect:3")
        except Exception as e:
            st.error(f"ファイル読み込みエラー: {str(e)}")
            pass

    def isbn13_to_10(isbn13: str) -> str:
        """ISBN-13文字列をISBN-10(ASIN)に変換する。変換できない場合はそのまま返す"""
        isbn = str(isbn13).replace("-", "").strip()
        if len(isbn) != 13 or not isbn.startswith("978"):
            return isbn
        nine_digits = isbn[3:12]
        chk_sum = sum((10 - i) * int(nine_digits[i]) for i in range(9))
        chk_digit = 11 - (chk_sum % 11)
        if chk_digit == 10:
            chk_str = "X"
        elif chk_digit == 11:
            chk_str = "0"
        else:
            chk_str = str(chk_digit)
        return nine_digits + chk_str

    def get_latest_product_names(orders_df):
        # ISBNごとに最新の商品名を取得する
        # 同じISBNでも商品名がブレる場合があるため、最初の1件を採用する
        return orders_df.groupby('ISBN').first().reset_index()[['ISBN', '商品名']]

    SNOOZE_FILE = os.path.join(base_dir, "snooze_isbns.json")
    def get_snoozed_isbns():
        import json
        import time
        if os.path.exists(SNOOZE_FILE):
            try:
                with open(SNOOZE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                current_time = time.time()
                seven_days = 7 * 24 * 60 * 60
                active = {}
                ignored = set()
                for isbn, ts in data.items():
                    if current_time - float(ts) < seven_days:
                        active[isbn] = ts
                        ignored.add(isbn)
                if len(active) != len(data):
                    with open(SNOOZE_FILE, "w", encoding="utf-8") as f:
                        json.dump(active, f)
                return ignored
            except Exception:
                return set()
        return set()

    def add_snooze_isbn(isbn):
        import json
        import time
        data = {}
        if os.path.exists(SNOOZE_FILE):
            try:
                with open(SNOOZE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                pass
        data[isbn] = time.time()
        with open(SNOOZE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)

    ignored_isbns = get_snoozed_isbns()

    # --- アラート1: バズ検知判定ロジック ---
    alert_targets = pd.DataFrame()
    if not recent_orders.empty and not yagi_df.empty and 'ISBN' in recent_orders.columns and 'ISBN' in yagi_df.columns:
        order_counts = recent_orders.groupby('ISBN')['販売数'].sum().reset_index(name='受注件数')
        buzz_isbns = order_counts[order_counts['受注件数'] >= 2]
        
        # 見送りリストの除外
        if not buzz_isbns.empty:
            buzz_isbns = buzz_isbns[~buzz_isbns['ISBN'].isin(ignored_isbns)]
        
        if not buzz_isbns.empty:
            alert_targets = pd.merge(buzz_isbns, yagi_df, on='ISBN')
            if not alert_targets.empty and '在庫数' in alert_targets.columns:
                # 在庫数が 1以上、かつ20以下
                alert_targets = alert_targets[(alert_targets['在庫数'] >= 1) & (alert_targets['在庫数'] <= 20)]

    # --- UI表示1: バズ検知 ---
    st.markdown("### 🚨 緊急ハイジャック推奨（バズ商品）")
    if alert_targets.empty:
        st.write("現在、該当する商品はありません")
    else:
        for idx, row in alert_targets.iterrows():
            isbn = row['ISBN']
            product_name = recent_orders[recent_orders['ISBN'] == isbn].iloc[0]['商品名']
            count = row['受注件数']
            stock = int(row['在庫数'])
            url = row['発注URL']
            
            with st.container():
                st.error("🚨 **緊急バズ検知！全量買い占め推奨** 🚨")
                st.markdown(f"""
                - **商品名**: {product_name} (ISBN: {isbn})
                - **過去48時間の受注件数**: {count}件
                - **現在の八木書店在庫数**: 残り **{stock}** 冊
                """)
                asin = isbn13_to_10(isbn)
                amazon_url = f"https://www.amazon.co.jp/dp/{asin}"
                
                col1, col2, col3, _ = st.columns([2.2, 2.2, 1.8, 4])
                with col1:
                    st.markdown(f'<a href="{url}" target="_blank" style="display: block; padding: 6px 12px; background-color: #ff4b4b; color: white; border-radius: 4px; text-decoration: none; font-weight: bold; text-align: center; margin-bottom: 10px;">➔ 八木書店で買い占める</a>', unsafe_allow_html=True)
                with col2:
                    st.markdown(f'<a href="{amazon_url}" target="_blank" style="display: block; padding: 6px 12px; background-color: #f3a847; color: white; border-radius: 4px; text-decoration: none; font-weight: bold; text-align: center; margin-bottom: 10px;">➔ Amazonで確認</a>', unsafe_allow_html=True)
                with col3:
                    if st.button("⏳ 7日間見送り", key=f"snooze_alert1_{isbn}", use_container_width=True):
                        add_snooze_isbn(isbn)
                        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # --- アラート2: 予測型ハイジャック推奨（枯渇間近の刈り取り） ---
    st.markdown("### 🦅 予測型ハイジャック推奨（枯渇間近の刈り取り）")
    df_predictive = pd.DataFrame()
    if not orders_30d.empty and not yagi_df.empty:
        counts_30d_pred = orders_30d.groupby('ISBN')['販売数'].sum().reset_index(name='過去30日の販売数')
        counts_30d_pred = counts_30d_pred[counts_30d_pred['過去30日の販売数'] >= 2]
        
        # 見送りリストの除外
        if not counts_30d_pred.empty:
            counts_30d_pred = counts_30d_pred[~counts_30d_pred['ISBN'].isin(ignored_isbns)]
            
        if not counts_30d_pred.empty:
            df_predictive = pd.merge(counts_30d_pred, yagi_df, on='ISBN')
            if not df_predictive.empty:
                df_predictive = df_predictive[(df_predictive['在庫数'] >= 1) & (df_predictive['在庫数'] <= 11)]
                if not df_predictive.empty:
                    product_names = get_latest_product_names(orders_30d)
                    df_predictive = pd.merge(df_predictive, product_names, on='ISBN', how='left')
                    df_predictive['Amazonで確認'] = df_predictive['ISBN'].apply(lambda x: f"https://www.amazon.co.jp/dp/{isbn13_to_10(x)}")
                    df_predictive.rename(columns={'在庫数': '現在の八木在庫数'}, inplace=True)
                    df_predictive = df_predictive.sort_values(by='過去30日の販売数', ascending=False)
                    df_predictive = df_predictive[['ISBN', '商品名', '過去30日の販売数', '現在の八木在庫数', '発注URL', 'Amazonで確認']]

    if df_predictive.empty:
        st.write("現在、該当する商品はありません")
    else:
        for idx, row in df_predictive.iterrows():
            isbn = row['ISBN']
            product_name = row['商品名']
            count = row['過去30日の販売数']
            stock = int(row['現在の八木在庫数'])
            url = row['発注URL']
            
            with st.container():
                st.info("🦅 **枯渇間近！予測型ハイジャック推奨** 🦅")
                st.markdown(f"""
                - **商品名**: {product_name} (ISBN: {isbn})
                - **過去30日の販売数**: {count}件
                - **現在の八木書店在庫数**: 残り **{stock}** 冊
                """)
                asin = isbn13_to_10(isbn)
                amazon_url = f"https://www.amazon.co.jp/dp/{asin}"
                
                col1, col2, col3, _ = st.columns([2.2, 2.2, 1.8, 4])
                with col1:
                    st.markdown(f'<a href="{url}" target="_blank" style="display: block; padding: 6px 12px; background-color: #ff4b4b; color: white; border-radius: 4px; text-decoration: none; font-weight: bold; text-align: center; margin-bottom: 10px;">➔ 八木書店で買い占める</a>', unsafe_allow_html=True)
                with col2:
                    st.markdown(f'<a href="{amazon_url}" target="_blank" style="display: block; padding: 6px 12px; background-color: #f3a847; color: white; border-radius: 4px; text-decoration: none; font-weight: bold; text-align: center; margin-bottom: 10px;">➔ Amazonで確認</a>', unsafe_allow_html=True)
                with col3:
                    if st.button("⏳ 7日間見送り", key=f"snooze_pred_{isbn}", use_container_width=True):
                        add_snooze_isbn(isbn)
                        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # --- アラート3: 送料無料ライン突破・買い足し推奨（安全圏） ---
    st.markdown("### 🛒 送料無料ライン突破・買い足し推奨（安全圏）")
    df_restock = pd.DataFrame()
    if not orders_30d.empty and not yagi_df.empty:
        counts_30d = orders_30d.groupby('ISBN')['販売数'].sum().reset_index(name='過去30日の販売数')
        counts_30d = counts_30d[counts_30d['過去30日の販売数'] >= 3]
        
        if not counts_30d.empty:
            df_restock = pd.merge(counts_30d, yagi_df, on='ISBN')
            if not df_restock.empty:
                df_restock = df_restock[df_restock['在庫数'] >= 20]
                if not df_restock.empty:
                    product_names = get_latest_product_names(orders_30d)
                    df_restock = pd.merge(df_restock, product_names, on='ISBN', how='left')
                    df_restock['Amazonで確認'] = df_restock['ISBN'].apply(lambda x: f"https://www.amazon.co.jp/dp/{isbn13_to_10(x)}")
                    df_restock.rename(columns={'在庫数': '現在の八木在庫数'}, inplace=True)
                    df_restock = df_restock.sort_values(by='過去30日の販売数', ascending=False)
                    df_restock = df_restock[['商品名', '過去30日の販売数', '現在の八木在庫数', '発注URL', 'Amazonで確認']]

    if df_restock.empty:
        st.write("現在、該当する商品はありません")
    else:
        st.dataframe(
            df_restock,
            column_config={
                "発注URL": st.column_config.LinkColumn("発注リンク", display_text="発注画面へ"),
                "Amazonで確認": st.column_config.LinkColumn("Amazonで確認", display_text="Amazonへ")
            },
            hide_index=True,
            use_container_width=True
        )

elif page == "📚 YGシステム (自動受注リスト)":
    st.markdown('<div class="main-header">📚 YGシステム (自動受注リスト)</div>', unsafe_allow_html=True)
    st.markdown("きよた書店のGmailから、最新のAmazonとメルカリShopsの注文を自動抽出しています。")
    
    with st.spinner('最新の注文メールを読み込んでいます...'):
        orders_df = get_recent_orders()
        # text/plain と text/html の両方から抽出される重複を排除
        orders_df = orders_df.drop_duplicates(subset=["受信日時", "SKU"], keep='first')
        
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
        orders_df["_id"] = orders_df["受信日時"] + "_" + orders_df["SKU"]
        
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
            
        def make_amazon_link(row):
            sku = row.get("SKU", "")
            isbn = sku_to_isbn.get(sku)
            if isbn:
                try:
                    asin = isbn13_to_10(isbn)
                    return f"https://www.amazon.co.jp/dp/{asin}"
                except:
                    return f"https://www.amazon.co.jp/s?k={isbn}"
            
            title = row.get("商品名", "")
            if not title:
                return ""
            q = urllib.parse.quote(title.strip())
            return f"https://www.amazon.co.jp/s?k={q}"
            
        orders_df["🔗 八木リンク"] = orders_df.apply(make_yagi_link, axis=1)
        orders_df["🔗 Amazonリンク"] = orders_df.apply(make_amazon_link, axis=1)
        
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
        view_cols = ["✅ 発注済", "受信日時", "プラットフォーム", "🔗 八木リンク", "🔗 Amazonリンク", "SKU", "数量", "商品名"]
        
        # 受信日時の新しい順に降順ソート
        filtered_df = filtered_df.sort_values(by="dt", ascending=False)
        
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
        
        # まず✅ 発注済以外の列でdfを作成
        base_cols = [c for c in view_cols if c != "✅ 発注済" and c in filtered_df.columns]
        df = filtered_df[base_cols].copy()
        
        # チェック列を追加
        df.insert(0, "✅ 発注済", df.apply(lambda row: status_dict.get(f"{row['受信日時']}_{row['SKU']}", False), axis=1))
        
        # 並び替え
        missing_cols = [c for c in view_cols if c not in df.columns]
        for c in missing_cols:
            df[c] = ""
        df = df[view_cols]
        
        st.markdown("<h3 style='color: #E32B36;'>⚠️ 【重要】チェック後の弾かれを完全に防ぐフォーム形式</h3>", unsafe_allow_html=True)
        st.markdown("👇 **チェックを入れてもすぐには裏で保存されません。ポンポン連続でチェックを入れて、最後に下の「💾 変更を確定する」ボタンを押してください💡**")

        with st.form("yg_order_form"):
            edited_df = st.data_editor(
                df,
                key="yg_orders_editor_form_final",
                column_config={
                    "✅ 発注済": st.column_config.CheckboxColumn("✅ 発注済", help="発注が終わったらチェック"),
                    "受信日時": st.column_config.TextColumn("受信日時", disabled=True),
                    "プラットフォーム": st.column_config.TextColumn("プラットフォーム", disabled=True),
                    "🔗 八木リンク": st.column_config.LinkColumn("🔗 八木リンク", help="八木書店のページを開く", display_text="発注ページへ", disabled=True),
                    "🔗 Amazonリンク": st.column_config.LinkColumn("🔗 Amazonリンク", help="Amazonの検索/商品ページを開く", display_text="Amazonで確認", disabled=True),
                    "SKU": st.column_config.TextColumn("SKU", disabled=True),
                    "数量": st.column_config.TextColumn("数量", disabled=True),
                    "商品名": st.column_config.TextColumn("商品名", disabled=True),
                },
                hide_index=True,
                use_container_width=True,
                height=700,
            )
            
            # フォームの送信ボタン
            submit_btn = st.form_submit_button("💾 変更を確定する", type="primary", use_container_width=True)
            
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
                    row_id = f"{row['受信日時']}_{row['SKU']}"
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

elif page == "📦 未発送の注文 (Amazon)":
    render_amazon_orders_page()

elif page == "🎯 TRICK SHOOTER (出品ツール)":
    # 審査待ち制限を解除し、直接画面を埋め込み表示
    target_path = os.path.join(os.path.dirname(__file__), "pages", "trick_shooter.py")
    with open(target_path, encoding="utf-8") as f:
        code = f.read()
        # st.set_page_configが重複するとエラーになるため無効化
        code = code.replace('st.set_page_config', '# st.set_page_config')
        # 別ファイルとして定義されている変数との名前衝突を防ぎつつ実行
        exec(code, globals().copy())
elif page == "⚙️ テンプレート管理":
    target_path = os.path.join(os.path.dirname(__file__), "pages", "template_manager.py")
    with open(target_path, encoding="utf-8") as f:
        code = f.read()
        code = code.replace('st.set_page_config', '# st.set_page_config')
        exec(code, globals().copy())
elif page == "⚡ TRICK RADAR":
    import requests
    import math

    # スマホ向け：サイドバーを開くよう促す案内
    st.markdown("""
    <div style="background-color: #ffeaea; padding: 10px; border-radius: 5px; margin-bottom: 15px; font-size: 0.9em; display: flex; align-items: center; justify-content: space-between;">
        <span style="font-weight: bold; color: #d32f2f;">左上の 「 ＞ 」 ボタンからメニューが開けます⚡️</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-header">⚡ TRICK RADAR</div>', unsafe_allow_html=True)
    st.markdown("バーコードリーダーでISBNをスキャンしてください。")

    # APIキーの取得（Secretsからのセキュアな読み込み）
    try:
        keepa_api_key = st.secrets["KEEPA_API_KEY"]
    except KeyError:
        st.error("⚠️ `st.secrets['KEEPA_API_KEY']` が設定されていません。Streamlit CloudのSecretsまたはローカルの`.streamlit/secrets.toml`に設定を追加してください。")
        st.stop()

    # スマホUI向けカスタムCSS（巨大な結果表示かつトランクルームでの視認性向上）
    st.markdown("""
        <style>
        .radar-success {
            background-color: #4CAF50;
            color: white;
            padding: 30px 10px;
            border-radius: 12px;
            text-align: center;
            font-size: 8vw;
            font-weight: 900;
            line-height: 1.4;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.5);
            margin-top: 20px;
        }
        .radar-error {
            background-color: #e53935;
            color: white;
            padding: 30px 10px;
            border-radius: 12px;
            text-align: center;
            font-size: 8vw;
            font-weight: 900;
            line-height: 1.4;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.5);
            margin-top: 20px;
        }
        .radar-drops {
            font-size: 6vw;
            font-weight: bold;
            margin-top: 15px;
            background-color: rgba(0,0,0,0.2);
            padding: 5px;
            border-radius: 5px;
        }
        @media (min-width: 600px) {
            .radar-success, .radar-error { font-size: 40px; }
            .radar-drops { font-size: 24px; }
        }
        /* スキャン入力欄を大きくする設定 */
        [data-testid="stTextInput"] input {
            font-size: 24px !important;
            padding: 15px !important;
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)

    # フォームを利用することで、バーコードリーダー(Enterキー)での自動送信＆リセットを確実にする
    with st.form(key="radar_scan_form", clear_on_submit=True):
        isbn = st.text_input("ISBN", placeholder="スキャンしてください", label_visibility="collapsed", autocomplete="off")
        submitted = st.form_submit_button("検索（またはリーダーのEnter）", use_container_width=True)

    if submitted and isbn:
        url = "https://api.keepa.com/product"
        params = {
            "key": keepa_api_key,
            "domain": 5, # Amazon.co.jp
            "code": isbn.strip(),
            "stats": 90,
            "history": 0
        }
        
        with st.spinner("Keepa検索中..."):
            try:
                response = requests.get(url, params=params, timeout=10)
                
                # HTTPエラーのハンドリング
                if response.status_code != 200:
                    st.markdown('<div class="radar-error">API通信エラー<br>時間をおいて再試行してください</div>', unsafe_allow_html=True)
                else:
                    res_data = response.json()
                    
                    if "error" in res_data:
                        error_msg = res_data['error'].get('message', '不明なエラー')
                        st.markdown(f'<div class="radar-error">APIエラー<br><span style="font-size: 0.5em;">{error_msg}</span></div>', unsafe_allow_html=True)
                    elif "products" not in res_data or not res_data["products"]:
                        st.markdown('<div class="radar-error">商品が見つかりませんでした</div>', unsafe_allow_html=True)
                    else:
                        product = res_data["products"][0]
                        stats = product.get("stats", {})
                        
                        current_stats = stats.get("current", [])
                        used_price = current_stats[2] if len(current_stats) > 2 else -1
                        sales_rank_drops_90 = stats.get("salesRankDrops90", "不明")
                        
                        min_profit = 300 # ボスの最低希望利益
                        
                        if used_price == -1:
                            st.markdown(f'''
                                <div class="radar-error">
                                    在庫なし / 価格データなし
                                    <div class="radar-drops">直近90日間の売れ行き：{sales_rank_drops_90}回</div>
                                </div>
                            ''', unsafe_allow_html=True)
                        else:
                            # 上限仕入れ値の計算
                            max_purchase_price = math.floor(used_price - (used_price * 0.15) - 80 - 200 - min_profit)
                            
                            if max_purchase_price <= 0:
                                st.markdown(f'''
                                    <div class="radar-error">
                                        ゴミです。<br>仕入れ対象外
                                        <div class="radar-drops">直近90日間の売れ行き：{sales_rank_drops_90}回</div>
                                    </div>
                                ''', unsafe_allow_html=True)
                            else:
                                st.markdown(f'''
                                    <div class="radar-success">
                                        {max_purchase_price}円以下<br>なら買え！
                                        <div class="radar-drops">直近90日間の売れ行き：{sales_rank_drops_90}回</div>
                                    </div>
                                ''', unsafe_allow_html=True)
                                
            except Exception as e:
                st.markdown('<div class="radar-error">システムエラーが発生しました</div>', unsafe_allow_html=True)


