import streamlit as st
from webdav3.client import Client
import tempfile
import os
import base64


def init_session():
    st.session_state.setdefault("connected", False)
    st.session_state.setdefault("selected_pdf", None)
    st.session_state.setdefault("webdav_options", None)
    st.session_state.setdefault("subfolder", "/")


def display_login_form():
    with st.expander("🔐 Connexion à Nextcloud", expanded=not st.session_state["connected"]):
        webdav_url = st.text_input("🔗 URL WebDAV", value="https://TON_NEXTCLOUD/remote.php/dav/files/ton_user/")
        username = st.text_input("👤 Nom d'utilisateur")
        password = st.text_input("🔑 Mot de passe ou token d'application", type="password")

        if st.button("🔓 Se connecter"):
            options = {
                'webdav_hostname': webdav_url,
                'webdav_login': username,
                'webdav_password': password
            }

            client = Client(options)
            try:
                client.list()  # Test connexion
                st.session_state["connected"] = True
                st.session_state["webdav_options"] = options
                st.success("✅ Connexion réussie !")
            except Exception as e:
                st.error(f"❌ Erreur de connexion : {e}")
                st.stop()


def choose_subfolder():
    st.markdown("### 📁 Sélectionner un sous-dossier")
    subfolder = st.text_input("📂 Entrez le chemin relatif du sous-dossier (ex: `2024/factures/`)", value=st.session_state["subfolder"])
    if st.button("📂 Accéder à ce sous-dossier"):
        st.session_state["subfolder"] = subfolder if subfolder.startswith("/") else f"/{subfolder}"
        st.session_state["selected_pdf"] = None  # Reset PDF selection
        st.rerun()


def list_and_select_pdf():
    client = Client(st.session_state["webdav_options"])
    folder = st.session_state["subfolder"]

    try:
        files = client.list(folder)
        pdf_files = [f for f in files if f.lower().endswith('.pdf')]

        if not pdf_files:
            st.warning("⚠️ Aucun fichier PDF trouvé dans ce sous-dossier.")
        else:
            selected_file = st.selectbox("📄 Choisis un fichier PDF :", pdf_files)
            if st.button("📥 Afficher le PDF sélectionné"):
                st.session_state["selected_pdf"] = os.path.join(folder, selected_file)
                st.rerun()
    except Exception as e:
        st.error(f"❌ Impossible d'accéder au sous-dossier : {e}")


def display_pdf_from_nextcloud():
    client = Client(st.session_state["webdav_options"])
    selected = st.session_state["selected_pdf"]

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        client.download_sync(remote_path=selected, local_path=tmp.name)
        with open(tmp.name, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode("utf-8")

    st.markdown("### 📄 Aperçu du PDF sélectionné")
    st.markdown(
        f"""
        <iframe 
            src="data:application/pdf;base64,{base64_pdf}" 
            width="100%" height="500px" 
            style="border:1px solid #ccc; border-radius:8px;"
        ></iframe>
        """,
        unsafe_allow_html=True
    )
    os.unlink(tmp.name)


# ────────────── 🚀 APP STREAMLIT ──────────────

init_session()
display_login_form()

if st.session_state["connected"]:
    choose_subfolder()
    list_and_select_pdf()

if st.session_state["selected_pdf"]:
    display_pdf_from_nextcloud()
