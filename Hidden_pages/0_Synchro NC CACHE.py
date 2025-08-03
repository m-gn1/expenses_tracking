
import streamlit as st
from utils import new_nextcloud_tools as nc

st.title("🔄 Synchronisation Nextcloud")

# 1. Connexion à Nextcloud
client = nc.connect_to_nextcloud()

# 2. Vérification de la config et synchronisation automatique
if client:
    nc_folder, local_folder = nc.verify_config_and_sync(client)

    # 3. Choix manuel si pas de config
    if not nc_folder or not local_folder:
        nc_folder = nc.choose_remote_folder()
        local_folder = nc.choose_local_folder()

        if nc_folder and local_folder:
            nc.save_config(nc_folder, local_folder)
            nc.download_missing_files(client, nc_folder, local_folder)
