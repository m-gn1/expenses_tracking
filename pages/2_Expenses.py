import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from utils.data_loader import load_expenses, load_data, filter_by_date


# Load the cleaned data



df = load_expenses()


st.title("Voici nos depenses")
st.markdown(
    """ 

 regarde ce que je peux faire avec Streamlit !
    """
)

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
filtered_df = df[
    (df["month"].isin(selected_months)) &
    (df["user"].isin(selected_users))
]

# --- Aggregate data ---
grouped_df = filtered_df.groupby(["month", "user"], as_index=False)["amount"].sum()



# --- Aggregate data ---
grouped_df = filtered_df.groupby(["month", "user"], as_index=False)["amount"].sum()

# --- Altair chart ---
chart = alt.Chart(grouped_df).mark_bar().encode(
    x=alt.X("month:N", title="Month", sort=available_months),
    y=alt.Y("amount:Q", title="Total amount (£)"),
    color="user:N",
    tooltip=["month", "user", "amount"]
).properties(
    title="Monthly Expenses by User",
    width=700,
    height=400
)

st.altair_chart(chart, use_container_width=True)

# --- Optional table display ---
with st.expander("Show aggregated data"):
    st.dataframe(grouped_df)