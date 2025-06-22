import streamlit as st
import pandas as pd
import os
from utils.data_loader import extract_all_transactions, extract_cardholder_refs


def get_pdf_files(folder_path):
    return [f for f in os.listdir(folder_path) if f.lower().endswith(".pdf")]

def display_file_selection(files):
    return st.multiselect("📂 Sélectionne les fichiers PDF :", files)

def get_extraction_options(files):
    st.markdown("### ⚙️ Options d'extraction")
    options = {}
    for file in files:
        with st.expander(f"Options pour {file}"):
            has_user = st.checkbox(
                "Ce fichier contient une section 'Cardholders and their references'",
                key=f"user_col_{file}"
            )
            options[file] = has_user
    return options

def extract_selected_data(selected_files, options, folder):
    dfs = []
    all_cardholders = set()

    for file in selected_files:
        path = os.path.join(folder, file)
        has_user = options[file]

        df = extract_all_transactions(path, has_user=has_user)
        df["source_file"] = file

        if has_user:
            cardholders = extract_cardholder_refs(path)
            all_cardholders.update(cardholders.values())
            df["user"] = None  # à compléter manuellement
        else:
            df["user"] = "foyer"

        dfs.append(df)

    return dfs, all_cardholders

### TO DO : key cardholder ne fonctionnne pas, verfiier le session. state #####

def assign_missing_users(full_df_key="full_df", cardholders_key="cardholders"):
    full_df = st.session_state.get(full_df_key)
    cardholders = ["Foyer"] + sorted(list(st.session_state.get(cardholders_key, [])))

    if full_df is None or full_df["user"].notna().all():
        return

    rows_to_fill = full_df[full_df["user"].isna()].copy()
    if rows_to_fill.empty:
        return

    # ✅ Afficher message de succès si besoin
    if st.session_state.get("affectation_success"):
        st.success("✅ Toutes les lignes ont été mises à jour avec succès 🎉")
        del st.session_state["affectation_success"]
        st.dataframe(full_df, use_container_width=True)
        return

    st.markdown("### 🖊️ Affecter les utilisateurs manquants")

    if "user_selections" not in st.session_state:
        st.session_state.user_selections = {}

    with st.form("user_assignment_form"):
        for i, row in rows_to_fill.iterrows():
            row_key = f"user_{i}"
            default = st.session_state.user_selections.get(row_key, "Foyer")
            date_str = row["date"] if isinstance(row["date"], str) else row["date"].strftime("%Y-%m-%d")
            label = f"{date_str} | {row['description']} | {row['amount']} €"

            selected = st.selectbox(
                label,
                options=cardholders,
                index=cardholders.index(default) if default in cardholders else 0,
                key=row_key
            )
            st.session_state.user_selections[row_key] = selected

        submitted = st.form_submit_button("✅ Valider les affectations")

    if submitted:
        for i, row in rows_to_fill.iterrows():
            row_key = f"user_{i}"
            full_df.at[i, "user"] = st.session_state.user_selections[row_key]

        st.session_state[full_df_key] = full_df.copy()
        st.session_state["affectation_success"] = True
        st.rerun()