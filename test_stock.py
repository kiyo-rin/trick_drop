import pandas as pd
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import app

# Mock secrets to avoid issues
try:
    with open(".streamlit/secrets.toml", "r") as f:
        import toml
        config = toml.load(f)
except:
    config = {"email": {"gmail_kiyota_user": "dummy", "gmail_kiyota_pass": "dummy"}}
import streamlit as st
class SecretsMock:
    def __init__(self, d): self.d = d
    def __getitem__(self, key): return self.d[key]
    def __contains__(self, key): return key in self.d
st.secrets = SecretsMock(config)

df = app.get_recent_orders()
if df.empty:
    print("Empty DF...")
else:
    # Do exactly what app does
    df = df.drop_duplicates(subset=["受信日時", "SKU"], keep='first')
    df['受注日時'] = pd.to_datetime(df['受信日時'], format='%Y/%m/%d %H:%M', errors='coerce')
    
    sku_to_isbn = {}
    json_path = os.path.join(os.path.dirname(__file__), "sku_to_isbn.json")
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            sku_to_isbn = json.load(f)
    
    df['ISBN'] = df['SKU'].map(sku_to_isbn).fillna('')
    df['販売数'] = df['数量'].astype(str).str.extract(r'(\d+)').astype(float).fillna(1).astype(int)
    
    valid_orders = df[df['ISBN'] != '']
    print("Valid orders:", len(valid_orders))
    
    from datetime import datetime, timedelta
    now = datetime.now()
    orders_30d = valid_orders[valid_orders['受注日時'] >= now - timedelta(days=30)]
    counts_30d = orders_30d.groupby('ISBN')['販売数'].sum().reset_index(name='過去30日の販売数')
    print("Counts >= 3:")
    print(counts_30d[counts_30d['過去30日の販売数'] >= 3])

