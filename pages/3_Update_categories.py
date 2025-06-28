import streamlit as st
import pandas as pd
import os 
from utils.import_files import list_processed_files, display_file_processing_block, import_pdf_file, display_processed_summary, save_processed_files
from utils.ui_helpers import clear_cache_on_page_change,manage_categories
from utils.models import classify_expenses_learning

CURRENT_PAGE = "2_Personal Reimbursment.py"  # ex: "Importer", "Analyse", "Résultats"
clear_cache_on_page_change(CURRENT_PAGE)
###########################################@

#st.markdown("## WARNING SUBTEST")

IMPORTED_FOLDER = "./data/imported_data"
CATEFORISED_FOLDER = "./data/categorised_data"

processed_path = "./data/processed"
name_df = "expenses_data.csv"
total_path = os.path.join(processed_path, name_df)

df = pd.read_csv(total_path)

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
                    st.session_state["categories"],  # ou une liste de ton choix
                    existing_category=row["categories"] if pd.notnull(row["categories"]) else None
                ),
                axis=1
            )
            st.dataframe (df)
            st.dataframe(df["predicted_category"].value_counts())
            st.dataframe(df["categories"].value_counts())




#df["categories"] = df["description"].apply(lambda x: classify_expenses(x, st.session_state["categories"]))   