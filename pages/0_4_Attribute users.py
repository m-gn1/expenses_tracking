import streamlit as st
st.title("TODO")
st.write("récuperr fichier de nextcloud 'importer', make sure cache importer is empty, importer les fichiers dans le cache, et les traiter un par un. ")

import os
import streamlit as st
import pandas as pd
from utils.import_files import list_processed_files, display_processed_summary, save_processed_files
from utils.ui_helpers import clear_cache_on_page_change
from utils.new_nextcloud_tools import (
    load_config,
    list_remote_pdf_files, 
    list_remote_csv_files)
from utils.import_files_nextcloud import display_file_processing_block, import_pdf_file
# from config import IMPORTED_FOLDER, PROCESSED_PDF
# from config import REMOTE_IMPORTED_FOLDER, REMOTE_PROCESSED_PDF, REMOTE_PROCESSED_PATH, LOCAL_NEW_PDF

## config

REMOTE_IMPORTED_FOLDER = "data/imported_data/"
REMOTE_PROCESSED_PDF = "data/processed_pdf/"
REMOTE_PROCESSED_PATH = "data/processed/"
LOCAL_NEW_PDF = "data/new_pdf/"
LOCAL_ALL_PDF = "data/all_pdf/"
REMOTE_FOLDERS = [REMOTE_IMPORTED_FOLDER, REMOTE_PROCESSED_PDF, REMOTE_PROCESSED_PATH]
LOCAL_FOLDERS = REMOTE_FOLDERS + [LOCAL_NEW_PDF, LOCAL_ALL_PDF]

## end config

##### INIT #######
st.session_state.setdefault("connect_validated", None)
st.session_state.setdefault("client", None)
st.session_state.setdefault("source_folder", None)
st.session_state.setdefault("working_folder", None)

####### CLEAR CACHE ########
# Identifier cette page par un nom unique
CURRENT_PAGE = "0_3_ NEW Importer_fichiers.py"  # ex: "Importer", "Analyse", "Résultats"
clear_cache_on_page_change(CURRENT_PAGE, preserve_keys=["connect_validated", "client", "source_folder", "working_folder"])

if st.session_state["connect_validated"]:
    client = st.session_state["client"]
    st.info("🔓 Connecté à NextCloud")
else:
    st.warning("⚠️ Connecte toi à NextCloud")
    st.page_link("pages/0_1_NEW Synchro NC cache working.py", label="🔐 Aller à la page de connexion")

###########################################

###### LOAD CONFIG ######
config = load_config()
if config:
    source_folder = config.get("source_folder")
    working_folder = config.get("working_folder")

processed_folder_pdf = working_folder+"/"+REMOTE_PROCESSED_PDF
imported_folder_csv = working_folder+"/"+REMOTE_IMPORTED_FOLDER
local_imported_folder_csv = os.path.join(".cache/", REMOTE_IMPORTED_FOLDER)

st.title("📄 Affectation manuelle des utilisateurs")
all_dfs = []
# Check if there are new PDF files to process
new_pdf, processed_pdf = list_remote_pdf_files(client, source_folder), list_remote_pdf_files(client, processed_folder_pdf)
if all(file in processed_pdf for file in new_pdf):
    st.success("✅ Tous les fichiers présents dans `data/new_pdf/` ont été traités et sauvegardés, prêt pour l'attribution")
else:
    missing = [file for file in new_pdf if file not in processed_pdf]
    st.warning(f"⚠️ Il reste {len(missing)} fichier(s) à extraire : {', '.join(missing)}")
    st.page_link("pages/1_Importer_fichiers.py", label="➡️ Aller à l’import")

# Check if all files from the remote imported folder exist in the local imported folder
imported_csv_remote = list_remote_csv_files(client, imported_folder_csv)
imported_csv_local= list_processed_files(local_imported_folder_csv)
if all(file in imported_csv_remote for file in imported_csv_local):
    st.success(f"✅ Tous les fichiers présents dans {imported_folder_csv} sont presents dans le cache local `{local_imported_folder_csv}`")
else:
    missing = [file for file in imported_csv_remote if file not in imported_csv_local]
    st.warning(f"⚠️ Il reste {len(missing)} fichier(s) à extraire : {', '.join(missing)}")

### Check if a file already exists
# nb_df = 0
# existing_df = check_if_existing_processed_file(processed_path, name_df)
# if existing_df is not None:
#     all_dfs.append(existing_df)
#     nb_df = 1
#     st.info(f"Il y a déjà eu un fichier processé : {name_df}")


