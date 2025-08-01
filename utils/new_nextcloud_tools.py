import os
import json
import streamlit as st
from webdav3.client import Client
import tempfile
import os
import base64
import io


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
def save_config(source_folder, working_folder):
    if not os.path.exists(".cache"):
        os.makedirs(".cache")
    config = {
        "source_folder": source_folder,
        "working_folder": working_folder
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

def verify_config(client):
    config = load_config()
    if config:
        working_folder = config.get("working_folder")
        source_folder = config.get("source_folder")
        if working_folder and source_folder:
            return source_folder, working_folder
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
    

def choose_remote_source_folder(defaut):
    with st.expander("📂 Dossier source Nextcloud", expanded=True):
        #default_folder = st.session_state.get("source_folder", defaut)
        source_folder = st.text_input("Chemin du dossier source", value=defaut)
        if st.button("✅ Valider le dossier source"):
            st.session_state.source_folder = source_folder
            st.success("✅ Dossier source sélectionné.")
    return st.session_state.get("source_folder")

def choose_remote_working_folder(defaut):
    with st.expander("📂 Dossier de travail Nextcloud", expanded=True):
        #default_folder = st.session_state.get("working_folder", "/")
        working_folder = st.text_input("Chemin du dossier de travail", value=defaut)
        if st.button("✅ Valider le dossier de travail"):
            st.session_state.working_folder = working_folder
            st.success("✅ Dossier de travail sélectionné.")
    return st.session_state.get("working_folder")

def list_and_select_pdf():
    client = st.session_state["client"]
    folder = st.session_state["source_folder"]

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
    client = st.session_state["client"]
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


def create_nested_subfolders_in_nextcloud(client, parent_folder: str, subfolder_paths: list):
    """
    Crée des sous-dossiers (y compris imbriqués) dans un dossier Nextcloud existant.

    Args:
        client (Client): Client WebDAV connecté.
        parent_folder (str): Dossier distant parent (ex: "/Marie/").
        subfolder_paths (list): Liste des chemins de sous-dossiers (ex: ["Data/2023", "Reports/Jan"]).
    """
    if not parent_folder.endswith("/"):
        parent_folder += "/"

    for path in subfolder_paths:
        full_path = os.path.join(parent_folder, path).replace("\\", "/")
        parts = full_path.strip("/").split("/")
        cumulative_path = "/"

        for part in parts:
            cumulative_path = os.path.join(cumulative_path, part).replace("\\", "/")
            if not cumulative_path.endswith("/"):
                cumulative_path += "/"

            try:
                if not client.check(cumulative_path):
                    client.mkdir(cumulative_path)
                    st.success(f"📁 Créé : {cumulative_path}")
                else:
                    st.info(f"ℹ️ Existe déjà : {cumulative_path}")
            except Exception as e:
                st.error(f"❌ Erreur création {cumulative_path} : {e}")



def list_remote_pdf_files(client, NEW_PDF, PROCESSED_PDF):
    client = st.session_state["client"]
    new_pdf = [f for f in client.list(NEW_PDF) if f.lower().endswith('.pdf')]
    processed_pdf = [f for f in client.list(PROCESSED_PDF) if f.lower().endswith('.pdf')]
    return new_pdf, processed_pdf


import os

def create_local_subfolders(base_local_folder: str, subfolder_paths: list):
    """
    Crée localement les sous-dossiers (y compris imbriqués) dans un dossier de base.

    Args:
        base_local_folder (str): Le chemin de base local (ex: ".cache").
        subfolder_paths (list): Liste de chemins relatifs des sous-dossiers (ex: ["Data/2023", "Reports/Jan"]).
    """
    for path in subfolder_paths:
        full_path = os.path.join(base_local_folder, path)
        try:
            os.makedirs(full_path, exist_ok=True)
            st.info(f"📁 Dossier local prêt : {full_path}")
        except Exception as e:
            st.error(f"❌ Erreur création locale {full_path} : {e}")

def download_pdf(client, remote_folder, file_name, local_subfolder):
    """
    Télécharge un PDF depuis Nextcloud dans le dossier .cache/IMPORTED_FOLDER et l'affiche.

    Args:
        client (Client): Instance WebDAV connectée.
        remote_folder (str): Chemin distant dans Nextcloud (ex: "/Marie/Londres_shared").
        file_name (str): Nom du fichier PDF (ex: "facture.pdf").
        local_subfolder (str): Nom du sous-dossier local dans .cache (par défaut "IMPORTED_FOLDER").
    """
    local_folder = os.path.join(".cache", local_subfolder)
    os.makedirs(local_folder, exist_ok=True)

    remote_path = f"{remote_folder.rstrip('/')}/{file_name}"
    local_path = os.path.join(local_folder, file_name)

    try:
        client.download_sync(remote_path=remote_path, local_path=local_path)
        st.success(f"📥 Fichier téléchargé : {file_name}")
    except Exception as e:
        st.error(f"❌ Erreur lors du téléchargement de {file_name} : {e}")



def copy_file_nextcloud(client, old_folder, new_folder, file_name):
    """
    Déplace un fichier sur Nextcloud d'un dossier à un autre.

    Args:
        client (Client): Instance WebDAV connectée.
        old_folder (str): Chemin du dossier source (ex: "/Marie/source").
        new_folder (str): Chemin du dossier destination (ex: "/Marie/destination").
        file_name (str): Nom du fichier à déplacer (ex: "document.pdf").
    """
    # Nettoyage des chemins
    old_path = f"{old_folder.rstrip('/')}/{file_name}"
    new_path = f"{new_folder.rstrip('/')}/{file_name}"

    try:
        # Vérifie si le dossier destination existe, sinon le crée
        if not client.check(new_folder.rstrip('/')):
            client.mkdir(new_folder.rstrip('/'))

        # Déplacement du fichier
        client.copy(remote_path_from=old_path, remote_path_to=new_path)
        st.success(f"📂 Fichier déplacé avec succès vers : {new_path}")
    except Exception as e:
        st.error(f"❌ Erreur lors du déplacement de {file_name} : {e}")



def save_df_to_nextcloud_csv(client, df, remote_folder, filename):
    """
    Enregistre un DataFrame CSV dans un dossier Nextcloud.

    Args:
        client (Client): Client WebDAV connecté.
        df (pd.DataFrame): Le DataFrame à sauvegarder.
        remote_folder (str): Dossier distant Nextcloud (ex: "/Marie/cache").
        filename (str): Nom du fichier (ex: "mon_fichier.csv").
    """
    remote_path = f"{remote_folder.rstrip('/')}/{filename}"

    try:
        # Crée un fichier CSV temporaire
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as tmp_file:
            df.to_csv(tmp_file.name, index=False)
            tmp_file_path = tmp_file.name

        # Crée le dossier distant s'il n'existe pas
        if not client.check(remote_folder.rstrip("/")):
            client.mkdir(remote_folder.rstrip("/"))

        # Upload du fichier temporaire vers Nextcloud
        client.upload_sync(remote_path=remote_path, local_path=tmp_file_path)
        st.success(f"✅ CSV enregistré dans Nextcloud : {remote_path}")

        # Nettoyage du fichier temporaire
        os.remove(tmp_file_path)

    except Exception as e:
        st.error(f"❌ Erreur lors de l'enregistrement du CSV : {e}")

