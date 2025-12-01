print("🔍 Chargement du module ui_helpers")

try:
    import streamlit as st
    import pandas as pd
    import os
    import base64
    #from utils.data_loader import extract_all_transactions, extract_cardholder_refs
except Exception as e:
    print("💥 Erreur d'import :", e)


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

# def extract_selected_data(selected_files, options, folder):
#     dfs = []
#     all_cardholders = set()

#     for file in selected_files:
#         path = os.path.join(folder, file)
#         has_user = options[file]

#         df = extract_all_transactions(path, has_user=has_user)
#         df["source_file"] = file

#         if has_user:
#             cardholders = extract_cardholder_refs(path)
#             all_cardholders.update(cardholders.values())
#             df["user"] = None  # à compléter manuellement
#         else:
#             df["user"] = "foyer"

#         dfs.append(df)

#     return dfs, all_cardholders

### TO DO : key cardholder ne fonctionnne pas, verfiier le session. state #####

def assign_missing_users(common_user, full_df_key="full_df", cardholders_key="cardholders"):
    full_df = st.session_state.get(full_df_key)
    cardholders = common_user + sorted(list(st.session_state.get(cardholders_key, [])))

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
            label = f"{date_str} | {row['description']} | {row['amount']} £"

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
        st.session_state["refresh_after_affectation"] = True


def show_quick_checks(df, balance, due_date):
    total_expenses = df["amount"].sum()
    min_date = df["date"].min().date()
    max_date = df["date"].max().date()
    balance_value = list(balance.values())[0]
    due_value = list(due_date.values())[0]

    st.markdown(f"""
<div style="border-radius: 8px; padding: 1em; background-color: rgba(0, 123, 255, 0.1);">
    <div>🔎 Quick Checks<div>
    <div style="height: 0.7em;"></div>
    </div>
    <div style="display: flex; justify-content: start; gap: 11em;">
        <div>💰 <strong>Total expenses:</strong> {total_expenses:.2f}£</div>
        <div>💰 <strong>Balance from PDF:</strong> {balance_value}£</div>
    </div>
    <div style="display: flex; justify-content: start; gap: 9em; margin-top: 0.5em;">
        <div>📅 <strong>From:</strong> {min_date} → {max_date}</div>
        <div>📅 <strong>Due date:</strong> {due_value}</div>
    </div>
</div>
    """, unsafe_allow_html=True)

def pdf_display(pdf_path):
    """
    Display a PDF file in Streamlit.
    """
    with open(pdf_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')

    display_module = f"""
    <iframe 
        src="data:application/pdf;base64,{base64_pdf}" 
        width="100%" 
        height="300px" 
        type="application/pdf"
        style="border: 1px solid #ccc; border-radius: 8px;"
    ></iframe>
"""    
    st.markdown(display_module, unsafe_allow_html=True)


def quick_checks(df, balance, due_date):
    total_expenses = df["amount"].sum()
    min_date = df["date"].min().date()
    max_date = df["date"].max().date()
    balance_value = list(balance.values())[0]
    due_value = list(due_date.values())[0]


    st.markdown(f"""
<div style="border-radius: 8px; padding: 1em; background-color: rgba(0, 123, 255, 0.1);">
    <div>🔎 Quick Checks<div>
    <div style="height: 0.7em;"></div>
    </div>
    <div style="display: flex; justify-content: start; gap: 11em;">
        <div>💰 <strong>Total expenses:</strong> {total_expenses:.2f}£</div>
        <div>💰 <strong>Balance from PDF:</strong> {balance_value}£</div>
    </div>
    <div style="display: flex; justify-content: start; gap: 9em; margin-top: 0.5em;">
        <div>📅 <strong>From:</strong> {min_date} → {max_date}</div>
        <div>📅 <strong>Due date:</strong> {due_value}</div>
    </div>
    <div style="height: 0.7em;"></div>
    </div>
</div>
    """, unsafe_allow_html=True)


def is_fee_adjusted_match(df, balance, fee=20):
    total_expenses = round(df["amount"].sum(), 2)
    balance_value = round(list(balance.values())[0],2)
    
    """
    Vérifie si le solde correspond aux dépenses + un éventuel frais fixe.

    Retourne True uniquement si balance = total_expenses + fee (arrondis à 2 décimales).
    """
    if total_expenses == balance_value:
        st.success("✅ Le solde correspond aux dépenses totales.")
        return False  # condition 1
    elif balance_value == total_expenses + fee:
        st.info(f"ℹ️ Le solde correspond aux dépenses totales + un frais de {fee}£.")
        return True   # condition 2
    else:
        st.error("❌ Le solde ne correspond pas aux dépenses totales ni aux dépenses + frais.")
        return False  # condition 3


def clear_cache_on_page_change(current_page: str, preserve_keys=None):
    """
    Supprime les éléments de st.session_state si on change de page.
    
    :param current_page: Nom unique de la page actuelle (ex: "Import", "Analyse", etc.)
    :param preserve_keys: Liste de clés à ne pas supprimer (ex: ["previous_page", "config"])
    """
    if preserve_keys is None:
        preserve_keys = ["previous_page"]

    previous_page = st.session_state.get("previous_page")

    if previous_page and previous_page != current_page:
        for key in list(st.session_state.keys()):
            if key not in preserve_keys:
                del st.session_state[key]

    st.session_state["previous_page"] = current_page


def display_user_amount_boxes (df, col_user, col_amount):
    cols = st.columns(len(df))
    for i, (_, row) in enumerate(df.iterrows()):
        user = row[col_user]
        amount = row[col_amount]

        with cols[i]:
            st.markdown(f"""
            <br>
            <div style="border: 1px solid #ccc; border-radius: 10px; padding: 1em; background-color: #323e54;">
                <h4 style="margin-bottom: 0.5em;">👤 {user}</h4>
                <p style="font-size: 1.1em;">💸 <strong>{amount:.2f} £</strong></p>
            </div>
            <br>
            """, unsafe_allow_html=True)
    return

import streamlit as st

def manage_categories():
    # Initialisation si besoin
    if "list_categories" not in st.session_state:
        st.session_state["list_categories"] = [
            "Food & Beverage", "Furniture", "Transport", "Shopping",
            "Other", "Home & Bills", "Entertainment", "Vin", "Restaurant"
        ]

    st.markdown("### 📂 Gérer les catégories")

    # 🔠 Ajout de catégorie
    with st.form("add_category_form", clear_on_submit=True):
        new_cat = st.text_input("➕ Ajouter une nouvelle catégorie", "")
        submitted = st.form_submit_button("✅ Ajouter")
        if submitted:
            if new_cat:
                if new_cat not in st.session_state["list_categories"]:
                    st.session_state["list_categories"].append(new_cat)
                    st.success(f"✅ '{new_cat}' a été ajouté.")
                else:
                    st.warning("⚠️ Cette catégorie existe déjà.")
            else:
                st.warning("⚠️ Entrez un nom valide.")

    # 🧹 Suppression de catégorie
    st.markdown("#### 📌 Liste des catégories")
    cols = st.columns(4)

    for i, cat in enumerate(st.session_state["list_categories"]):
        col = cols[i % 4]
        with col:
            st.markdown(
                f"""
                <div style='background-color: #e0e0e0; color: black; padding: 6px 12px;
                            margin: 4px 0; border-radius: 20px; font-size: 0.9em;
                            display: flex; justify-content: space-between; align-items: center;'>
                    <span>{cat}</span>
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button(f"✖", key=f"remove_{cat}"):
                st.session_state["list_categories"].remove(cat)
                st.rerun()


#❌