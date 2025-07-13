import os
import json
import streamlit as st
from webdav3.client import Client

CONFIG_PATH = ".cache/config_nextcloud.json"

# 🔐 Connexion à Nextcloud
def connect_to_nextcloud():
    if "expand_connect" not in st.session_state:
        st.session_state.expand_connect = True
    if "connect_validated" not in st.session_state:
        st.session_state.connect_validated = False

    with st.expander("🔐 Connexion à Nextcloud", expanded=st.session_state.expand_connect):
        default_url = st.session_state.get("webdav_url", "https://your-nextcloud-instance/remote.php/dav/files/username")
        webdav_url = st.text_input("🔗 URL WebDAV", value=default_url)
        username = st.text_input("👤 Nom d'utilisateur", value=st.session_state.get("username", ""))
        password = st.text_input("🔑 Mot de passe ou token d'application", type="password")

        if st.button("🔓 Se connecter"):
            options = {
                'webdav_hostname': webdav_url,
                'webdav_login': username,
                'webdav_password': password
            }
            client = Client(options)
            try:
                client.list()  # check root
                st.success("✅ Connexion réussie !")
                st.session_state.client = client
                st.session_state.webdav_url = webdav_url
                st.session_state.username = username
                st.session_state.connect_validated = True
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erreur de connexion : {e}")
                return None

    if st.session_state.get("connect_validated"):
        st.session_state.expand_connect = False
        return st.session_state.get("client")

    return None

# 📂 Choix du dossier distant (manuel)
def choose_remote_folder():
    if "expand_remote" not in st.session_state:
        st.session_state.expand_remote = True
    if "remote_validated" not in st.session_state:
        st.session_state.remote_validated = False

    with st.expander("📂 Dossier distant", expanded=st.session_state.expand_remote):
        default_folder = st.session_state.get("remote_folder", "/")
        remote_folder = st.text_input("📂 Chemin du dossier distant dans Nextcloud", value=default_folder)
        if st.button("✅ Valider le dossier distant"):
            st.session_state.remote_folder = remote_folder
            st.session_state.remote_validated = True
            st.rerun()

    if st.session_state.get("remote_validated"):
        st.session_state.expand_remote = False
    return st.session_state.get("remote_folder")

# 📁 Choix du dossier local (manuel)
def choose_local_folder():
    if "expand_local" not in st.session_state:
        st.session_state.expand_local = True
    if "local_validated" not in st.session_state:
        st.session_state.local_validated = False

    with st.expander("📁 Dossier local", expanded=st.session_state.expand_local):
        default_folder = st.session_state.get("local_folder", ".cache")
        local_folder = st.text_input("📁 Chemin du dossier local cible", value=default_folder)
        if st.button("✅ Valider le dossier local"):
            st.session_state.local_folder = local_folder
            st.session_state.local_validated = True
            st.rerun()

    if st.session_state.get("local_validated"):
        st.session_state.expand_local = False
    return st.session_state.get("local_folder")

# 🖫 Sauvegarde de la configuration
def save_config(nc_folder, local_folder):
    if not os.path.exists(".cache"):
        os.makedirs(".cache")
    config = {
        "nc_folder": nc_folder,
        "local_folder": local_folder
    }
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f)

# 🔠 Chargement de la configuration
def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return None

# 🔢 Liste les fichiers distants (hors dossiers)
def list_remote_files(client, folder):
    try:
        return [f for f in client.list(folder) if not f.endswith("/")]
    except Exception as e:
        st.error(f"Erreur lors de la lecture du dossier distant : {e}")
        return []

# 📅 Télécharger les fichiers manquants
def download_missing_files(client, nc_folder, local_folder):
    remote_files = list_remote_files(client, nc_folder)
    local_files = os.listdir(local_folder) if os.path.exists(local_folder) else []
    missing_files = [f for f in remote_files if f not in local_files]

    if not os.path.exists(local_folder):
        os.makedirs(local_folder)

    if not missing_files:
        st.info("✅ Tous les fichiers sont déjà téléchargés.")
    else:
        st.warning(f"⚠️ {len(missing_files)} fichier(s) manquant(s) à télécharger.")

    for f in missing_files:
        remote_path = f"{nc_folder.rstrip('/')}/{f}"
        local_path = os.path.join(local_folder, f)

        try:
            client.download_sync(remote_path=remote_path, local_path=local_path)
            st.success(f"📅 Téléchargé : {f}")
        except Exception as e:
            st.error(f"❌ Échec du téléchargement pour {f} : {e}")

# 🔍 Vérification et synchronisation depuis la config
def verify_config_and_sync(client):
    config = load_config()
    if config:
        nc_folder = config.get("nc_folder")
        local_folder = config.get("local_folder")
        if nc_folder and local_folder:
            st.info(f"🗂️ Utilisation des chemins enregistrés : {nc_folder} → {local_folder}")
            download_missing_files(client, nc_folder, local_folder)
            return nc_folder, local_folder
    return None, None
