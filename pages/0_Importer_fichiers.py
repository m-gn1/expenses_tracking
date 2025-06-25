import streamlit as st
import pandas as pd
from utils.import_files import list_files, display_file_processing_block, import_pdf_file, display_processed_summary, save_processed_files
from utils.helpers import add_df_to_dict, concat_all_dataframes_from_session_dict

RAW_FOLDER = "./data/raw"
IMPORTED_FOLDER = "./data/imported_data"


st.title("📦 Monthly Ingestion of pdf files")

raw_files, imported_files = list_files(RAW_FOLDER, IMPORTED_FOLDER)
if not raw_files:
    st.warning("Aucun fichier PDF trouvé dans data/raw/")
    st.stop()

for file in raw_files:
    st.session_state.setdefault(f"extracted_{file}", False)
    is_done = file in imported_files
    display_file_processing_block(RAW_FOLDER, file, is_done)

#Une fois tous les blocs affichés
active_file = st.session_state.get("active_file")
if active_file:
    import_pdf_file(IMPORTED_FOLDER, active_file)

## si tous les fichiers ont été procesées
raw_files_end, imported_files_end = list_files(RAW_FOLDER, IMPORTED_FOLDER)
if all(file in imported_files_end for file in raw_files_end):
    st.success("✅ Tous les fichiers présents dans `data/raw/` ont été traités et sauvegardés.")
    st.page_link("pages/1_Attribute_users.py", label="➡️ Aller à l’attribution", icon="👤")

else:
    missing = [file for file in raw_files if file not in imported_files]
    st.warning(f"⚠️ Il reste {len(missing)} fichier(s) à extraire : {', '.join(missing)}")


