import streamlit as st
import pandas as pd
from utils.helpers import concat_dataframes
from utils.ui_helpers import assign_missing_users, get_pdf_files, display_file_selection, get_extraction_options

DATA_FOLDER = "./data/new_pdf"  # adapte ce chemin à ta structure

st.title("📄 Extraction de données PDF avec affectation manuelle des utilisateurs")

st.warning("cette page n'est pas utile")

pdf_files = get_pdf_files(DATA_FOLDER)
selected_files = display_file_selection(pdf_files)


# def main():
#     if selected_files:
#         user_column_options = get_extraction_options(selected_files)

#         if st.button("🔄 Extraire les données"):
#             dfs, cardholders = extract_selected_data(selected_files, user_column_options, DATA_FOLDER)

#             full_df = concat_dataframes(*dfs)
#             st.session_state["full_df"] = full_df
#             st.session_state["cardholders"] = cardholders

#             st.success("✅ Données extraites avec succès.")
#             st.dataframe(full_df)

#     # Formulaire pour compléter les utilisateurs manquants

#     if "full_df" in st.session_state:
#         assign_missing_users()

#     # Affichage si tout est rempli
#     if st.session_state["full_df"]["user"].notna().all():
#         st.success("✅ Toutes les lignes ont un utilisateur affecté.")
#         st.dataframe(st.session_state["full_df"], use_container_width=True)


# main()
