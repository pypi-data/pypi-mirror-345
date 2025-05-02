import streamlit as st

bc = st.get_option("theme.backgroundColor")
tc = st.get_option("theme.textColor")

st.write(f"text color is {tc} with background color {bc}")
