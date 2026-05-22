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
page = st.sidebar.radio("", [
    "🚨 司令室 (メイン)", 
    "📚 YGシステム (無在庫)", 
    "📖 国内有在庫 (千葉・神田)", 
    "🌐 B28コマンド (越境プレ値)"
])

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
        
        # すべてのメールから最新300件のIDを取得 (取得件数を増やしました)
        status, response = mail.search(None, 'ALL')
        if status == 'OK':
            email_ids = response[0].split()
            latest_ids = email_ids[-300:]  # 最新300件を取得
            
            for e_id in reversed(latest_ids):
                status, data = mail.fetch(e_id, '(RFC822)')
                if status != 'OK': continue
                
                raw_email = data[0][1]
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
                    formatted_date = dt.strftime('%Y/%m/%d %H:%M')
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
                        
                    # 件名から商品名を抽出 (例: 注文確定 : SKU 商品名 [Tankobon...)
                    # "]" や SKU の後の部分を抽出する簡易ロジック
                    parts = subject.split(' ', 3)
                    product_name = parts[-1] if len(parts) > 3 else subject
                    
                    orders.append({
                        "受信日時": formatted_date,
                        "プラットフォーム": "📦 Amazon",
                        "商品名": product_name,
                        "ステータス": "🔴 未発注_八木"
                    })
                    
                # ② メルカリShopsの注文判定
                elif '【メルカリShops】' in subject:
                    # 「発送」または「購入」が含まれ、かつ「メッセージ」ではないものを注文とする
                    if ('発送' in subject or '購入' in subject) and 'メッセージ' not in subject:
                        # YGから始まる商品管理コードのみ対象とする
                        if 'YG' not in body and '商品管理コード : YG' not in body:
                            continue
                            
                        # 件名から「商品名」を抽出 (例: 【メルカリShops】「〇〇〇」が購入されました)
                        match = re.search(r'「(.*?)」', subject)
                        product_name = match.group(1) if match else subject.replace('【メルカリShops】', '')
                        
                        orders.append({
                            "受信日時": formatted_date,
                            "プラットフォーム": "🔴 メルカリShops",
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

if page == "🚨 司令室 (メイン)":
    st.markdown('<div class="main-header">🚨 司令室 (Command Center)</div>', unsafe_allow_html=True)
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
        
        import os
        import json
        STATUS_FILE = "yg_order_status.json"
        
        status_dict = {}
        if os.path.exists(STATUS_FILE):
            with open(STATUS_FILE, "r", encoding="utf-8") as f:
                try:
                    status_dict = json.load(f)
                except:
                    pass
                    
        # チェック状態を保持するための列を用意
        orders_df["_id"] = orders_df["受信日時"] + "_" + orders_df["商品名"]
        orders_df["✅ 発注済"] = orders_df["_id"].map(lambda x: status_dict.get(x, False))
        
        # 画面表示用に並び替え
        view_cols = ["✅ 発注済", "受信日時", "プラットフォーム", "商品名"]
        view_df = orders_df[view_cols]
        
        st.markdown("👇 **チェックボックスをクリックすると、自動で「発注済み」として記録されます💡**")
        edited_df = st.data_editor(
            view_df,
            column_config={
                "✅ 発注済": st.column_config.CheckboxColumn("✅ 発注済", help="発注が終わったらチェック", default=False),
                "受信日時": st.column_config.TextColumn("受信日時", disabled=True),
                "プラットフォーム": st.column_config.TextColumn("プラットフォーム", disabled=True),
                "商品名": st.column_config.TextColumn("商品名", disabled=True),
            },
            hide_index=True,
            use_container_width=True,
            height=700  # 一覧を下まで伸ばす
        )
        
        # 変更があればJSONに保存
        new_status_dict = status_dict.copy()
        for index, row in edited_df.iterrows():
            row_id = f"{row['受信日時']}_{row['商品名']}"
            new_status_dict[row_id] = row['✅ 発注済']
            
        if new_status_dict != status_dict:
            with open(STATUS_FILE, "w", encoding="utf-8") as f:
                json.dump(new_status_dict, f, ensure_ascii=False, indent=2)
                
    else:
        st.info("直近100件のメールに新しい注文は見つかりませんでした。")

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
