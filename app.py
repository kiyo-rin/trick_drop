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
    "📚 YGシステム (自動受注リスト)"
    # "未発送の注文 (Amazon)",
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
                            if ('発送' in subject or '購入' in subject) and 'メッセージ' not in subject:
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
    st.markdown('<div class="main-header">🎰 司令室 (Command Center)</div>', unsafe_allow_html=True)
    st.markdown('<div class="slogan">TRICK DROP — 「ありえない成功を生み出す、仕掛けられた自販機」 ⚡️🎰</div>', unsafe_allow_html=True)
    
    # === バズ検知アラート機能 ===
    import pandas as pd
    from datetime import datetime, timedelta

    # (モックデータ生成: 実運用時は実際のDBやAPIから取得する想定)
    now = datetime.now()
    orders_df = pd.DataFrame([
        {'受注日時': now - timedelta(hours=2), 'ISBN': '9784001111111', '商品名': 'バズり本A'},
        {'受注日時': now - timedelta(hours=10), 'ISBN': '9784001111111', '商品名': 'バズり本A'},
        {'受注日時': now - timedelta(hours=5), 'ISBN': '9784112222222', '商品名': '普通の売れ筋B'},
    ])
    yagi_df = pd.DataFrame([
        {'ISBN': '9784001111111', '在庫数': 5, '発注URL': 'https://www.kosho.or.jp/products/list.php?mode=search&name=9784001111111'},
        {'ISBN': '9784112222222', '在庫数': 100, '発注URL': 'https://www.kosho.or.jp/products/list.php?mode=search&name=9784112222222'},
    ])
    
    # --- アラート判定ロジック ---
    threshold_time = now - timedelta(hours=48)
    recent_orders = orders_df[orders_df['受注日時'] >= threshold_time]
    
    if not recent_orders.empty:
        order_counts = recent_orders.groupby('ISBN').size().reset_index(name='受注件数')
        buzz_isbns = order_counts[order_counts['受注件数'] >= 2]
        
        # yagi_df とマージして在庫数を取得
        alert_targets = pd.merge(buzz_isbns, yagi_df, on='ISBN')
        
        # 在庫数が 1以上、かつ20以下
        alert_targets = alert_targets[(alert_targets['在庫数'] >= 1) & (alert_targets['在庫数'] <= 20)]
    else:
        alert_targets = pd.DataFrame()

    # --- UI表示 ---
    if alert_targets.empty:
        st.info("🚨 現在、緊急ハイジャック推奨のバズ商品はありません")
    else:
        for idx, row in alert_targets.iterrows():
            isbn = row['ISBN']
            product_name = recent_orders[recent_orders['ISBN'] == isbn].iloc[0]['商品名']
            count = row['受注件数']
            stock = row['在庫数']
            url = row['発注URL']
            
            with st.container():
                st.error("🚨 **緊急バズ検知！全量買い占め推奨** 🚨")
                st.markdown(f"""
                - **商品名**: {product_name} (ISBN: {isbn})
                - **過去48時間の受注件数**: {count}件
                - **現在の八木書店在庫数**: 残り **{stock}** 冊
                """)
                st.markdown(f'<a href="{url}" target="_blank" style="display: inline-block; padding: 8px 16px; background-color: #ff4b4b; color: white; border-radius: 4px; text-decoration: none; font-weight: bold; margin-bottom: 20px;">➔ 八木書店で買い占める</a>', unsafe_allow_html=True)
                
    st.markdown("---")

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

# elif page == " 未発送の注文 (Amazon)":
#     render_amazon_orders_page()

