import streamlit as st
import pandas as pd
import subprocess
import json
import os
from datetime import datetime

# --- Page Config ---
st.set_page_config(page_title="ASO Pro Max Dashboard", page_icon="📈", layout="wide")

st.title("🚀 ASO Pro Max: End-to-End Optimization")
st.markdown(f"**Current Date:** {datetime.now().strftime('%Y-%m-%d')} | **Status:** 2026 Production Ready")

# --- Sidebar Controls ---
st.sidebar.header("Global Settings")
locale = st.sidebar.selectbox("Target Locale", ["us", "gb", "jp", "fr", "de", "es", "ar"])
keywords_input = st.sidebar.text_area("Keywords (comma separated)", "photo editor, ai headshot, portrait")
keyword_list = [k.strip() for k in keywords_input.split(",")]

# --- Tabs for Workflow ---
tab1, tab2, tab3, tab4 = st.tabs(["🔍 Market Research", "⚔️ Competitor Analysis", "🛡️ ASO Audit", "📝 Draft & Validate"])

# --- Tab 1: Market Research (Google Signals) ---
with tab1:
    st.header("Stage 1 & 3: Demand Signals")
    st.info("Fetches Google Suggest and Google Trends data to validate search volume.")
    
    if st.button("Fetch Demand Signals"):
        with st.spinner("Analyzing cross-platform demand..."):
            try:
                # Running the google_signals script
                cmd = ["python", "scripts/google_signals.py", "--geo", locale.upper(), "--keywords", ",".join(keyword_list)]
                result = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode("utf-8")
                st.code(result)
            except Exception as e:
                st.error(f"Error: {e}")

# --- Tab 2: Competitor Analysis (iTunes Search) ---
with tab2:
    st.header("Stage 2: Competitive Landscape")
    st.write("Detects the Top 5 competitors per keyword to find 'Function Match' gaps.")
    
    if st.button("Run Competitor Audit"):
        with st.spinner("Scraping iTunes Search API..."):
            try:
                cmd = ["python", "scripts/itunes_search_check.py", "--country", locale, "--keywords", ",".join(keyword_list)]
                result = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode("utf-8")
                st.markdown("### Competitive Rankings")
                st.code(result)
            except Exception as e:
                st.error(f"Error: {e}")

# --- Tab 3: ASO Audit (The Engine) ---
with tab3:
    st.header("Stage 5: Metadata Mechanical Audit")
    st.write("Checks for character budgets, stem overlaps, and CJK traps.")
    
    col1, col2 = st.columns(2)
    with col1:
        app_title = st.text_input("App Title", placeholder="Max 30 chars")
        subtitle = st.text_input("Subtitle", placeholder="Max 30 chars")
    with col2:
        keywords_field = st.text_area("Keywords Field", placeholder="Max 100 chars, comma separated")

    if st.button("Run Mechanical Audit"):
        # We simulate the aso_audit logic by creating a temporary snapshot
        mock_data = {
            "title": app_title,
            "subtitle": subtitle,
            "keywords": keywords_field,
            "locale": locale
        }
        with open("temp_audit.json", "w") as f:
            json.dump(mock_data, f)
            
        try:
            cmd = ["python", "scripts/aso_audit.py", "--from-file", "temp_audit.json"]
            result = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode("utf-8")
            st.success("Audit Complete")
            st.code(result)
        except Exception as e:
            st.error(f"Audit Script Error: {e}")

# --- Tab 4: Multi-Locale Strategy ---
with tab4:
    st.header("Golden Rules & Locale Pools")
    st.markdown("""
    ### 🛡️ The 6 Golden Rules
    1. **No Repetition:** Never repeat words between Title, Subtitle, and Keywords.
    2. **Fill the Budget:** Title ≥ 15, Subtitle ≥ 20, Keywords 95-100.
    3. **Locale Independence:** en-US and en-GB have different 100-char pools.
    4. **Avoid Transliteration Traps:** Don't use 'vintage' in Japan if volume is 0.
    5. **Caption Indexing:** (2026 Rule) Screenshot text is now searchable.
    6. **Function Match:** If users search for the keyword and would be disappointed, delete it.
    """)
    
    st.divider()
    st.subheader("Generate Locale Draft")
    if st.button("Generate .aso/context.md"):
        st.write("This would generate the Stage 2/3 outputs in your repo structure.")
        st.download_button("Download Draft Template", "## App Functions\n- Feature 1\n- Feature 2", file_name="context.md")
