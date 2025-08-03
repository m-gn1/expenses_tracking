import streamlit as st
st.title("TODO")
st.write("recuperer expenses data de remote a local, reprendre le meme code ")


import os
import streamlit as st
import pandas as pd
from utils.import_files import list_processed_files, display_processed_summary, save_processed_files
from utils.ui_helpers import clear_cache_on_page_change, assign_missing_users
from utils.new_nextcloud_tools import (
    load_config,
    list_remote_pdf_files, 
    list_remote_csv_files,
    check_if_existing_processed_file_remote, 
    save_df_to_nextcloud_csv, 
    clear_local_folder)
from utils.import_files_nextcloud import display_file_processing_block, import_pdf_file
from utils.helpers import concat_dataframes
from utils.nextcloud_helpers import sync_from_nextcloud_to_server


REMOTE_PROCESSED_PATH = "data/processed/"

## end config

##### INIT #######
st.session_state.setdefault("connect_validated", None)
st.session_state.setdefault("client", None)
st.session_state.setdefault("working_folder", None)

####### CLEAR CACHE ########
# Identifier cette page par un nom unique
CURRENT_PAGE = "0_5_NEW_Update_categories.py"  # ex: "Importer", "Analyse", "Résultats"
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
    working_folder = config.get("working_folder")

processed_folder = working_folder+"/"+REMOTE_PROCESSED_PATH
local_processed_folder = os.path.join(".cache/", REMOTE_PROCESSED_PATH)
name_processed_df = "expenses_data.csv"


##### clear cache #####
clear_local_folder(local_processed_folder)
sync_from_nextcloud_to_server(client, processed_folder, local_processed_folder)
existing_df = check_if_existing_processed_file_remote(client, processed_folder, name_processed_df, local_processed_folder)
st.dataframe(existing_df)