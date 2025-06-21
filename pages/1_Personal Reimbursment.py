import streamlit as st
import pandas as pd
from utils.data_loader import load_expenses, load_data, filter_by_date


st.title("Personal Reimbursement")
st.write("This app was created by Marie.")

# Define variables
# --- Load data ---

df = load_data()

st.title("💸 Personal Reimbursement to the Common Pot")
st.write("Select a date range to see how much each person needs to pay back to the shared pot (excluding shared expenses).")

# --- Date range filter ---
min_date = df["date"].min().date()
max_date = df["date"].max().date()

start_date, end_date = st.date_input(
    "Select date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# --- Filter by date ---
df_filtered = filter_by_date(df, start_date, end_date)

# --- Exclude shared expenses ("commun") ---
individual_df = df_filtered[df_filtered["user"] != "Foyer"]

# --- Sum of personal expenses ---
personal_totals = individual_df.groupby("user")["amount"].sum().sort_values(ascending=False)

st.subheader("💰 Amount each person must repay to the common pot")
st.dataframe(personal_totals)

# --- Optional total for reference ---
st.caption(f"Total individual expenses: {personal_totals.sum():.2f}€")
