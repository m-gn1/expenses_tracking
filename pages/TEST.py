import streamlit as st
import base64
from utils.ui_helpers import pdf_display

st.title("📊 Analyse")

if "full_df" in st.session_state:
    df = st.session_state["full_df"]

    st.subheader("Aperçu des données chargées :")
    st.dataframe(df)

    # Tu peux maintenant faire tous tes filtres, visualisations, etc.
else:
    st.warning("Aucune donnée n'a encore été chargée. Va d'abord dans l'onglet 'Data'.")



total_expenses = 2
min_date = 3
max_date = 4
balance_value = 5
due_value =  6


pdf_path = "./data/raw/2025_03_Monthly BarclayCard Statement.pdf"

pdf_display(pdf_path)
