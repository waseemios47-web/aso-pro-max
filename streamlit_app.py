import streamlit as st
import pandas as pd
import subprocess
import json
import os
from datetime import datetime
import io

# --- Page Config ---
st.set_page_config(page_title="ASO Pro Max Dashboard", page_icon="🚀", layout="wide")

st.title("🚀 ASO Pro Max: End-to-End Optimization")
st.markdown(f"**Current Date:** {datetime.now().strftime('%Y-%m-%d')} | **Status:** 2026 Production Ready")

# --- Helper Function to Run Scripts Safely ---
def run_script(command_list):
    """Runs a terminal command and captures both success and error outputs gracefully."""
    result = subprocess.run(command_list, capture_output=True, text=True)
    if result.returncode != 0:
        st.error("⚠️ Script exited with an error.")
        st.code(result.stderr or result.stdout, language="bash")
        return False, None
    return True, result.stdout

# --- Sidebar Controls ---
st.sidebar.header("⚙️ Global Settings")
locale = st.sidebar.selectbox("Target Locale", ["us", "gb", "jp", "fr", "de", "es", "ar"])

st.sidebar.divider()
st.sidebar.subheader("Keyword Input")
input_method = st.sidebar.radio("Input Method", ["Manual Entry", "Bulk CSV Upload"])

keyword_list = []
if input_method == "Manual Entry":
    keywords_input = st.sidebar.text_area("Keywords (comma separated)", "photo editor, ai headshot, portrait")
    if keywords_input:
        keyword_list = [k.strip() for k in keywords_input.split(",") if k.strip()]
else:
    uploaded_file = st.sidebar.file_uploader("Upload CSV (must have a 'keyword' column)", type=["csv"])
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            if 'keyword' in df.columns:
                keyword_list = df['keyword'].dropna().astype(str).tolist()
                st.sidebar.success(f"Loaded {len(keyword_list)} keywords.")
            else:
                st.sidebar.error("CSV must contain a column named 'keyword'.")
        except Exception as e:
            st.sidebar.error(f"Error reading CSV: {e}")

# --- Tabs for Workflow ---
tab1, tab2, tab3, tab4 = st.tabs(["🔍 Market Research", "⚔️ Competitor Analysis", "🛡️ ASO Audit", "📝 Draft & Validate"])

# --- Tab 1: Market Research (Google Signals) ---
with tab1:
    st.header("Stage 1 & 3: Demand Signals")
    st.info("Fetches Google Suggest and Google Trends data to validate search volume.")
    
    if st.button("Fetch Demand Signals", type="primary"):
        if not keyword_list:
            st.warning("Please enter keywords in the sidebar first.")
        else:
            with st.spinner("Analyzing cross-platform demand (This may take a moment)..."):
                cmd = ["python", "scripts/google_signals.py", "--geo", locale.upper(), "--keywords", ",".join(keyword_list)]
                success, output = run_script(cmd)
                if success:
                    st.success("Analysis Complete!")
                    st.code(output, language="markdown")
                elif "429" in (output or "") or "rate limit" in (output or "").lower():
                    st.error("Google is blocking Streamlit's cloud IP address (Rate Limit). You may need to run this specific script locally.")

# --- Tab 2: Competitor Analysis (iTunes Search) ---
with tab2:
    st.header("Stage 2: Competitive Landscape")
    st.write("Detects the Top 5 competitors per keyword to find 'Function Match' gaps.")
    
    if st.button("Run Competitor Audit", type="primary"):
        if not keyword_list:
            st.warning("Please enter keywords in the sidebar first.")
        else:
            with st.spinner("Scraping iTunes Search API..."):
                cmd = ["python", "scripts/itunes_search_check.py", "--country", locale.lower(), "--keywords", ",".join(keyword_list)]
                success, output = run_script(cmd)
                if success:
                    st.markdown("### 🏆 Competitive Rankings")
                    st.code(output, language="markdown")

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

    if st.button("Run Mechanical Audit", type="primary"):
        if not app_title and not keywords_field:
            st.warning("Please fill in at least the Title or Keywords field.")
        else:
            # Create temporary snapshot for the audit script
            mock_data = {
                "title": app_title,
                "subtitle": subtitle,
                "keywords": keywords_field,
                "locale": locale.lower()
            }
            with open("temp_audit.json", "w") as f:
                json.dump(mock_data, f)
                
            with st.spinner("Running mechanical stem checks..."):
                cmd = ["python", "scripts/aso_audit.py", "--from-file", "temp_audit.json"]
                success, output = run_script(cmd)
                if success:
                    st.success("Audit Complete!")
                    st.code(output, language="markdown")

# --- Tab 4: Multi-Locale Strategy ---
with tab4:
    st.header("Golden Rules & Strategy")
    st.markdown("""
    ### 🛡️ The 6 Golden Rules
    1. **No Repetition:** Never repeat words between Title, Subtitle, and Keywords.
    2. **Character Budget:** Fill it entirely. Title ≥ 15, Subtitle ≥ 20, Keywords 95-100.
    3. **Locale Independence:** `en-US` and `en-GB` have different 100-char pools. Treat them as separate apps.
    4. **Avoid Transliteration Traps:** English words like 'vintage' often have zero search volume in CJK locales.
    5. **Caption Indexing:** Screenshot text is searchable on the 2026 App Store algorithm.
    6. **Function Match:** If users search your keyword and would be disappointed by your app's actual features, delete the keyword.
    """)
    
    st.divider()
    st.subheader("Generate Project Context Document")
    st.write("Download a template to map out your app's core functions before expanding to new locales.")
    
    template_content = """# App Context Boundary
## Core Functions
- [Feature 1]
- [Feature 2]

## Anti-Functions (What we are NOT)
- [Competitor Feature we don't have]
"""
    st.download_button(
        label="Download context.md Template",
        data=template_content,
        file_name="context.md",
        mime="text/markdown"
    )
