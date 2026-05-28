import streamlit as st
import pandas as pd

if "my_df" not in st.session_state:
    st.session_state.my_df = pd.DataFrame({"Select": [False, False], "Name": ["A", "B"]})

@st.fragment
def show_editor():
    edited = st.data_editor(st.session_state.my_df, key="my_editor_test")
    st.session_state.my_df = edited
    st.write(st.session_state.my_df)

show_editor()
