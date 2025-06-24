import streamlit as st
import pandas as pd
from utils.import_files import list_files, display_file_processing_block, process_pdf_file, display_processed_summary, save_processed_files

RAW_FOLDER = "./data/raw"
IMPORTED_FOLDER = "./data/imported_data"

st.title("📦 Monthly Ingestion of pdf files")

raw_files, processed_files = list_files(RAW_FOLDER, IMPORTED_FOLDER)
if not raw_files:
    st.warning("Aucun fichier PDF trouvé dans data/raw/")
    st.stop()

for file in raw_files:
    is_done = file in processed_files
    display_file_processing_block(RAW_FOLDER, file, is_done)
    process_pdf_file(IMPORTED_FOLDER, file)

#display_processed_summary(IMPORTED_FOLDER)

#save_processed_files(IMPORTED_FOLDER)
