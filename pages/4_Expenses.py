import streamlit as st
import pandas as pd
import numpy as np
import os
import altair as alt
from utils.data_loader import load_data, filter_dataframe_categoriel, add_month


# Load the cleaned data

processed_path = "./data/processed"
name_df = "expenses_data.csv"
total_path = os.path.join(processed_path, name_df)

df = pd.read_csv(total_path)
st.dataframe(df)

# df = load_data()
# df = add_month(df, "date")



st.title("Voici nos depenses")

# --- Filtres interactifs ---
st.sidebar.header("Filters")

available_months = sorted(df["date_source_file"].unique())
available_users = sorted(df["user"].unique())

selected_months = st.sidebar.multiselect(
    "Select months",
    options=available_months,
    default=available_months
)

selected_users = st.sidebar.multiselect(
    "Select users",
    options=available_users,
    default=available_users
)


# --- Apply filters ---

filters = {
    "date_source_file": selected_months,
    "user": selected_users,
}

filtered_df = filter_dataframe_categoriel(df, filters)


# --- Aggregate data ---
# --- Group by month + category ---
monthly_by_category = (
    filtered_df
    .groupby(["date_source_file", "categories"], as_index=False)
    .agg({"amount": "sum"})
)

monthly_users = (
    filtered_df
    .groupby(["date_source_file", "user"], as_index=False)
    .agg({"amount": "sum"})
)


# --- Altair chart ---
chart1 = alt.Chart(monthly_users).mark_bar().encode(
    x=alt.X("date_source_file:N", title="Month", sort=available_months),
    y=alt.Y("amount:Q", title="Total amount (£)"),
    color="user:N",
    tooltip=["date_source_file", "user", "amount"]
).properties(
    title="Monthly Expenses by User",
    width=700,
    height=400
)

chart2 = alt.Chart(monthly_by_category).mark_bar().encode(
    x=alt.X("date_source_file:N", title="Month", axis=alt.Axis(labelAngle=0)),
    y=alt.Y("amount:Q", title="Total Amount (£)"),
    color=alt.Color("categories:N", title="Category"),
    xOffset="categories:N",  # 🔑 CLÉ POUR GROUPÉ
    tooltip=["date_source_file", "categories", "amount"]
).properties(
    width=700,
    height=400,
    title="💰 Monthly Expenses by Category (Grouped)"
)


st.altair_chart(chart1, use_container_width=True)
st.altair_chart(chart2, use_container_width=True)

