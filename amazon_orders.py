import streamlit as st
import pandas as pd
import datetime
from sp_api.api import Orders, CatalogItems
from sp_api.base import Marketplaces
import sys
import os

# To ensure the config is correctly imported
sys.path.append(os.path.abspath('.'))
try:
    from exports.amazon_sp_api_config import SP_API_CONFIG
except ImportError:
    # Streamlit Cloud (デプロイ環境) では st.secrets を使用する
    SP_API_CONFIG = {
        'refresh_token': st.secrets.get("SP_API_REFRESH_TOKEN", ""),
        'lwa_app_id': st.secrets.get("SP_API_LWA_APP_ID", ""),
        'lwa_client_secret': st.secrets.get("SP_API_LWA_CLIENT_SECRET", ""),
        'aws_access_key': st.secrets.get("SP_API_AWS_ACCESS_KEY", ""),
        'aws_secret_key': st.secrets.get("SP_API_AWS_SECRET_KEY", ""),
        'role_arn': st.secrets.get("SP_API_ROLE_ARN", ""), 
        'seller_id': st.secrets.get("SP_API_SELLER_ID", "")
    }

@st.cache_data(ttl=300)
def fetch_unshipped_orders():
    """SP-APIから未発送の注文を取得する"""
    try:
        orders_api = Orders(credentials=SP_API_CONFIG, marketplace=Marketplaces.JP)
        # 過去30日間の未発送の注文を取得
        created_after = (datetime.datetime.now() - datetime.timedelta(days=30)).isoformat()
        
        res = orders_api.get_orders(CreatedAfter=created_after, OrderStatuses=["Unshipped", "PartiallyShipped"])
        catalog_api = CatalogItems(credentials=SP_API_CONFIG, marketplace=Marketplaces.JP)
        asin_img_cache = {}
        orders = res.payload.get("Orders", [])
        
        result = []
        for order in orders:
            order_id = order.get("AmazonOrderId")
            shipping = order.get("ShippingAddress", {})
            purchase_date = order.get("PurchaseDate")
            # ISO format から datetime へ変換して表示を見やすく
            if purchase_date:
                try:
                    dt = datetime.datetime.fromisoformat(purchase_date.replace("Z", "+00:00"))
                    # JSTに変換
                    dt_jst = dt.astimezone(datetime.timezone(datetime.timedelta(hours=9)))
                    purchase_date = dt_jst.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    pass
            
            # アイテム情報を取得
            items_res = orders_api.get_order_items(order_id)
            items = items_res.payload.get("OrderItems", [])
            
            for item in items:
                asin = item.get("ASIN", "")
                # Book cover image URL formula
                img_url = ""
                if asin:
                    if asin in asin_img_cache:
                        img_url = asin_img_cache[asin]
                    else:
                        try:
                            cat_res = catalog_api.get_catalog_item(asin, includedData=["images"])
                            images_payload = cat_res.payload.get("images", [])
                            if images_payload and len(images_payload) > 0:
                                img_list = images_payload[0].get("images", [])
                                if img_list:
                                    # 一番小さい画像や適度なサイズの画像が欲しい場合もあるがとりあえず1つ目
                                    img_url = img_list[0].get("link", "")
                        except Exception:
                            pass
                        
                        # Fallback
                        if not img_url:
                            img_url = "https://dummyimage.com/70x100/eeeeee/999999.png&text=No+Image"
                        asin_img_cache[asin] = img_url
                
                raw_qty_str = item.get("QuantityOrdered", "1")
                
                # --- 【テスト用】1件目の注文を強制的に「2冊」にする ---
                if len(result) == 0:
                    raw_qty_str = "2"
                # ----------------------------------------------------
                
                try:
                    raw_qty = int(raw_qty_str)
                    qty_display = f"{raw_qty}冊" if raw_qty > 1 else str(raw_qty)
                except (ValueError, TypeError):
                    qty_display = str(raw_qty_str)
                
                address1 = shipping.get('StateOrRegion', '') + shipping.get('AddressLine1', '')
                address2 = shipping.get('AddressLine2', '')
                addr_lines = [f"〒{shipping.get('PostalCode', '')}"]
                if address1: addr_lines.append(address1)
                if address2: addr_lines.append(address2)
                addr_lines.append(f"{shipping.get('Name', '')} 様")
                customer_info = "\n".join(addr_lines)
                
                short_date = purchase_date[:16] if purchase_date else "" # 2026-05-18 10:03
                price = item.get('ItemPrice', {}).get('Amount', '0')
                sku = item.get('SellerSKU', '')
                
                result.append({
                    "選択": False,
                    "注文詳細": f"{short_date}\n{order_id}\n¥{price}",
                    "画像": img_url,
                    "商品名": f"【SKU】{sku}\n{item.get('Title', '')}",
                    "数量": qty_display,
                    "お届け先": customer_info,
                    "配送": "ヤマト",
                    "追跡番号": "",
                    "_order_id": order_id, # 内部処理用
                })
        return result, None
    except Exception as e:
        return [], str(e)

