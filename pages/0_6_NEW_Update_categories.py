import os
import streamlit as st
import pandas as pd
from utils.ui_helpers import clear_cache_on_page_change, manage_categories
from utils.new_nextcloud_tools import (
    load_config,
    check_if_existing_processed_file_remote, 
    clear_local_folder,
    save_df_to_nextcloud_csv, 
    get_clef_openAI)
from utils.nextcloud_helpers import sync_from_nextcloud_to_server
from utils.models import classify_expenses_learning, classify_expenses_learning_require_key

REMOTE_PROCESSED_PATH = "data/processed/"

## end config

##### INIT #######
st.session_state.setdefault("connect_validated", None)
st.session_state.setdefault("client", None)
st.session_state.setdefault("working_folder", None)

####### CLEAR CACHE ########
# Identifier cette page par un nom unique
CURRENT_PAGE = "0_6_NEW_Update_categories.py"  # ex: "Importer", "Analyse", "Résultats"
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
    working_folder = config.get("working_folder")

processed_folder = working_folder+"/"+REMOTE_PROCESSED_PATH
local_processed_folder = os.path.join(".cache/", REMOTE_PROCESSED_PATH)
name_processed_df = "expenses_data.csv"


##### clear cache #####
clear_local_folder(local_processed_folder)
sync_from_nextcloud_to_server(client, processed_folder, local_processed_folder)
existing_df = check_if_existing_processed_file_remote(client, processed_folder, name_processed_df, local_processed_folder)

df = existing_df.drop_duplicates(subset="transaction_ID")

### CATEGORIES ###
st.dataframe (df)
st.title("📦 Updating categories")

## clef open AI
# st.dataframe(df["categories"].value_counts())
# st.header("🔐 Clé OpenAI")
# st.text("Cette clé est utilisée pour classifier les dépenses avec GPT.")
# openai_api_key = st.text_input("Entre ta clé OpenAI", type="password")

# # Mémoriser dans session_state si saisie
# if openai_api_key:
#     st.session_state["openai_api_key"] = openai_api_key

get_clef_openAI(defaut="/Londres_shared/Bank/app_working_directory/open_ai_key.txt")
## fin clef open AII


if df["categories"].notnull().all():
    st.success("✅ Tout est catégorisé")
else: 
    with st.expander("🤖 Je catégorise avec l'IA", expanded=True):        
        manage_categories()
        if "openai_api_key" in st.session_state:
            if st.button("⚙️ Lançons la machine", key="ia"):
                df["predicted_category"] = df.apply(
                    lambda row: classify_expenses_learning_require_key(
                        row["description"],
                        st.session_state["list_categories"],  # ou une liste de ton choix
                        existing_category=row["categories"] if pd.notnull(row["categories"]) else None
                    ),
                    axis=1
                )
                st.dataframe (df)
                st.dataframe(df["predicted_category"].value_counts())
                st.dataframe(df["categories"].value_counts())
                st.session_state["df_categories_ia"] = df

if "df_categories_mano" in st.session_state and st.session_state["df_categories_mano"] is not None:
    df_ia = st.session_state["df_categories_mano"].copy()
    st.caption("le df est dans session.state")
elif "df_categories_ia" in st.session_state and st.session_state["df_categories_ia"] is not None:
    df_ia = st.session_state["df_categories_ia"].copy()
    st.caption("new df")
else:
    st.caption("tout est vide")

if "df_categories_mano" in st.session_state or "df_categories_ia" in st.session_state :
    with st.expander("✍🏻 Je vérifie les catégories à la main",expanded =True):
        st.session_state["df_categories_mano"] = df_ia

    ########################### fonction attribution #########################
        col_to_assign = "categories"
        full_df = st.session_state.get("df_categories_mano")
        categories = sorted(st.session_state["list_categories"])

    if full_df is None or full_df[col_to_assign].notna().all():
        st.write("issue") # remove si fonction, et donc return. 
        #return

    rows_to_fill = full_df[full_df[col_to_assign].isna()].copy()
    if rows_to_fill.empty:
        st.write("issue")
        #return

    # ✅ Afficher message de succès si besoin
    if st.session_state.get("affectation_success"):
        st.success("✅ Toutes les lignes ont été mises à jour avec succès 🎉")
        del st.session_state["affectation_success"]
        st.dataframe(full_df, use_container_width=True)
        #return

    st.markdown("### 🖊️ Revoir les categories")

    if "cat_selections" not in st.session_state:
        st.session_state.cat_selections = {}

    with st.form("cat_assignment_form"):
        for i, row in rows_to_fill.iterrows():
            row_key = f"cat_{i}"
            default = st.session_state.cat_selections.get(row_key, row["predicted_category"])
            date_str = row["date"] if isinstance(row["date"], str) else row["date"].strftime("%Y-%m-%d")
            label = f"{date_str}| {row['transaction_ID']} |{row['user']} | {row['description']}| {row['categories']} | {row['amount']} £"

            selected = st.selectbox(
                label,
                options=categories,
                index=categories.index(default) if default in categories else 0,
                key=row_key
            )
            st.session_state.cat_selections[row_key] = selected

        submitted = st.form_submit_button("✅ Valider les affectations")

    if submitted:
        for i, row in rows_to_fill.iterrows():
            row_key = f"cat_{i}"
            full_df.at[i, col_to_assign] = st.session_state.cat_selections[row_key]

        st.success("Modifications prises en compte")
        st.session_state["df_categories_mano"] = full_df.copy()
        st.session_state["affectation_success"] = True
        st.write("✅ Catégories mises à jour")
        st.session_state["refresh_after_affectation"] = True
        st.rerun()

    if "df_categories_mano" in st.session_state and st.button("💾 Sauvegarder ce fichier modifié", key="save_full_df"):
        final_full_df = st.session_state["df_categories_mano"]
        
        # Vérification que la colonne est bien remplie
        if final_full_df["categories"].isnull().any():
            st.warning("⚠️ Certaines lignes n'ont pas encore de catégorie.")
        else:
            save_df_to_nextcloud_csv(client, final_full_df, processed_folder, name_processed_df)
            clear_local_folder(local_processed_folder)
            st.success(f"✅ Fichier sauvegardé dans {processed_folder}")
            st.dataframe(final_full_df)
