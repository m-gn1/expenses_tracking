import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from utils.data_loader import load_data, filter_dataframe_categoriel, add_month


# Load the cleaned data


df = load_data()
df = add_month(df, "date")

st.title("Voici nos depenses")

# --- Filtres interactifs ---
st.sidebar.header("Filters")

available_months = sorted(df["month"].unique())
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
    "month": selected_months,
    "user": selected_users,
}

filtered_df = filter_dataframe_categoriel(df, filters)


# --- Aggregate data ---
# --- Group by month + category ---
monthly_by_category = (
    filtered_df
    .groupby(["month", "category"], as_index=False)
    .agg({"amount": "sum"})
)

monthly_users = (
    filtered_df
    .groupby(["month", "user"], as_index=False)
    .agg({"amount": "sum"})
)


# --- Altair chart ---
chart1 = alt.Chart(monthly_users).mark_bar().encode(
    x=alt.X("month:N", title="Month", sort=available_months),
    y=alt.Y("amount:Q", title="Total amount (£)"),
    color="user:N",
    tooltip=["month", "user", "amount"]
).properties(
    title="Monthly Expenses by User",
    width=700,
    height=400
)

chart2 = alt.Chart(monthly_by_category).mark_bar().encode(
    x=alt.X("month:N", title="Month", axis=alt.Axis(labelAngle=0)),
    y=alt.Y("amount:Q", title="Total Amount (£)"),
    color=alt.Color("category:N", title="Category"),
    xOffset="category:N",  # 🔑 CLÉ POUR GROUPÉ
    tooltip=["month", "category", "amount"]
).properties(
    width=700,
    height=400,
    title="💰 Monthly Expenses by Category (Grouped)"
)


st.altair_chart(chart1, use_container_width=True)
st.altair_chart(chart2, use_container_width=True)

