from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components


BASE_DIR = Path(__file__).resolve().parent
HTML_FILE = BASE_DIR / "BOQ_price_finder.html"


st.set_page_config(
    page_title="BOQ Price Intelligence",
    layout="wide",
)

if not HTML_FILE.exists():
    st.error("BOQ_price_finder.html was not found in this repository.")
    st.stop()

html = HTML_FILE.read_text(encoding="utf-8")
components.html(html, height=920, scrolling=True)
