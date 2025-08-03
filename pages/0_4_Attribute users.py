
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
    clear_remote_folder)
from utils.import_files_nextcloud import display_file_processing_block, import_pdf_file
from utils.helpers import concat_dataframes
from utils.nextcloud_helpers import sync_from_nextcloud_to_server

# from config import IMPORTED_FOLDER, PROCESSED_PDF
# from config import REMOTE_IMPORTED_FOLDER, REMOTE_PROCESSED_PDF, REMOTE_PROCESSED_PATH, LOCAL_NEW_PDF

## config

REMOTE_IMPORTED_FOLDER = "data/imported_data/"
REMOTE_PROCESSED_PDF = "data/processed_pdf/"
REMOTE_PROCESSED_PATH = "data/processed/"
LOCAL_NEW_PDF = "data/new_pdf/"
LOCAL_ALL_PDF = "data/all_pdf/"
REMOTE_FOLDERS = [REMOTE_IMPORTED_FOLDER, REMOTE_PROCESSED_PDF, REMOTE_PROCESSED_PATH]
LOCAL_FOLDERS = REMOTE_FOLDERS + [LOCAL_NEW_PDF, LOCAL_ALL_PDF]
FOYER = ["Foyer"]
## end config

##### INIT #######
st.session_state.setdefault("connect_validated", None)
st.session_state.setdefault("client", None)
st.session_state.setdefault("source_folder", None)
st.session_state.setdefault("working_folder", None)
st.session_state.setdefault("full_df", None)

####### CLEAR CACHE ########
# Identifier cette page par un nom unique
CURRENT_PAGE = "0_3_ NEW Importer_fichiers.py"  # ex: "Importer", "Analyse", "Résultats"
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
    source_folder = config.get("source_folder")
    working_folder = config.get("working_folder")

processed_folder_pdf = working_folder+"/"+REMOTE_PROCESSED_PDF
processed_folder = working_folder+"/"+REMOTE_PROCESSED_PATH
imported_folder_csv = working_folder+"/"+REMOTE_IMPORTED_FOLDER
local_imported_folder_csv = os.path.join(".cache/", REMOTE_IMPORTED_FOLDER)
local_processed_folder = os.path.join(".cache/", REMOTE_PROCESSED_PATH)
name_processed_df = "expenses_data.csv"

st.title("📄 Affectation manuelle des utilisateurs")
all_dfs = []
# Check if there are new PDF files to process
new_pdf, processed_pdf = list_remote_pdf_files(client, source_folder), list_remote_pdf_files(client, processed_folder_pdf)
if all(file in processed_pdf for file in new_pdf):
    st.success("✅ Tous les fichiers présents dans `data/new_pdf/` ont été traités et sauvegardés, prêt pour l'attribution")
else:
    missing = [file for file in new_pdf if file not in processed_pdf]
    st.warning(f"⚠️ Il reste {len(missing)} fichier(s) à extraire : {', '.join(missing)}")
    st.page_link("pages/1_Importer_fichiers.py", label="➡️ Aller à l’import")

# Check if all files from the remote imported folder exist in the local imported folder

##### TO DO: check cacher folder, copy paste files from remote to local cache #####
## DEBUG HERE ## 
imported_csv_remote = list_remote_csv_files(client, imported_folder_csv)
imported_csv_local = list_processed_files(local_imported_folder_csv)

missing = [f for f in imported_csv_remote if f not in imported_csv_local]

if not imported_csv_local:
    st.warning("⚠️ Le dossier cache local est vide.")
    sync_from_nextcloud_to_server(client, imported_folder_csv, local_imported_folder_csv)
elif missing:
    st.warning(f"⚠️ Il reste {len(missing)} fichier(s) à extraire : {', '.join(missing)}")
else:
    st.success("✅ Tous les fichiers sont bien présents dans le cache.")


### Check if a file already exists
nb_df = 0
existing_df = check_if_existing_processed_file_remote(client, processed_folder, name_processed_df, local_processed_folder)
if existing_df is not None:
    all_dfs.append(existing_df)
    st.session_state["full_df"] = None
    nb_df = 1
    st.info(f"Il y a déjà eu un fichier processé : {name_processed_df}")
else:
    st.info(f"Il n'y a pas de fichier processé dans {processed_folder} ou le fichier {name_processed_df} n'existe pas.")


##### Assign users to the processed files #####

### METTRE DF DANS LISTE
# Parcours tous les fichiers du dossier
if os.listdir(local_imported_folder_csv):
    for file in os.listdir(local_imported_folder_csv):
        if file.endswith("_Monthly BarclayCard Statement.csv"):
            path_df = os.path.join(local_imported_folder_csv, file)
            df = pd.read_csv(path_df)
            all_dfs.append(df)
            st.session_state["full_df"] = None
            st.info(f"Le fichier {file} n'a pas d'users assignés.")
    st.info(f"Il y a {len(all_dfs)-nb_df} fichiers sans users assignés.")
elif existing_df is not None:
    st.success(f"Pas d'autre fichiers à part {name_processed_df} n'a été ajouté")
else:
    st.error("❌ il n'y a aucun fichier à traiter")
    st.page_link("pages/0_1_NEW Synchro NC cache working.py", label="🔐 Aller à la page de connexion")

if "full_df" in st.session_state and st.session_state["full_df"] is not None:
    full_df = st.session_state["full_df"]
    st.write("le df est dans session.state")
    st.write(full_df['user'].unique())
else:
    full_df = concat_dataframes(*all_dfs)
    st.write("Voici le fichier à assigner")
    df_wo_users = full_df[full_df['user'].isna()]
    st.dataframe(df_wo_users)
    st.session_state["full_df"] = full_df
    cardholders = full_df["cardholder"].dropna().unique()
    st.write(cardholders)
    st.session_state["cardholders"] = cardholders

assign_missing_users(FOYER, full_df_key="full_df", cardholders_key="cardholders")
# Affichage si tout est rempli
if st.session_state["full_df"]["user"].notna().all():
    st.success("✅ Toutes les lignes ont un utilisateur affecté.")
    st.session_state["full_df"] = full_df
    st.dataframe(st.session_state["full_df"], use_container_width=True)

# Sauvegarder
if st.button("💾 Sauvegarder ce fichier assigné", key="save_full_df"):
    output_path_imported_cache = os.path.join(local_processed_folder, name_processed_df)
    final_full_df = st.session_state["full_df"]
    final_full_df.to_csv(output_path_imported_cache, index=False)
    st.success(f"Fichier sauvegardé dans {output_path_imported_cache}")
    save_df_to_nextcloud_csv(client, final_full_df, processed_folder, name_processed_df)
    clear_remote_folder(client, imported_folder_csv)
## retirer les fichiers de imported data ##
    for fichier in os.listdir(local_imported_folder_csv):
        chemin_complet = os.path.join(local_imported_folder_csv, fichier)
        if os.path.isfile(chemin_complet):
            os.remove(chemin_complet)
    st.session_state["full_df"] = final_full_df
    st.rerun()

