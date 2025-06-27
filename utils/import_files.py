print("🔍 Chargement du module import_files")

try:
    from pathlib import Path
    import pandas as pd
    import os
    import shutil
    import streamlit as st
    from utils.data_loader import extract_all_transactions, extract_cardholder_refs, extract_balance_due_date
    from utils.helpers import concat_dataframes#, save_csv_move_pdf
    #from utils.ui_helpers import assign_missing_users, quick_checks, pdf_display, is_fee_adjusted_match
    from datetime import datetime
    
except Exception as e:
    print("💥 Erreur d'import :", e)


def list_files(NEW_PDF, IMPORTED_FOLDER):
    raw_files = [f for f in os.listdir(NEW_PDF) if f.lower().endswith(".pdf")]
    processed_files = [f.replace(".csv", ".pdf") for f in os.listdir(IMPORTED_FOLDER) if f.endswith(".csv")]
    return raw_files, processed_files


def list_pdf_files(NEW_PDF, PROCESSED_PDF):
    new_pdf = [f for f in os.listdir(NEW_PDF) if f.lower().endswith(".pdf")]
    processed_pdf = [f for f in os.listdir(PROCESSED_PDF) if f.lower().endswith(".pdf")]
    return new_pdf, processed_pdf

def list_processed_files(IMPORTED_FOLDER):
    processed_files = [f for f in os.listdir(IMPORTED_FOLDER) if f.lower().endswith(".csv")]
    return processed_files

def import_pdf_file(IMPORTED_FOLDER, NEW_PDF, PROCESSED_PDF,file):
    if st.session_state.get("active_file") != file:
        return

    df_temp = st.session_state.get("df_to_process")
    if df_temp is None:
        return
    
    #assign_missing_users(full_df_key="df_to_process", cardholders_key="cardholders")

    df_temp = st.session_state.get("df_to_process")
    if df_temp is not None:
        if st.button("💾 Sauvegarder ce fichier validé", key=f"save_{file}"):
            output_path = os.path.join(IMPORTED_FOLDER, file.replace(".pdf", ".csv"))
            st.success(f"Fichier sauvegardé dans {output_path}")
            #on fera la fonction plus tard save_csv_move_pdf(IMPORTED_FOLDER, NEW_PDF, PROCESSED_PDF,file, df_temp)
            df_temp.to_csv(output_path, index=False)
            source = os.path.join(NEW_PDF, file)
            destination = os.path.join(PROCESSED_PDF, file)
            shutil.copy(source, destination)
            #st.success(f"Fichier bougé dans {destination}")
            
            del st.session_state["df_to_process"]
            del st.session_state["active_file"]
            st.rerun()
        # else:
        #     st.warning("Veuillez affecter les utilisateurs manquants avant de sauvegarder.")
        #     #st.dataframe(df_temp, use_container_width=True)
        #     st.page_link("pages/9999_TEST.py", label="➡️ Aller à l’attribution", icon="👤")
        #     st.rerun()


def display_processed_summary(IMPORTED_FOLDER):
    processed_files = [f for f in os.listdir(IMPORTED_FOLDER) if f.endswith(".csv")]
    if not processed_files:
        return

    st.markdown("---")
    st.markdown("## 📊 Aperçu des fichiers traités")
    dfs = []
    for f in processed_files:
        df = pd.read_csv(os.path.join(IMPORTED_FOLDER, f))
        dfs.append(df)

    full_df = concat_dataframes(*dfs)
    st.session_state["full_df"] = full_df
    st.dataframe(full_df, use_container_width=True)

