import pandas as pd
import json
import os
import streamlit as st

def get_orders():
    # just dummy to mock st.secrets
    return pd.DataFrame()

import app

df = app.get_recent_orders()
print("Total orders:", len(df))
if not df.empty:
    df['販売数'] = df['数量'].astype(str).str.extract(r'(\d+)').astype(float).fillna(1).astype(int)
    print("販売数 type:", df['販売数'].dtype)
    print(df[['販売数', '数量', '商品名']].head(10))

