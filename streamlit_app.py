import streamlit as st
import subprocess

st.set_page_config(page_title="ASO Pro Max Online", page_icon="🚀")

st.title("🚀 ASO Pro Max Toolkit")
st.write("Run your App Store Optimization tools without any code!")

# Sidebar for inputs
st.sidebar.header("Settings")
keyword = st.sidebar.text_input("Enter Keyword", "wedding photo")
country = st.sidebar.text_input("Country Code (e.g., us, jp, gb)", "us")

# Action Buttons
if st.button("🔍 Check Google Search Signals"):
    with st.spinner("Talking to Google..."):
        # This runs the script just like we did in Colab
        result = subprocess.check_output(["python", "scripts/google_signals.py", "--geo", country.upper(), "--keywords", keyword])
        st.code(result.decode("utf-8"))

if st.button("🍎 Check iTunes Competition"):
    with st.spinner("Searching App Store..."):
        result = subprocess.check_output(["python", "scripts/itunes_search_check.py", "--country", country.lower(), "--keywords", keyword])
        st.code(result.decode("utf-8"))
