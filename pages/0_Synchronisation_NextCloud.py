import streamlit as st
from utils import nextcloud_tools as nc

st.set_page_config(page_title="🔗 Connexion Nextcloud", layout="centered")
st.title("☁️ Synchronisation Nextcloud")

client = nc.connect_to_nextcloud()

if client:
    # Étape 1 : vérifier la config
    nc_folder, local_folder = nc.verify_config_and_sync(client)

    # Étape 2 : si pas de config → choix manuels
    if not (nc_folder and local_folder):
        nc_folder = nc.choose_remote_folder()
        local_folder = nc.choose_local_folder()

        if nc_folder and local_folder:
            nc.download_missing_files(client, nc_folder, local_folder)
            nc.save_config(nc_folder, local_folder)
