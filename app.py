import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# ページ設定
st.set_page_config(page_title="TRICK DROP", page_icon="⚡️", layout="wide")

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
    "🏢 統合財務 (CFO)", 
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
st.sidebar.markdown("- [🔴 メルカリ](https://jp.mercari.com/)")
st.sidebar.markdown("- [✉️ Webメール (注文通知)](https://webmail.muumuu-domain.com/mail/INBOX)")
st.sidebar.markdown("- [🏷️ プライスター](https://jp3.pricetar.com/seller)")
st.sidebar.markdown("- [🖨️ ラベル屋さん](https://www.labelyasan.com/)")
st.sidebar.markdown("- [🔍 駿河屋あんしん買取](https://www.suruga-ya.jp/kaitori/search_buy?category=&search_word=)")

st.sidebar.markdown("---")
st.sidebar.markdown("**🛒 仕入れ先**")
st.sidebar.markdown("- [📖 八木書店バーゲンブック](https://www.books-yagi.co.jp/bb/)")
st.sidebar.markdown("- [🐟 魚住書店](https://www.uozumishoten.jp/cart.cgi)")
st.sidebar.markdown("- [🏢 三協社](http://book-sankyo.co.jp/)")

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

if page == "🏢 統合財務 (CFO)":
    st.markdown('<div class="main-header">🏢 統合財務総括 (CFO Dashboard)</div>', unsafe_allow_html=True)
    st.markdown('<div class="slogan">TRICK DROP — 「ありえない成功を生み出す、仕掛けられた自販機」 ⚡️🎰</div>', unsafe_allow_html=True)
    
    # KPI
    col1, col2, col3 = st.columns(3)
    col1.metric("今月の総売上", "¥12,500,000", "+15%")
    col2.metric("総粗利益", "¥6,800,000", "+18%")
    col3.metric("注文件数", "1,245件", "+5%")
    
    st.markdown("### 事業別 売上比率")
    pie_data = pd.DataFrame({
        "事業": ["YGシステム (無在庫)", "国内有在庫 (千葉・神田)", "B28コマンド (越境プレ値)"],
        "売上": [3500000, 1500000, 7500000]
    })
    fig = px.pie(pie_data, names="事業", values="売上", hole=0.5, color="事業",
                 color_discrete_map={
                     "YGシステム (無在庫)": "#3B82F6", 
                     "国内有在庫 (千葉・神田)": "#10B981", 
                     "B28コマンド (越境プレ値)": "#8B5CF6"
                 })
    fig.update_traces(
        marker=dict(line=dict(color='#FFFFFF', width=2)),
        pull=[0.02, 0.02, 0.02],
        hoverinfo="label+percent+name"
    )
    st.plotly_chart(update_modern_layout(fig), use_container_width=True)

elif page == "📚 YGシステム (無在庫)":
    st.markdown('<div class="main-header">📚 YGシステム (無在庫)</div>', unsafe_allow_html=True)
    
    st.markdown("### 売上推移")
    sales_data = pd.DataFrame({"月": months, "売上": [350000, 420000, 390000, 510000, 600000]})
    fig = px.bar(sales_data, x="月", y="売上", text="売上", color_discrete_sequence=["#3B82F6"])
    st.plotly_chart(update_modern_layout(fig), use_container_width=True)
    
    st.markdown("### 未発送リスト")
    yg_tasks = pd.DataFrame({
        "プラットフォーム": ["Amazon", "メルカリ", "日本の古本屋", "Yahoo!"],
        "書籍名": ["現代物理学の基礎", "スラムダンク全巻", "古文書学入門", "プログラミング大全"],
        "ISBN": ["978-4-00-111111-1", "978-4-08-222222-2", "978-4-12-333333-3", "978-4-77-444444-4"],
        "八木書店発注要否": ["🔴 要発注", "🟢 発注済", "🔴 要発注", "🟢 発注済"]
    })
    st.dataframe(yg_tasks, use_container_width=True)

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
