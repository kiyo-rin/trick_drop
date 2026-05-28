import streamlit as st
import pandas as pd

df = pd.DataFrame({"テスト": ["1行目\n2行目\n3行目", "A\nB", "C"]})
styled_df = df.style.set_properties(**{'white-space': 'pre-wrap'})

st.data_editor(styled_df)
st.data_editor(df)
