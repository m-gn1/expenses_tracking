import streamlit as st
from utils.new_nextcloud_tools import (
    list_and_select_pdf,
    display_pdf_from_nextcloud)

st.title("📑 Visualiser PDF Nextcloud")


LOCAL_ALL_PDF = "data/all_pdf/"
####### fonction ##########

import os
def list_and_select_pdf_local():
    client = st.session_state["client"]
    folder = st.session_state["source_folder"]
    local_dir = os.path.join(".cache/", LOCAL_ALL_PDF)


    try:
        files = client.list(folder)
        pdf_files = [f for f in files if f.lower().endswith('.pdf')]

        if not pdf_files:
            st.warning("⚠️ Aucun fichier PDF trouvé dans ce sous-dossier.")
        else:
            selected_file = st.selectbox("📄 Choisis un fichier PDF :", pdf_files)
            if st.button("📥 Afficher le PDF sélectionné"):
                # Téléchargement local
                remote_path = f"{folder.rstrip('/')}/{selected_file}"
                os.makedirs(local_dir, exist_ok=True)
                local_path = os.path.join(local_dir, selected_file)

                try:
                    client.download_sync(remote_path=remote_path, local_path=local_path)
                    st.session_state["selected_pdf_local"] = local_path
                    st.success("✅ PDF téléchargé")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Échec du téléchargement : {e}")
    except Exception as e:
        st.error(f"❌ Impossible d'accéder au sous-dossier : {e}")



import base64

import streamlit.components.v1 as components

def pdf_display_local(pdf_path):
    with open(pdf_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    components.iframe(
        src=f"data:application/pdf;base64,{base64_pdf}",
        width=700,
        height=800,
        scrolling=True
    )



# ────────────── 🚀 APP STREAMLIT ──────────────

st.session_state.setdefault("selected_pdf", None)
st.session_state.setdefault("connect_validated", None)

if st.session_state["connect_validated"]:
    client = st.session_state["client"]
    st.info("🔓 Connecté à NextCloud")
    list_and_select_pdf_local()
    if st.session_state["selected_pdf_local"]:
        #client = st.session_state["client"]
        pdf_display_local(st.session_state["selected_pdf_local"])
else:
    st.warning("⚠️ Connecte toi à NextCloud")
    st.page_link("pages/0_1_NEW Synchro NC cache working.py", label="🔐 Aller à la page de connexion")