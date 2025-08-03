
import streamlit as st
import pandas as pd
import tempfile
import os
from utils.ui_helpers import clear_cache_on_page_change
from utils.new_nextcloud_tools import (
    load_config)
from utils.import_files_nextcloud import save_df_to_nextcloud_csv
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
####################################


####### ----------------- in my app -------------########

##### INIT #######
st.session_state.setdefault("connect_validated", None)
st.session_state.setdefault("client", None)
st.session_state.setdefault("source_folder", None)
st.session_state.setdefault("working_folder", None)

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
import pandas as pd
df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
st.write(working_folder)
full_path = os.path.join(working_folder, REMOTE_IMPORTED_FOLDER)
st.write(full_path)
save_df_to_nextcloud_csv(client, df, full_path, "data.csv")