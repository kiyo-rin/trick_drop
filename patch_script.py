import urllib.request
import base64

with open("icon_b64.txt", "r") as f:
    b64_data = f.read().strip()

snippet = f"""
import os
import streamlit as st

@st.cache_resource
def setup_apple_icon():
    try:
        # Streamlitのインストールパスを取得
        st_dir = os.path.dirname(st.__file__)
        index_path = os.path.join(st_dir, 'static', 'index.html')
        
        with open(index_path, 'r', encoding='utf-8') as f:
            html = f.read()

        if 'apple-touch-icon' not in html:
            b64_icon = "{b64_data}"
            tag = '<link rel="apple-touch-icon" href="data:image/png;base64,' + b64_icon + '">'
            # <head>タグの直後に追加
            new_html = html.replace('<head>', '<head>' + tag)
            
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(new_html)
    except Exception as e:
        print("Failed to patch index.html:", e)

setup_apple_icon()
"""
with open("patch.py", "w") as f:
    f.write(snippet)
