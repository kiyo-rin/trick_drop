import streamlit as st
from supabase import create_client, Client
import datetime

# ページ内独立実行用（app.pyからexecされた場合はスキップされる）
try:
    pass
    st.set_page_config(page_title="テンプレート管理", page_icon="⚙️", layout="wide")
except:
    pass

st.markdown('<div class="main-header">⚙️ テンプレート管理</div>', unsafe_allow_html=True)
st.markdown("AIリライト（Gemini）用の各プラットフォーム × コンディションごとのベーステンプレートを管理します。")

@st.cache_resource
def init_connection() -> Client:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

try:
    supabase = init_connection()
except Exception as e:
    st.error(f"Supabaseへの接続に失敗しました: {e}")
    st.stop()

# 利用可能なプラットフォームと状態の定義
PLATFORMS = ["Mercari", "Qoo10", "Furuhon"]
CONDITIONS = ["新品", "ほぼ新品", "非常に良い", "良い", "可/悪い"]

# 現在のテンプレートを取得
@st.cache_data(ttl=5) # 5秒キャッシュ
def get_templates():
    try:
        response = supabase.table("templates").select("*").execute()
        return response.data
    except Exception as e:
        st.error(f"テンプレート情報の取得に失敗しました: {e}")
        return []

templates_data = get_templates()

# 辞書形式に変換 (platform, condition) -> template_text
template_dict = {}
for t in templates_data:
    template_dict[(t["platform"], t["condition"])] = t["template_text"]

st.markdown("### テンプレートの編集")
st.info("💡 **ヒント:** プロンプト内で必ず置換される変数は以下の通りです。\n- {title} : 商品名\n- {condition} : 状態\n- {condition_note} : 特記事項（ユーザー入力）\nこれらを好きな位置に配置してください。")

col1, col2 = st.columns(2)
with col1:
    selected_platform = st.selectbox("プラットフォームを選択", PLATFORMS)
with col2:
    selected_condition = st.selectbox("状態を選択", CONDITIONS)

current_text = template_dict.get((selected_platform, selected_condition), "")

# デフォルトのテキスト（未設定の場合のガイド）
if not current_text:
    if selected_platform == "Mercari":
        current_text = "【商品名】: {title}\n【状態】: {condition}\n\n{condition_note}\n\nご質問がありましたらお気軽にお声掛けください。\n#古本 #中古本"
    elif selected_platform == "Qoo10":
        current_text = "■ 商品名\n{title}\n\n■ コンディション\n{condition}\n\n■ 状態詳細\n{condition_note}"
    else:
        current_text = "{title} / 状態: {condition} / {condition_note}"

new_text = st.text_area("テンプレート用の文章（プロンプトに渡されます）", value=current_text, height=300)

if st.button("このテンプレートを保存", type="primary"):
    with st.spinner("保存中..."):
        try:
            # 既存のものがあるかチェック（UPSERTの代わり）
            now = datetime.datetime.now().isoformat()
            data_to_save = {
                "platform": selected_platform,
                "condition": selected_condition,
                "template_text": new_text,
                "updated_at": now
            }
            
            # 存在チェック
            existing = supabase.table("templates").select("id").eq("platform", selected_platform).eq("condition", selected_condition).execute()
            
            if existing.data and len(existing.data) > 0:
                # Update
                res = supabase.table("templates").update(data_to_save).eq("id", existing.data[0]["id"]).execute()
            else:
                # Insert
                res = supabase.table("templates").insert(data_to_save).execute()
            
            st.success(f"✅ {selected_platform} の「{selected_condition}」テンプレートを保存しました！再読み込みします...")
            get_templates.clear()
            st.rerun()
                
        except Exception as e:
            st.error(f"保存エラー: {e}")

st.markdown("---")
st.markdown("### 登録済みテンプレート一覧")
if not templates_data:
    st.write("現在保存されているテンプレートはありません。すべてデフォルトの命令でAIが生成します。")
else:
    import pandas as pd
    df = pd.DataFrame(templates_data)
    if not df.empty:
        df = df[["platform", "condition", "updated_at", "template_text"]]
        df.columns = ["プラットフォーム", "状態", "最終更新", "テンプレート内容"]
        st.dataframe(df, use_container_width=True)
