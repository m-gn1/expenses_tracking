import os
from difflib import SequenceMatcher
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
from utils.models import classify_expenses_learning_require_key

REMOTE_PROCESSED_PATH = "data/processed/"

## end config

##### INIT #######
st.session_state.setdefault("connect_validated", None)
st.session_state.setdefault("client", None)
st.session_state.setdefault("working_folder", None)

####### CLEAR CACHE ########
# Identifier cette page par un nom unique
CURRENT_PAGE = "0_6_Attribute categories.py"  # ex: "Importer", "Analyse", "Résultats"
clear_cache_on_page_change(CURRENT_PAGE, preserve_keys=["connect_validated", "client", "source_folder", "working_folder"])

if st.session_state["connect_validated"]:
    client = st.session_state["client"]
    st.info("🔓 Connecté à NextCloud")
else:
    st.warning("⚠️ Connecte toi à NextCloud")
    st.page_link("pages/0_1_Connection to NextCloud.py", label="🔐 Aller à la page de connexion")

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


def normalize_description(desc):
    return str(desc).lower().strip()


def build_category_mapping_from_descriptions(df, valid_categories):
    mapping_df = df[df["categories"].notna()].copy()
    mapping_df = mapping_df[mapping_df["categories"].isin(valid_categories)].copy()

    if mapping_df.empty:
        return {}

    mapping_df["description_clean"] = mapping_df["description"].apply(normalize_description)

    return (
        mapping_df
        .groupby("description_clean")["categories"]
        .agg(lambda x: x.value_counts().idxmax())
        .to_dict()
    )


def find_best_description_match(description, category_mapping, fuzzy_threshold=0.82):
    description_norm = normalize_description(description)

    if not description_norm or description_norm == "nan":
        return None, None, None

    for known_description, category in category_mapping.items():
        if known_description in description_norm or description_norm in known_description:
            return category, known_description, "contains"

    best_category = None
    best_description = None
    best_score = 0

    for known_description, category in category_mapping.items():
        score = SequenceMatcher(None, description_norm, known_description).ratio()
        if score > best_score:
            best_score = score
            best_category = category
            best_description = known_description

    if best_score >= fuzzy_threshold:
        return best_category, best_description, f"fuzzy {best_score:.0%}"

    return None, None, None