def save_processed_files(IMPORTED_FOLDER):
    if st.button("💾 Sauvegarder les données traitées", key="save_processed_files"):
        if "full_df" not in st.session_state:
            st.warning("Aucune donnée à sauvegarder.")
            return

        full_df = st.session_state["full_df"]
        output_path = os.path.join(IMPORTED_FOLDER, f"processed_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        full_df.to_csv(output_path, index=False)
        st.success(f"✅ Données sauvegardées dans {output_path}")

        st.caption(f"Total expenses: {full_df['amount'].sum():.2f}£")

        del st.session_state["full_df"]


def display_file_processing_block(NEW_PDF, file, is_done):

    if is_done:
        st.subheader(f"🗂 {file}")
        st.success("✅ Déjà traité")
        return
    
    st.subheader(f"🗂 {file}")

    with st.expander("🔧 Traiter ce fichier", expanded=True):
        path = os.path.join(NEW_PDF, file)
        pdf_display(path)

        has_user = st.checkbox("Contient la section 'Cardholders and their references' ?", key=f"user_col_{file}")

        handle_extraction_button(file, path, has_user)

                # Suite logique après extraction
        if not st.session_state.get(f"extracted_{file}", False):
            return

        df = st.session_state[f"df_{file}"]
        balance = st.session_state[f"balance_{file}"]
        due_date = st.session_state[f"due_{file}"]

        quick_checks(df, balance, due_date)

        handle_fee_adjustment_button(file)

        df = st.session_state[f"df_{file}"]

        if st.session_state.get(f"show_df_{file}", False):
            df = st.session_state[f"df_{file}"]

            # ✅ Affiche le message de succès si présent
            if st.session_state.get(f"fee_adjusted_success_{file}", False):
                st.success("✅ Les frais ajustés ont été ajoutés.")
                del st.session_state[f"fee_adjusted_success_{file}"]

            st.caption("📊 Données extraites :")
            st.dataframe(df, use_container_width=True)
            st.session_state["df_to_process"] = df


        st.session_state["df_to_process"] = df
        st.session_state["active_file"] = file


def handle_extraction_button(file, path, has_user):
    if st.button("🔍 Extraire et afficher les données", key=f"extract_{file}"):
        df = extract_all_transactions(path, has_user=has_user)
        df["source_file"] = file
        df["reimbursed"] = None
        file_prefix = file[:7]
        df = df.reset_index(drop=True)
        df.insert(0, "transaction_ID", df.index.map(lambda i: f"{file_prefix}_{i+1}"))
        balance, due_date = extract_balance_due_date(path)
        st.session_state[f"df_{file}"] = df
        st.session_state[f"balance_{file}"] = balance
        st.session_state[f"due_{file}"] = due_date
        st.session_state[f"has_user_{file}"] = has_user
        st.session_state[f"extracted_{file}"] = True
        st.session_state[f"show_df_{file}"] = True


def handle_fee_adjustment_button(file):
    df = st.session_state[f"df_{file}"]
    balance = st.session_state[f"balance_{file}"]

    if is_fee_adjusted_match(df, balance):
        if st.button("✅ Ajuster les frais", key=f"fee_match_{file}"):
            new_row = pd.DataFrame([{
                "date": df["date"].max(),
                "amount": 20,
                "description": "Monthly Membership Fee",
                "source_file": file,
            }])
            df = pd.concat([df, new_row], ignore_index=True)
            st.session_state["df_to_process"] = df
            st.session_state[f"df_{file}"] = df
            st.session_state[f"show_df_{file}"] = True
            st.session_state[f"fee_adjusted_success_{file}"] = True  # 🔥 flag temporaire
            st.rerun()




################ UI_HELPERS ###############

#import streamlit as st
#import pandas as pd
#import os
import base64
#from utils.data_loader import extract_all_transactions, extract_cardholder_refs


def get_pdf_files(folder_path):
    return [f for f in os.listdir(folder_path) if f.lower().endswith(".pdf")]

def get_csv_files(folder_path):
    return [f for f in os.listdir(folder_path) if f.lower().endswith(".csv")]

def bank_get_csv_files(folder_path):
    return [f for f in os.listdir(folder_path) if f.lower().endswith(".csv")]


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

# def assign_missing_users(common_user, full_df_key="full_df", cardholders_key="cardholders"):
#     full_df = st.session_state.get(full_df_key)
#     cardholders = common_user + sorted(list(st.session_state.get(cardholders_key, [])))

#     if full_df is None or full_df["user"].notna().all():
#         return

#     rows_to_fill = full_df[full_df["user"].isna()].copy()
#     if rows_to_fill.empty:
#         return

#     # ✅ Afficher message de succès si besoin
#     if st.session_state.get("affectation_success"):
#         st.success("✅ Toutes les lignes ont été mises à jour avec succès 🎉")
#         del st.session_state["affectation_success"]
#         st.dataframe(full_df, use_container_width=True)
#         return

#     st.markdown("### 🖊️ Affecter les utilisateurs manquants")

#     if "user_selections" not in st.session_state:
#         st.session_state.user_selections = {}

#     with st.form("user_assignment_form"):
#         for i, row in rows_to_fill.iterrows():
#             row_key = f"user_{i}"
#             default = st.session_state.user_selections.get(row_key, "Foyer")
#             date_str = row["date"] if isinstance(row["date"], str) else row["date"].strftime("%Y-%m-%d")
#             label = f"{date_str} | {row['description']} | {row['amount']} €"

#             selected = st.selectbox(
#                 label,
#                 options=cardholders,
#                 index=cardholders.index(default) if default in cardholders else 0,
#                 key=row_key
#             )
#             st.session_state.user_selections[row_key] = selected

#         submitted = st.form_submit_button("✅ Valider les affectations")

#     if submitted:
#         for i, row in rows_to_fill.iterrows():
#             row_key = f"user_{i}"
#             full_df.at[i, "user"] = st.session_state.user_selections[row_key]

#         st.session_state[full_df_key] = full_df.copy()
#         st.session_state["affectation_success"] = True
#         st.session_state["refresh_after_affectation"] = True


# def show_quick_checks(df, balance, due_date):
#     total_expenses = df["amount"].sum()
#     min_date = df["date"].min().date()
#     max_date = df["date"].max().date()
#     balance_value = list(balance.values())[0]
#     due_value = list(due_date.values())[0]

#     st.markdown(f"""
# <div style="border-radius: 8px; padding: 1em; background-color: rgba(0, 123, 255, 0.1);">
#     <div>🔎 Quick Checks<div>
#     <div style="height: 0.7em;"></div>
#     </div>
#     <div style="display: flex; justify-content: start; gap: 11em;">
#         <div>💰 <strong>Total expenses:</strong> {total_expenses:.2f}£</div>
#         <div>💰 <strong>Balance from PDF:</strong> {balance_value}£</div>
#     </div>
#     <div style="display: flex; justify-content: start; gap: 9em; margin-top: 0.5em;">
#         <div>📅 <strong>From:</strong> {min_date} → {max_date}</div>
#         <div>📅 <strong>Due date:</strong> {due_value}</div>
#     </div>
# </div>
#     """, unsafe_allow_html=True)

# def pdf_display(pdf_path):
#     """
#     Display a PDF file in Streamlit.
#     """
#     with open(pdf_path, "rb") as f:
#         base64_pdf = base64.b64encode(f.read()).decode('utf-8')

#     display_module = f"""
#     <iframe 
#         src="data:application/pdf;base64,{base64_pdf}" 
#         width="100%" 
#         height="300px" 
#         type="application/pdf"
#         style="border: 1px solid #ccc; border-radius: 8px;"
#     ></iframe>
# """    
#     st.markdown(display_module, unsafe_allow_html=True)


# def quick_checks(df, balance, due_date):
#     total_expenses = df["amount"].sum()
#     min_date = df["date"].min().date()
#     max_date = df["date"].max().date()
#     balance_value = list(balance.values())[0]
#     due_value = list(due_date.values())[0]


#     st.markdown(f"""
# <div style="border-radius: 8px; padding: 1em; background-color: rgba(0, 123, 255, 0.1);">
#     <div>🔎 Quick Checks<div>
#     <div style="height: 0.7em;"></div>
#     </div>
#     <div style="display: flex; justify-content: start; gap: 11em;">
#         <div>💰 <strong>Total expenses:</strong> {total_expenses:.2f}£</div>
#         <div>💰 <strong>Balance from PDF:</strong> {balance_value}£</div>
#     </div>
#     <div style="display: flex; justify-content: start; gap: 9em; margin-top: 0.5em;">
#         <div>📅 <strong>From:</strong> {min_date} → {max_date}</div>
#         <div>📅 <strong>Due date:</strong> {due_value}</div>
#     </div>
#     <div style="height: 0.7em;"></div>
#     </div>
# </div>
#     """, unsafe_allow_html=True)


# def is_fee_adjusted_match(df, balance, fee=20):
#     total_expenses = round(df["amount"].sum(), 2)
#     balance_value = round(list(balance.values())[0],2)
    
#     """
#     Vérifie si le solde correspond aux dépenses + un éventuel frais fixe.

#     Retourne True uniquement si balance = total_expenses + fee (arrondis à 2 décimales).
#     """
#     if total_expenses == balance_value:
#         st.success("✅ Le solde correspond aux dépenses totales.")
#         return False  # condition 1
#     elif balance_value == total_expenses + fee:
#         st.info(f"ℹ️ Le solde correspond aux dépenses totales + un frais de {fee}£.")
#         return True   # condition 2
#     else:
#         st.error("❌ Le solde ne correspond pas aux dépenses totales ni aux dépenses + frais.")
#         return False  # condition 3





