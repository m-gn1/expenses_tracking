print("🔍 Chargement du module import_files")

try:
    from pathlib import Path
    import pandas as pd
    import streamlit as st
    import os
    from utils.data_loader import extract_all_transactions, extract_cardholder_refs, extract_balance_due_date
    from utils.helpers import concat_dataframes
    from utils.ui_helpers import assign_missing_users, quick_checks
    from utils.ui_helpers import pdf_display, is_fee_adjusted_match
    from datetime import datetime
except Exception as e:
    print("💥 Erreur d'import :", e)


def list_files(RAW_FOLDER, PROCESSED_FOLDER):
    raw_files = [f for f in os.listdir(RAW_FOLDER) if f.lower().endswith(".pdf")]
    processed_files = [f.replace(".csv", ".pdf") for f in os.listdir(PROCESSED_FOLDER) if f.endswith(".csv")]
    return raw_files, processed_files

def list_processed_files(PROCESSED_FOLDER):
    processed_files = [f for f in os.listdir(PROCESSED_FOLDER) if f.lower().endswith(".csv")]
    return processed_files

def process_pdf_file(PROCESSED_FOLDER, file):
    if st.session_state.get("active_file") != file:
        return

    df_temp = st.session_state.get("df_to_process")
    if df_temp is None:
        return
    
    #assign_missing_users(full_df_key="df_to_process", cardholders_key="cardholders")

    df_temp = st.session_state.get("df_to_process")
    if df_temp is not None:# and df_temp["user"].notna().all():
        if df_temp["user"].notna().all():
            if st.button("💾 Sauvegarder ce fichier validé", key=f"save_{file}"):
                output_path = os.path.join(PROCESSED_FOLDER, file.replace(".pdf", ".csv"))
                df_temp.to_csv(output_path, index=False)
                st.success(f"Fichier sauvegardé dans {output_path}")
                del st.session_state["df_to_process"]
                del st.session_state["active_file"]
        else:
            st.warning("Veuillez affecter les utilisateurs manquants avant de sauvegarder.")
            st.dataframe(df_temp, use_container_width=True)
            st.page_link("pages/9999_TEST.py", label="➡️ Aller à l’attribution", icon="👤")
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

            # Store in session
            st.session_state[f"df_{file}"] = df
            st.session_state[f"balance_{file}"] = balance
            st.session_state[f"due_{file}"] = due_date
            st.session_state[f"has_user_{file}"] = has_user
            st.session_state[f"extracted_{file}"] = True

        # Bloc toujours visible si extraction a eu lieu
        if st.session_state.get(f"extracted_{file}", False):
            df = st.session_state[f"df_{file}"]
            balance = st.session_state[f"balance_{file}"]
            due_date = st.session_state[f"due_{file}"]

            quick_checks(df, balance, due_date)

            if is_fee_adjusted_match(df, balance):
                if st.button("✅ Ajuster les frais", key=f"fee_match_{file}"):
                    # DataFrame existant
                    new_row = pd.DataFrame([{
                        "date": df["date"].max(),
                        "amount": 20, 
                        "description": "Monthly Membership Fee ",
                        "source_file": file,
                    }])
                    df = st.session_state[f"df_{file}"]
                    df = pd.concat([df, new_row], ignore_index=True)
                    st.success("✅ Les frais ajustés correspondent au solde.")
                    st.session_state[f"df_{file}"] = df


            st.caption("")
            st.dataframe(df, use_container_width=True)

            if st.session_state[f"has_user_{file}"]:
                cardholders = extract_cardholder_refs(path)
                df["user"] = None
                st.session_state["cardholders"] = list(cardholders.values())
            else:
                df["user"] = "Foyer"
                st.session_state["cardholders"] = []

            st.session_state["df_to_process"] = df
            st.session_state["active_file"] = file
