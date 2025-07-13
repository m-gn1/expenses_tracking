import os
import streamlit as st
from webdav3.client import Client

def sync_from_nextcloud_to_server(client: Client, remote_folder: str, local_folder: str = "./data"):
    """
    Synchronise les fichiers du dossier distant Nextcloud vers un dossier local (sur le serveur Streamlit).
    - Crée le dossier local si besoin
    - Télécharge uniquement les fichiers manquants
    """

    # Créer le dossier local s’il n’existe pas
    os.makedirs(local_folder, exist_ok=True)

    # Lister les fichiers dans Nextcloud
    try:
        remote_items = client.list(remote_folder)
        remote_files = [f for f in remote_items if not f.endswith("/")]
    except Exception as e:
        st.error(f"❌ Erreur lors de la lecture du dossier distant : {e}")
        return

    # Lister les fichiers déjà présents localement
    local_files = os.listdir(local_folder)
    downloaded_count = 0
    missing_files = [f for f in remote_files if f not in local_files]

    if not missing_files:
        st.info("✅ Tous les fichiers sont déjà présents localement.")
    else:
        st.warning(f"⬇️ Téléchargement de {len(missing_files)} fichier(s) manquant(s) dans {local_folder}...")

    # Télécharger les fichiers manquants
    for filename in missing_files:
        remote_path = f"{remote_folder.rstrip('/')}/{filename}"
        local_path = os.path.join(local_folder, os.path.basename(filename))
        try:
            client.download_sync(remote_path=remote_path, local_path=local_path)
            st.success(f"📥 Téléchargé : {filename}")
            downloaded_count += 1
        except Exception as e:
            st.error(f"❌ Échec pour {filename} : {e}")

    if downloaded_count > 0:
        st.success(f"🎉 {downloaded_count} fichier(s) téléchargé(s) avec succès.")
