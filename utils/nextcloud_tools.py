import os
import json
import streamlit as st
from webdav3.client import Client

CONFIG_PATH = "config_nextcloud.json"

def connect_to_nextcloud():
    with st.expander("🔐 Connexion à Nextcloud", expanded=True):
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
            try:
                client = Client(options)
                client.list("/")  # Test connexion
                st.success("✅ Connexion réussie !")
                st.session_state.client = client
                st.session_state.webdav_url = webdav_url
                st.session_state.username = username
                return client
            except Exception as e:
                st.error(f"❌ Erreur de connexion : {e}")
    return st.session_state.get("client", None)


def choose_remote_source_folder():
    with st.expander("📂 Dossier source Nextcloud", expanded=True):
        default_folder = st.session_state.get("remote_source_folder", "/")
        remote_source_folder = st.text_input("Chemin du dossier source", value=default_folder)
        if st.button("✅ Valider le dossier source"):
            st.session_state.remote_source_folder = remote_source_folder
            st.success("✅ Dossier source sélectionné.")
    return st.session_state.get("remote_source_folder")

def choose_remote_working_folder():
    with st.expander("📂 Dossier de travail Nextcloud", expanded=True):
        default_folder = st.session_state.get("remote_working_folder", "/")
        remote_working_folder = st.text_input("Chemin du dossier de travail", value=default_folder)
        if st.button("✅ Valider le dossier de travail"):
            st.session_state.remote_working_folder = remote_working_folder
            st.success("✅ Dossier de travail sélectionné.")
    return st.session_state.get("remote_working_folder")


def choose_local_folder():
    with st.expander("📁 Dossier local de destination", expanded=True):
        default_folder = st.session_state.get("local_folder", os.getcwd())
        local_folder = st.text_input("Chemin du dossier local", value=default_folder)
        if st.button("✅ Valider le dossier local"):
            st.session_state.local_folder = local_folder
            st.success("✅ Dossier local sélectionné.")
    return st.session_state.get("local_folder")


def save_config(nc_folder, local_folder):
    config = {"nc_folder": nc_folder, "local_folder": local_folder}
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f)


def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return None


def list_remote_files(client, folder):
    try:
        files = client.list(folder)
        return [f.strip("/").split("/")[-1] for f in files if not f.endswith("/")]
    except Exception as e:
        st.error(f"Erreur lors de la lecture du dossier distant : {e}")
        return []


def download_missing_files(client, nc_folder, local_folder):
    remote_files = list_remote_files(client, nc_folder)
    if not remote_files:
        st.warning("⚠️ Aucun fichier trouvé dans le dossier distant.")
        return

    if not os.path.exists(local_folder):
        os.makedirs(local_folder)

    local_files = os.listdir(local_folder)
    missing_files = [f for f in remote_files if f not in local_files]

    if not missing_files:
        st.info("✅ Tous les fichiers sont déjà téléchargés.")
    else:
        st.warning(f"📥 {len(missing_files)} fichier(s) à télécharger.")
        for f in missing_files:
            remote_path = f"{nc_folder.rstrip('/')}/{f}"
            local_path = os.path.join(local_folder, f)
            try:
                client.download_sync(remote_path=remote_path, local_path=local_path)
                st.success(f"📄 Téléchargé : {f}")
            except Exception as e:
                st.error(f"❌ Erreur lors du téléchargement de {f} : {e}")


def verify_config_and_sync(client):
    config = load_config()
    if config:
        nc_folder = config.get("nc_folder")
        local_folder = config.get("local_folder")
        if nc_folder and local_folder:
            st.info(f"⚙️ Utilisation des chemins enregistrés : {nc_folder} → {local_folder}")
            download_missing_files(client, nc_folder, local_folder)
            return nc_folder, local_folder
    return None, None



def ensure_remote_folder_exists(client: Client, remote_path: str) -> bool:
    """
    Vérifie si un dossier distant Nextcloud existe, et le crée si besoin.

    Parameters:
    - client (Client): instance connectée de WebDAV.
    - remote_path (str): chemin distant (ex: "/Marie/fichiers").

    Returns:
    - bool: True si le dossier existe ou a été créé avec succès, False sinon.
    """
    try:
        if client.check(remote_path):
            st.info(f"📂 Le dossier distant existe déjà : {remote_path}")
            return True
        else:
            client.mkdir(remote_path)
            st.success(f"📁 Dossier distant créé : {remote_path}")
            return True
    except Exception as e:
        st.error(f"❌ Erreur lors de la vérification ou de la création du dossier distant : {e}")
        return False

