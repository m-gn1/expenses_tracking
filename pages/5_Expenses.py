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

### Affciher tables filtrée ###

selected_df = df.copy()
selected_df = selected_df[["transaction_ID", "date_source_file", "date", "user", "categories","description" ,"amount"]]

st.title("📊 Données filtrables")

# Filtres
with st.expander("🔍 Filtres", expanded=True):
    col1, col2, col3 = st.columns(3)

    with col1:
        nom_filter = st.multiselect("Name", options=selected_df["user"].unique(), default=list(selected_df["user"].unique()))
    with col2:
        cat_filter = st.multiselect("Categories", options=selected_df["categories"].unique(), default=list(selected_df["categories"].unique()))
    with col3:
        #date_range = st.date_input("Plage of dates", [selected_df["date"].min(), selected_df["date"].max()])
        date_filter = st.multiselect("Dates", options=selected_df["date_source_file"].unique(), default=list(selected_df["date_source_file"].unique()))


# Application des filtres
filtered_df = selected_df[
    df["user"].isin(nom_filter) &
    df["categories"].isin(cat_filter) &
    df["date_source_file"].isin(date_filter)
    #df["date"].between(pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1]))
]

# Affichage
st.markdown("### 📄 Données filtrées")
st.dataframe(filtered_df, use_container_width=True)
