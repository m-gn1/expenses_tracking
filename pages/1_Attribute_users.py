import streamlit as st
import pandas as pd
import os
from utils.import_files import list_files, list_processed_files, list_pdf_files
from utils.ui_helpers import get_csv_files, assign_missing_users
from utils.helpers import check_if_existing_processed_file, concat_dataframes

NEW_PDF = "./data/new_pdf"
PROCESSED_PDF = "./data/processed_pdf"
IMPORTED_FOLDER = "./data/imported_data"
processed_path = "./data/processed"
name_df = "expenses_data.csv"

st.title("📄 Affectation manuelle des utilisateurs")
all_dfs = []
## check si on a tout importé
new_pdf, processed_pdf = list_pdf_files(NEW_PDF, PROCESSED_PDF)
if all(file in processed_pdf for file in new_pdf):
    st.success("✅ Tous les fichiers présents dans `data/new_pdf/` ont été traités et sauvegardés, prêt pour l'attribution")
    
else:
    missing = [file for file in new_pdf if file not in processed_pdf]
    st.warning(f"⚠️ Il reste {len(missing)} fichier(s) à extraire : {', '.join(missing)}")

### Check if a file already exists
existing_df = check_if_existing_processed_file(processed_path, name_df)
if existing_df is not None:
    all_dfs.append(existing_df)
    st.write(f"{name_df} existe dans le dossier")

### METTRE DF DANS LISTE
# Parcours tous les fichiers du dossier
if os.listdir(IMPORTED_FOLDER):
    for file in os.listdir(IMPORTED_FOLDER):
        st.write(file)
        if file.endswith("_Monthly BarclayCard Statement.csv"):
            path_df = os.path.join(IMPORTED_FOLDER, file)
            df = pd.read_csv(path_df)
            all_dfs.append(df)
    st.write(f"{len(all_dfs)} fichiers CSV ont été chargés.")
elif existing_df is not None:
    st.write(f"Pas d'autre fichiers à part {name_df} n'a été ajouté")
else:
    st.error("❌ il n'y a aucun fichier à traiter")
    st.page_link("pages/0_Importer_fichiers.py", label="➡️ Aller à l’import")


if "full_df" in st.session_state and st.session_state["full_df"] is not None:
    full_df = st.session_state["full_df"]
    st.write("le df est dans session.state")
    st.write(full_df['user'].unique())
else:
    full_df = concat_dataframes(*all_dfs)
    st.write("Voici le fichier à assigner")
    st.dataframe(full_df)
    st.session_state["full_df"] = full_df
    cardholders = full_df["cardholder"].dropna().unique()
    st.session_state["cardholders"] = cardholders


##### probleme initilisation si on a que des fichiers sans cardhiolder. 
assign_missing_users(full_df_key="full_df", cardholders_key="cardholders")
# Affichage si tout est rempli
if st.session_state["full_df"]["user"].notna().all():
    st.success("✅ Toutes les lignes ont un utilisateur affecté.")
    st.session_state["full_df"] = full_df
    st.dataframe(st.session_state["full_df"], use_container_width=True)

# Sauvegarder
if st.button("💾 Sauvegarder ce fichier assigné", key="save_full_df"):
    output_path = os.path.join(processed_path, name_df)
    final_full_df = st.session_state["full_df"]
    final_full_df.to_csv(output_path, index=False)
    for fichier in os.listdir(IMPORTED_FOLDER):
        chemin_complet = os.path.join(IMPORTED_FOLDER, fichier)
        if os.path.isfile(chemin_complet):
            os.remove(chemin_complet)
    st.success(f"Fichier sauvegardé dans {output_path}")
    st.session_state["full_df"] = final_full_df
    st.rerun()
