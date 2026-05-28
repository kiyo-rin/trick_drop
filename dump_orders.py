import sys
import os
import toml
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mock streamlit st.secrets
class SecretsMock:
    def __init__(self, d):
        self.d = d
    def __getitem__(self, key):
        return self.d[key]
    def __contains__(self, key):
        return key in self.d

try:
    with open(".streamlit/secrets.toml", "r") as f:
        config = toml.load(f)
    print("Secrets loaded.")
except Exception as e:
    print("No secrets", e)
    config = {"email": {"gmail_kiyota_user": "dummy", "gmail_kiyota_pass": "dummy"}}

import streamlit as st
st.secrets = SecretsMock(config)

from app import get_recent_orders
df = get_recent_orders()
print("DF length:", len(df))
if not df.empty:
    df['販売数'] = df['数量'].astype(str).str.extract(r'(\d+)').astype(float).fillna(1).astype(int)
    print("head 10:")
    print(df[['数量', '販売数']].head(10))
    counts = df.groupby('SKU')['販売数'].sum().reset_index(name='count')
    print("Top sums:")
    print(counts.sort_values('count', ascending=False).head(10))
else:
    print("Empty DF")
