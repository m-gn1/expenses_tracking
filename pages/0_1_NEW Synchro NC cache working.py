# Verifie si une config existe dans cache, 
# sinon selectionne dossier de raw data, vérifier si dodsier working exsite, le cree sinon
# enregistre dans config cache

import streamlit as st
from utils.new_nextcloud_tools import (
    connect_to_nextcloud, 
    verify_config,  
    ensure_remote_folder_exists,
    choose_remote_source_folder,
    choose_remote_working_folder,
    save_config,
    create_nested_subfolders_in_nextcloud,
    create_local_subfolders)
#from config import REMOTE_IMPORTED_FOLDER, REMOTE_PROCESSED_PDF, REMOTE_PROCESSED_PATH, LOCAL_NEW_PDF


## config

REMOTE_IMPORTED_FOLDER = "data/imported_data/"
REMOTE_PROCESSED_PDF = "data/processed_pdf/"
REMOTE_PROCESSED_PATH = "data/processed/"
LOCAL_NEW_PDF = "data/new_pdf/"
LOCAL_ALL_PDF = "data/all_pdf/"
REMOTE_FOLDERS = [REMOTE_IMPORTED_FOLDER, REMOTE_PROCESSED_PDF, REMOTE_PROCESSED_PATH]
LOCAL_FOLDERS = REMOTE_FOLDERS + [LOCAL_NEW_PDF, LOCAL_ALL_PDF]

## end config

st.title("☁️ Synchronisation Nextcloud")

# 1. Connexion à Nextcloud
st.session_state.setdefault("working_folder", None)
st.session_state.setdefault("source_folder", None)
client = connect_to_nextcloud()

#### Verfiier si fichier de conf existe. 
if client:
    # Étape 1 : vérifier la config
    source_folder, working_folder = verify_config(client) ### j'ens suis là
    st.write("La config existe")
    st.write(source_folder)
    st.write(working_folder)
    create_local_subfolders(".cache", LOCAL_FOLDERS)

    # Étape 2 : si pas de config → choix manuels
    if not (source_folder and working_folder):
        remote_path = st.text_input("📁 Dossier distant à vérifier/créer", value="/fichiers")
        if st.button("📂 Vérifier/créer le dossier distant"):
            ensure_remote_folder_exists(st.session_state["client"], remote_path)

        source_folder = choose_remote_source_folder(defaut="/Londres_shared/Bank/Credit Card Statements")
        working_folder = choose_remote_working_folder(defaut="/Londres_shared/Bank/app_working_directory")
        st.session_state["source_folder"] = source_folder
        st.session_state["working_folder"] = working_folder
        create_nested_subfolders_in_nextcloud(client, working_folder, REMOTE_FOLDERS)
        create_local_subfolders(".cache", LOCAL_FOLDERS)
        save_config(source_folder, working_folder)
        st.write(st.session_state["source_folder"])
        st.write(st.session_state["working_folder"])

        ###### TO DO : voir si je crée ici l'arborescence du dossier de travail #######
        #### TO DO : après avoir utilise downloard missing files, 
        # je peux supprimer Syncho NC cache 
        # et nettoyer nex nextcloud tools