print("🔍 Chargement du module import_files")

try:
    from pathlib import Path
    import pandas as pd
    import streamlit as st
    import os
    from utils.data_loader import extract_all_transactions, extract_cardholder_refs, extract_balance_due_date
    from utils.helpers import concat_dataframes
    from utils.ui_helpers import assign_missing_users, quick_checks
    from utils.ui_helpers import pdf_display
    from datetime import datetime
except Exception as e:
    print("💥 Erreur d'import :", e)


def list_files(RAW_FOLDER, PROCESSED_FOLDER):
    raw_files = [f for f in os.listdir(RAW_FOLDER) if f.lower().endswith(".pdf")]
    processed_files = [f.replace(".csv", ".pdf") for f in os.listdir(PROCESSED_FOLDER) if f.endswith(".csv")]
    return raw_files, processed_files


def display_file_processing_block(RAW_FOLDER, file, is_done):
    if is_done:
        st.subheader(f"🗂 {file}")
        st.success("✅ Déjà traité")
        return

    st.subheader(f"🗂 {file}")
    with st.expander("🔧 Traiter ce fichier", expanded=True):
        path = os.path.join(RAW_FOLDER, file)
        pdf_display(path)
        has_user = st.checkbox("Contient la section 'Cardholders and their references' ?", key=f"user_col_{file}")

        if st.button("🔍 Extraire et afficher les données", key=f"extract_{file}"):
            df = extract_all_transactions(path, has_user=has_user)
            df["source_file"] = file
            balance, due_date = extract_balance_due_date(path)
            quick_checks(df, balance, due_date)
 
            st.caption("")
            st.dataframe(df, use_container_width=True)

            if has_user:
                cardholders = extract_cardholder_refs(path)
                df["user"] = None
                st.session_state["cardholders"] = list(cardholders.values())
            else:
                df["user"] = "Foyer"
                st.session_state["cardholders"] = []

            st.session_state["df_to_process"] = df
            st.session_state["active_file"] = file


def process_pdf_file(PROCESSED_FOLDER, file):
    if st.session_state.get("active_file") != file:
        return

    df_temp = st.session_state.get("df_to_process")
    if df_temp is None:
        return
    
    assign_missing_users(full_df_key="df_to_process", cardholders_key="cardholders")

    df_temp = st.session_state.get("df_to_process")
    if df_temp is not None and df_temp["user"].notna().all():
        if st.button("💾 Sauvegarder ce fichier validé", key=f"save_{file}"):
            output_path = os.path.join(PROCESSED_FOLDER, file.replace(".pdf", ".csv"))
            df_temp.to_csv(output_path, index=False)
            st.success(f"Fichier sauvegardé dans {output_path}")
            del st.session_state["df_to_process"]
            del st.session_state["active_file"]
            st.rerun()


def display_processed_summary(PROCESSED_FOLDER):
    processed_files = [f for f in os.listdir(PROCESSED_FOLDER) if f.endswith(".csv")]
    if not processed_files:
        return

    st.markdown("---")
    st.markdown("## 📊 Aperçu des fichiers traités")
    dfs = []
    for f in processed_files:
        df = pd.read_csv(os.path.join(PROCESSED_FOLDER, f))
        dfs.append(df)

    full_df = concat_dataframes(*dfs)
    st.session_state["full_df"] = full_df
    st.dataframe(full_df, use_container_width=True)

def save_processed_files(PROCESSED_FOLDER):
    if st.button("💾 Sauvegarder les données traitées", key="save_processed_files"):
        if "full_df" not in st.session_state:
            st.warning("Aucune donnée à sauvegarder.")
            return

        full_df = st.session_state["full_df"]
        output_path = os.path.join(PROCESSED_FOLDER, f"processed_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        full_df.to_csv(output_path, index=False)
        st.success(f"✅ Données sauvegardées dans {output_path}")

        st.caption(f"Total expenses: {full_df['amount'].sum():.2f}£")

        del st.session_state["full_df"]