def prefill_categories_from_existing_data(df, valid_categories):
    df_prefilled = df.copy()

    if "predicted_category" not in df_prefilled.columns:
        df_prefilled["predicted_category"] = None

    df_prefilled["matched_description"] = None
    df_prefilled["matching_method"] = None

    category_mapping = build_category_mapping_from_descriptions(df_prefilled, valid_categories)

    mask_missing_category = df_prefilled["categories"].isna()

    for idx, row in df_prefilled.loc[mask_missing_category].iterrows():
        category, matched_description, matching_method = find_best_description_match(
            row["description"],
            category_mapping
        )

        if category is not None:
            df_prefilled.at[idx, "predicted_category"] = category
            df_prefilled.at[idx, "matched_description"] = matched_description
            df_prefilled.at[idx, "matching_method"] = matching_method

    return df_prefilled, category_mapping

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
    mode_categorisation = st.radio(
        "Comment veux-tu catégoriser les transactions ?",
        options=[
            "🤖 IA puis vérification manuelle",
            "🧠 Pré-remplissage depuis l'existant puis vérification manuelle",
            "✍🏻 Vérification manuelle uniquement"
        ],
        key="mode_categorisation"
    )

    manage_categories()

    if mode_categorisation == "🤖 IA puis vérification manuelle":
        with st.expander("🤖 Je catégorise avec l'IA", expanded=True):
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
                    st.dataframe(df)
                    st.dataframe(df["predicted_category"].value_counts())
                    st.dataframe(df["categories"].value_counts())
                    st.session_state["df_categories_ia"] = df.copy()
            else:
                st.warning("⚠️ Ajoute une clé OpenAI pour utiliser la catégorisation IA.")

    elif mode_categorisation == "🧠 Pré-remplissage depuis l'existant puis vérification manuelle":
        valid_categories = st.session_state["list_categories"]

        if st.session_state.get("df_categories_mode") != mode_categorisation:
            df_prefilled, category_mapping = prefill_categories_from_existing_data(df, valid_categories)
            st.session_state["df_categories_mano"] = df_prefilled.copy()
            st.session_state["df_categories_mode"] = mode_categorisation
            st.session_state.cat_selections = {
                f"cat_{idx}": row["predicted_category"]
                for idx, row in df_prefilled.iterrows()
                if pd.notna(row.get("predicted_category", None))
                and row.get("predicted_category", None) in valid_categories
                and pd.isna(row.get("categories", None))
            }
        else:
            df_prefilled = st.session_state["df_categories_mano"].copy()
            category_mapping = build_category_mapping_from_descriptions(df_prefilled, valid_categories)

        nb_prefilled = df_prefilled.loc[
            df_prefilled["categories"].isna() & df_prefilled["predicted_category"].notna()
        ].shape[0]

        st.info(
            f"🧠 Pré-remplissage activé : {nb_prefilled} ligne(s) ont été pré-remplies "
            "avec un matching contains/fuzzy sur les descriptions déjà catégorisées."
        )

        with st.expander("Voir les lignes pré-remplies", expanded=False):
            st.dataframe(
                df_prefilled.loc[
                    df_prefilled["categories"].isna() & df_prefilled["predicted_category"].notna(),
                    ["date", "transaction_ID", "user", "description", "amount", "predicted_category", "matched_description", "matching_method"]
                ],
                use_container_width=True
            )

    else:
        if st.session_state.get("df_categories_mode") != mode_categorisation:
            df_manual = df.copy()
            if "predicted_category" not in df_manual.columns:
                df_manual["predicted_category"] = None
            st.session_state["df_categories_mano"] = df_manual.copy()
            st.session_state["df_categories_mode"] = mode_categorisation
            st.session_state.cat_selections = {}
        st.info("✍🏻 Mode manuel activé : tu peux choisir les catégories toi-même ci-dessous.")

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

    if full_df is None:
        st.stop()

    rows_to_fill = full_df[full_df[col_to_assign].isna()].copy()
    if rows_to_fill.empty:
        st.success("✅ Toutes les lignes ont une catégorie. Tu peux sauvegarder le fichier.")

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
            predicted_category = row.get("predicted_category", None)
            matched_description = row.get("matched_description", None)
            matching_method = row.get("matching_method", None)

            default = st.session_state.cat_selections.get(row_key, predicted_category)
            date_str = row["date"] if isinstance(row["date"], str) else row["date"].strftime("%Y-%m-%d")

            label = f"{date_str} | {row['transaction_ID']} | {row['user']} | {row['description']} | {row['amount']} £"
            if pd.notna(predicted_category):
                label += f" | proposition: {predicted_category}"
            if pd.notna(matched_description) and pd.notna(matching_method):
                label += f" ({matching_method} avec: {matched_description})"

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
        final_full_df = st.session_state["df_categories_mano"].copy()

        # Sécurité : si certaines catégories sont encore vides mais qu'une catégorie prédite existe,
        # on l'utilise avant la sauvegarde. Cela évite que le mode pré-remplissage reste bloqué
        # si l'utilisateur n'a pas cliqué sur "Valider les affectations" avant de sauvegarder.
        if "predicted_category" in final_full_df.columns:
            mask_to_autofill = (
                final_full_df["categories"].isna()
                & final_full_df["predicted_category"].notna()
                & final_full_df["predicted_category"].isin(st.session_state["list_categories"])
            )
            final_full_df.loc[mask_to_autofill, "categories"] = final_full_df.loc[mask_to_autofill, "predicted_category"]

        # Vérification que la colonne est bien remplie
        if final_full_df["categories"].isnull().any():
            missing_rows = final_full_df[final_full_df["categories"].isnull()].copy()
            st.warning(f"⚠️ {len(missing_rows)} ligne(s) n'ont pas encore de catégorie.")
            st.dataframe(
                missing_rows[["date", "transaction_ID", "user", "description", "amount", "predicted_category"]],
                use_container_width=True
            )
        else:
            st.session_state["df_categories_mano"] = final_full_df.copy()
            save_df_to_nextcloud_csv(client, final_full_df, processed_folder, name_processed_df)
            clear_local_folder(local_processed_folder)
            st.success(f"✅ Fichier sauvegardé dans {processed_folder}")
            st.dataframe(final_full_df)
