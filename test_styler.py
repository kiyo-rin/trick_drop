import streamlit as st
import pandas as pd

def color_qty(val):
    if "冊" in str(val) and val != "1":
        return 'color: red; font-weight: bold;'
    return ''

df = pd.DataFrame({"数量": ["1", "2冊", "1", "3冊"]})
st.data_editor(df.style.map(color_qty))
