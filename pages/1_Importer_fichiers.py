import streamlit as st
import os
import pandas as pd
from utils.data_loader import extract_all_transactions, extract_cardholder_refs
from utils.helpers import concat_dataframes
from utils.ui_helpers import assign_missing_users
from utils.import_files import list_files, display_file_processing_block, process_pdf_file, display_processed_summary, save_processed_files

RAW_FOLDER = "./data/raw"
PROCESSED_FOLDER = "./data/processed_pdf"

st.title("📦 Monthly Ingestion of pdf files")

raw_files, processed_files = list_files(RAW_FOLDER, PROCESSED_FOLDER)
if not raw_files:
    st.warning("Aucun fichier PDF trouvé dans data/raw/")
    st.stop()

for file in raw_files:
    is_done = file in processed_files
    display_file_processing_block(RAW_FOLDER, file, is_done)
    process_pdf_file(PROCESSED_FOLDER, file)

display_processed_summary(PROCESSED_FOLDER)

save_processed_files(PROCESSED_FOLDER)
