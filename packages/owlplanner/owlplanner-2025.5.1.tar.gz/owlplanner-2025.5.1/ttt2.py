import streamlit as st
from streamlit_theme import st_theme

header = st.container()
with header:
    # Print the entire theme dictionary
    st.write("Getting theme settings...")

    # Get the current theme
    current_theme = st_theme()

if current_theme:
    print(current_theme)
else:
    print('Got none', current_theme)

# Check if the theme is dark or light
# if current_theme["isDark"]:
    # st.write("Current theme is dark")
# else:
    # st.write("Current theme is light")

# Print the entire theme dictionary
st.write("Current theme settings:", current_theme)
