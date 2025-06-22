import streamlit as st
import pandas as pd
from utils.data_loader import load_expenses, load_data, filter_by_date


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
    max_value=max_date, 
    key = "dates_personal_reimbursement"
)

# --- Filter by date ---
df_filtered = filter_by_date(df, start_date, end_date)

# --- Exclude shared expenses ("commun") ---
individual_df = df_filtered[df_filtered["user"] != "Foyer"]

# --- Sum of personal expenses ---
personal_totals = individual_df.groupby("user")["amount"].sum().sort_values(ascending=False)

st.subheader("💰 Amount spent per person individually")
st.dataframe(personal_totals)

# --- Optional total for reference ---
st.caption(f"Total individual expenses: {personal_totals.sum():.2f}£")


# --- Amount to be reimbursed to the common pot ---
st.subheader("💸 Amount to be reimbursed to the common pot")


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


# --- Sum of all expenses ---
totals = df_filtered_all["amount"].sum() + 20

st.caption(f"Total expenses: {totals:.2f}£")

st.subheader("💰 Amount each person must repay to the common pot")

tot_to_reimburse = totals - personal_totals.sum()
nb_users = individual_df["user"].nunique()

df_to_reimburse = tot_to_reimburse/nb_users + personal_totals
st.dataframe(df_to_reimburse)
