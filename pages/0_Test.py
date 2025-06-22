import streamlit as st
from utils.data_loader import load_data, filter_by_date

# Chargement du DataFrame
df = load_data()

st.title("💸 Expenses")
# Affichage ou utilisation

# --- Date range filter ---
min_date_all = df["date"].min().date()
max_date_all = df["date"].max().date()

start_date_all, end_date_all = st.date_input(
    "Select date range",
    value=(min_date_all, max_date_all),
    min_value=min_date_all,
    max_value=max_date_all, 
    key = "dates_all_expenses"
)

# --- Filter by date ---
df_filtered_all = filter_by_date(df, start_date_all, end_date_all)
st.dataframe(df_filtered_all)
