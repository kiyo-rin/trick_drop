import streamlit as st
import pandas as pd

st.markdown("""
<style>
.order-row {
    border-bottom: 1px solid #ddd;
    padding: 10px 0;
}
</style>
""", unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns([0.5, 2, 1, 3, 2])
col1.write("**選択**")
col2.write("**注文情報**")
col3.write("**画像**")
col4.write("**商品名**")
col5.write("**処理**")
st.markdown("---")

for i in range(3):
    c1, c2, c3, c4, c5 = st.columns([0.5, 2, 1, 3, 2])
    with c1:
        st.checkbox("", key=f"chk_{i}")
    with c2:
        st.markdown(f"2026-05-18 10:03<br>250-9803215<br>¥3,648", unsafe_allow_html=True)
    with c3:
        st.image("https://images-na.ssl-images-amazon.com/images/P/4096017287.09.MAIN._SCRM_.jpg", width=50)
    with c4:
        st.markdown(f"**【SKU】** YG12345<br>孤独の歴史 [Tankobon]", unsafe_allow_html=True)
    with c5:
        st.selectbox("配送", ["ヤマト", "日本郵便"], key=f"carrier_{i}")
        st.text_input("追跡番号", key=f"trk_{i}")
    st.markdown("---")
