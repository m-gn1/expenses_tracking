import os
import streamlit as st
import pandas as pd
import altair as alt
from utils.ui_helpers import clear_cache_on_page_change, display_user_amount_boxes
from utils.new_nextcloud_tools import (
    load_config,
    check_if_existing_processed_file_remote, 
    clear_local_folder,
    save_df_to_nextcloud_csv, 
    )
from utils.nextcloud_helpers import sync_from_nextcloud_to_server
from utils.data_loader import filter_dataframe_categoriel


REMOTE_PROCESSED_PATH = "data/processed/"
FOYER = 'Foyer'


## end config

##### INIT #######
st.session_state.setdefault("connect_validated", None)
st.session_state.setdefault("client", None)
st.session_state.setdefault("working_folder", None)

####### CLEAR CACHE ########
# Identifier cette page par un nom unique
CURRENT_PAGE = "0_7_Expenses.py"  # ex: "Importer", "Analyse", "Résultats"
clear_cache_on_page_change(CURRENT_PAGE, preserve_keys=["connect_validated", "client", "source_folder", "working_folder"])

if st.session_state["connect_validated"]:
    client = st.session_state["client"]
    st.info("🔓 Connecté à NextCloud")
else:
    st.warning("⚠️ Connecte toi à NextCloud")
    st.page_link("pages/0_1_NEW Synchro NC cache working.py", label="🔐 Aller à la page de connexion")

###########################################

###### LOAD CONFIG ######
config = load_config()
if config:
    working_folder = config.get("working_folder")

processed_folder = working_folder+"/"+REMOTE_PROCESSED_PATH
local_processed_folder = os.path.join(".cache/", REMOTE_PROCESSED_PATH)
name_processed_df = "expenses_data.csv"


##### clear cache #####
clear_local_folder(local_processed_folder)
sync_from_nextcloud_to_server(client, processed_folder, local_processed_folder)
existing_df = check_if_existing_processed_file_remote(client, processed_folder, name_processed_df, local_processed_folder)

df = existing_df.drop_duplicates(subset="transaction_ID")

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