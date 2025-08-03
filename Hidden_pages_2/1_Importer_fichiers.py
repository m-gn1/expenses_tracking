import streamlit as st
import pandas as pd
from utils.import_files import list_pdf_files, list_files, display_file_processing_block, import_pdf_file, display_processed_summary, save_processed_files
from utils.ui_helpers import clear_cache_on_page_change
from utils.nextcloud_tools import load_config
from config import IMPORTED_FOLDER, PROCESSED_PDF


####### CLEAR CACHE ########
# Identifier cette page par un nom unique
CURRENT_PAGE = "1_Importer_fichiers.py"  # ex: "Importer", "Analyse", "Résultats"
clear_cache_on_page_change(CURRENT_PAGE, preserve_keys="source_folder")

st.write(st.session_state.get("source_folder"))

###########################################

config = load_config()
if config:
    local_folder = config.get("local_folder")

new_pdf, processed_pdf = list_pdf_files(local_folder, PROCESSED_PDF)

st.title("📦 Monthly Ingestion of pdf files")

raw_files, imported_files = list_files(local_folder, IMPORTED_FOLDER)
if not raw_files:
    st.warning("Aucun fichier PDF trouvé dans data/new_pdf/")
    st.stop()

for file in new_pdf:
    st.session_state.setdefault(f"extracted_{file}", False)
    is_done = file in processed_pdf
    display_file_processing_block(local_folder, file, is_done)

#Une fois tous les blocs affichés
active_file = st.session_state.get("active_file")
if active_file:
    import_pdf_file(IMPORTED_FOLDER, local_folder, PROCESSED_PDF, active_file)

if all(file in processed_pdf for file in new_pdf):
    st.success("✅ Tous les fichiers présents dans `data/new_pdf/` ont été traités et sauvegardés, prêt pour l'attribution")
    st.page_link("pages/2_Attribute_users.py", label="➡️ Aller à l’attribution", icon="👤")
else:
    missing = [file for file in new_pdf if file not in processed_pdf]
    st.warning(f"⚠️ Il reste {len(missing)} fichier(s) à extraire : {', '.join(missing)}")


