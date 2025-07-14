import streamlit as st
import pandas as pd
from utils.import_files import display_processed_summary, save_processed_files
from utils.ui_helpers import clear_cache_on_page_change
from utils.new_nextcloud_tools import (
    load_config,
    list_remote_pdf_files)
from utils.import_files_nextcloud import display_file_processing_block, import_pdf_file
# from config import IMPORTED_FOLDER, PROCESSED_PDF
# from config import REMOTE_IMPORTED_FOLDER, REMOTE_PROCESSED_PDF, REMOTE_PROCESSED_PATH, LOCAL_NEW_PDF

## config

REMOTE_IMPORTED_FOLDER = "data/imported_data/"
REMOTE_PROCESSED_PDF = "data/processed_pdf/"
REMOTE_PROCESSED_PATH = "data/processed/"
LOCAL_NEW_PDF = "data/new_pdf/"
REMOTE_FOLDERS = [REMOTE_IMPORTED_FOLDER, REMOTE_PROCESSED_PDF, REMOTE_PROCESSED_PATH]
LOCAL_FOLDERS = REMOTE_FOLDERS + [LOCAL_NEW_PDF]

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

config = load_config()
if config:
    source_folder = config.get("source_folder")
    working_folder = config.get("working_folder")

processed_folder_pdf = working_folder+"/"+REMOTE_PROCESSED_PDF
imported_folder_pdf = working_folder+"/"+REMOTE_IMPORTED_FOLDER

new_pdf, processed_pdf = list_remote_pdf_files(client, source_folder, processed_folder_pdf)

st.title("DEBUG")
st.write(new_pdf)
st.write(processed_pdf)

for file in new_pdf:
    st.write(file)

# st.title("📦 Monthly Ingestion of pdf files")

# raw_files, imported_files = list_remote_pdf_files(client, source_folder, imported_folder_pdf)
# if not raw_files:
#     st.warning(f"Aucun fichier PDF trouvé dans {source_folder}")
#     st.stop()

# for file in new_pdf:
#     st.session_state.setdefault(f"extracted_{file}", False)
#     is_done = file in processed_pdf
#     st.write("debug")
#     st.write(file)
#     st.write(is_done)
#     st.write(processed_pdf)
#     st.write(LOCAL_NEW_PDF)
#     st.write(source_folder)
#     display_file_processing_block(client, source_folder, LOCAL_NEW_PDF, file, is_done)

# #Une fois tous les blocs affichés
# active_file = st.session_state.get("active_file")
# if active_file:
#     import_pdf_file(client, source_folder, working_folder, REMOTE_IMPORTED_FOLDER, LOCAL_NEW_PDF, REMOTE_PROCESSED_PDF,active_file)

# if all(file in processed_pdf for file in new_pdf):
#     st.success("✅ Tous les fichiers présents dans `data/new_pdf/` ont été traités et sauvegardés, prêt pour l'attribution")
#     st.page_link("pages/2_Attribute_users.py", label="➡️ Aller à l’attribution", icon="👤")
# else:
#     missing = [file for file in new_pdf if file not in processed_pdf]
#     st.warning(f"⚠️ Il reste {len(missing)} fichier(s) à extraire : {', '.join(missing)}")


