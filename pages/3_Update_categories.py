import streamlit as st
import pandas as pd
import os 
from utils.import_files import list_processed_files, display_file_processing_block, import_pdf_file, display_processed_summary, save_processed_files
from utils.ui_helpers import clear_cache_on_page_change,manage_categories
from utils.models import classify_expenses_learning

CURRENT_PAGE = "2_Personal Reimbursment.py"  # ex: "Importer", "Analyse", "Résultats"
clear_cache_on_page_change(CURRENT_PAGE)
###########################################@



IMPORTED_FOLDER = "./data/imported_data"
CATEFORISED_FOLDER = "./data/categorised_data"

processed_path = "./data/processed"
name_df = "expenses_data.csv"
total_path = os.path.join(processed_path, name_df)

df = pd.read_csv(total_path)
#st.markdown("## WARNING SUBTEST")
#df = df [:5]

#df = df_test[:10].copy()
st.dataframe (df)
st.title("📦 Updating categories")

st.dataframe(df["categories"].value_counts())

if df["categories"].notnull().all():
    st.success("✅ Tout est catégorisé")
else: 
    with st.expander("🤖 Je catégorise avec l'IA", expanded=True):        
        manage_categories()
        if st.button("⚙️ Lançons la machine", key="ia"):
            df["predicted_category"] = df.apply(
                lambda row: classify_expenses_learning(
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
            output_path = os.path.join(processed_path, name_df)
            final_full_df.to_csv(output_path, index=False)
            st.success(f"✅ Fichier sauvegardé dans {output_path}")
            st.dataframe(final_full_df)