def render_amazon_orders_page():
    st.markdown("<h2 class='main-header'>📦 未発送の注文 (Amazon)</h2>", unsafe_allow_html=True)
    st.write("Amazon SP-APIから「未発送」の注文を自動取得して表示します。")
    
    with st.spinner("Amazon SP-APIと通信しています..."):
        orders_data, error = fetch_unshipped_orders()
        
    if error:
        st.error(f"データの取得に失敗しました: {error}")
        return
        
    if not orders_data:
        st.success("🎉 現在、未発送の注文はありません！")
        return
        
    df = pd.DataFrame(orders_data)
    
    # 画像を表示しつつ、チェックボックスを左端に置く設定
    st.markdown("### 📋 注文一覧")
    
    # 選択や一括処理などのボタンを配置
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("✈️ 選択した注文を発送済みにする", use_container_width=True):
            st.info("※ フェーズ2で発送通知(Feeds API等)を実装します！")
            
    st.write("")
    
    # 完全にプライスター風の「複数行対応」リストUIを columns で手作りする
    h0, h1, h2, h3, h4, h5 = st.columns([0.5, 1.5, 1, 3, 2.5, 2])
    h0.write("**選択**")
    h1.write("**注文詳細**")
    h2.write("**商品**")
    h3.write("**SKU・商品名 / 数量**")
    h4.write("**お届け先**")
    h5.write("**マケプレ配送 (ヤマト)**")
    st.markdown("<hr style='margin: 0;'>", unsafe_allow_html=True)

    for i, row in enumerate(orders_data):
        c0, c1, c2, c3, c4, c5 = st.columns([0.5, 1.5, 1, 3, 2.5, 2])
        
        with c0:
            st.checkbox(" ", key=f"chk_{row['_order_id']}_{i}", label_visibility="collapsed")
            
        with c1:
            st.markdown(f"<div style='font-size: 0.85em; line-height: 1.6;'>{row['注文詳細'].replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
            
        with c2:
            if row["画像"]:
                st.image(row["画像"], width=70)
                
        with c3:
            # 数量のアラート強調
            qty_val = row["数量"]
            if "冊" in qty_val and qty_val != "1冊":
                qty_html = f"<span style='color:#ff4b4b; font-weight:bold; font-size:1.1em; background:#ffefef; padding:4px 8px; border: 1px solid #ff4b4b; border-radius: 4px;'>数量: {qty_val}</span>"
            else:
                qty_html = f"<b>数量:</b> {qty_val}"
                
            st.markdown(f"<div style='font-size: 0.9em; line-height: 1.4; margin-bottom: 5px;'>{row['商品名'].replace(chr(10), '<br>')}</div>{qty_html}", unsafe_allow_html=True)
        with c4:
            st.markdown(f"<div style='font-size: 0.85em; line-height: 1.5;'>{row['お届け先'].replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
            
        with c5:
            # マケプレ配送（ヤマト契約）用の梱包サイズリスト
            shipping_sizes = [
                "ネコポス", "宅急便コンパクト", "宅急便60サイズ", 
                "宅急便80サイズ", "宅急便100サイズ", "宅急便120サイズ",
                "宅急便140サイズ", "宅急便160サイズ", "宅急便180サイズ", "宅急便200サイズ"
            ]
            st.selectbox("梱包サイズ", shipping_sizes, key=f"size_{row['_order_id']}_{i}", label_visibility="collapsed")
            
            st.markdown("<div style='font-size:0.75em; color:#007185; text-align:center; padding-bottom:5px; cursor:pointer;'>商品サイズから推定して梱包サイズを入力</div>", unsafe_allow_html=True)
            
            if st.button("マケプレ配送を申し込む", key=f"btn_mplace_{row['_order_id']}_{i}", use_container_width=True, type="secondary"):
                st.toast(f"フェーズ2で {row['_order_id']} のラベル購入(Merchant Fulfillment API)を実行します！", icon="📦")
            
        st.markdown("<hr style='margin: 15px 0; border: 0; border-top: 1px solid #EEE;'>", unsafe_allow_html=True)

    # 選択状況のカウント
    selected_count = sum(1 for i, row in enumerate(orders_data) if st.session_state.get(f"chk_{row['_order_id']}_{i}", False))
    if selected_count > 0:
        st.success(f"☑️ 現在 {selected_count} 件の注文が選択されています。")
