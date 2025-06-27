import streamlit as st
import pandas as pd
from utils.import_files import list_pdf_files, list_files, display_file_processing_block, import_pdf_file, display_processed_summary, save_processed_files
from utils.ui_helpers import clear_cache_on_page_change

####### CLEAR CACHE ########
# Identifier cette page par un nom unique
CURRENT_PAGE = "0_Importer_fichiers.py"  # ex: "Importer", "Analyse", "Résultats"
clear_cache_on_page_change(CURRENT_PAGE)

###########################################


NEW_PDF = "./data/new_pdf"
IMPORTED_FOLDER = "./data/imported_data"
PROCESSED_PDF = "./data/processed_pdf"

new_pdf, processed_pdf = list_pdf_files(NEW_PDF, PROCESSED_PDF)

st.title("📦 Monthly Ingestion of pdf files")

raw_files, imported_files = list_files(NEW_PDF, IMPORTED_FOLDER)
if not raw_files:
    st.warning("Aucun fichier PDF trouvé dans data/new_pdf/")
    st.stop()

for file in new_pdf:
    st.session_state.setdefault(f"extracted_{file}", False)
    is_done = file in processed_pdf
    display_file_processing_block(NEW_PDF, file, is_done)

#Une fois tous les blocs affichés
active_file = st.session_state.get("active_file")
if active_file:
    import_pdf_file(IMPORTED_FOLDER, NEW_PDF, PROCESSED_PDF, active_file)

if all(file in processed_pdf for file in new_pdf):
    st.success("✅ Tous les fichiers présents dans `data/new_pdf/` ont été traités et sauvegardés, prêt pour l'attribution")
    st.page_link("pages/1_Attribute_users.py", label="➡️ Aller à l’attribution", icon="👤")
else:
    missing = [file for file in new_pdf if file not in processed_pdf]
    st.warning(f"⚠️ Il reste {len(missing)} fichier(s) à extraire : {', '.join(missing)}")

## si tous les fichiers ont été procesées
# raw_files_end, imported_files_end = list_files(NEW_PDF, IMPORTED_FOLDER)
# if all(file in imported_files_end for file in raw_files_end):
#     st.success("✅ Tous les fichiers présents dans `data/new_pdf/` ont été traités et sauvegardés.")
#     st.page_link("pages/1_Attribute_users.py", label="➡️ Aller à l’attribution", icon="👤")

# else:
#     missing = [file for file in raw_files if file not in imported_files]
#     st.warning(f"⚠️ Il reste {len(missing)} fichier(s) à extraire : {', '.join(missing)}")


