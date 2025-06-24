import streamlit as st
import pandas as pd
from utils.import_files import list_processed_files, display_file_processing_block, process_pdf_file, display_processed_summary, save_processed_files
import os


IMPORTED_FOLDER = "./data/imported_data"
CATEFORISED_FOLDER = "./data/categorised_data"


st.title("📦 Updating categories")

imported_files = list_processed_files(IMPORTED_FOLDER)
if not imported_files:
    st.warning("Aucun fichier CSV trouvé dans data/processed/")
    st.stop()

if len(imported_files) > 1:
    # La liste contient plus d'un élément
    st.caption("Plus d'un élément, je contacat")
else:
    # La liste contient un seul élément
    st.caption("Un seul élément, je l'affiche")
    path = os.path.join(IMPORTED_FOLDER, imported_files[0])
    df = pd.read_csv(path)
    st.dataframe(df, use_container_width=True)  


# for file in imported_files:
#     is_done = file in imported_files
#     st.success(f"File: {file}")
#     st.dataframe(pd.read_csv(f"{IMPORTED_FOLDER}/{file}"), use_container_width=True)