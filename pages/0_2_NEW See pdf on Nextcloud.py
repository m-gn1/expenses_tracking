import streamlit as st
from utils.new_nextcloud_tools import (
    list_and_select_pdf,
    display_pdf_from_nextcloud)

st.title("📑 Visualiser PDF Nextcloud")


# ────────────── 🚀 APP STREAMLIT ──────────────

st.session_state.setdefault("selected_pdf", None)
st.session_state.setdefault("connect_validated", None)

if st.session_state["connect_validated"]:
    client = st.session_state["client"]
    st.info("🔓 Connecté à NextCloud")
    list_and_select_pdf()
    if st.session_state["selected_pdf"]:
        client = st.session_state["client"]
        display_pdf_from_nextcloud()
else:
    st.warning("⚠️ Connecte toi à NextCloud")
    st.page_link("pages/0_1_NEW Synchro NC cache working.py", label="🔐 Aller à la page de connexion")

