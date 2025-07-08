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

import pandas as pd
import streamlit as st
import plotly.express as px
from streamlit_plotly_events import plotly_events

# # Exemple de DataFrame
# df = pd.DataFrame({
#     "date_source_file": ["2024-01", "2024-01", "2024-02", "2024-02"],
#     "categories": ["Food", "Transport", "Food", "Transport"],
#     "amount": [100, 50, 120, 70]
# })

# Crée une colonne combinée pour l'affichage
df["custom_label"] = df["categories"]

# Crée le graphique interactif avec customdata pour passer la catégorie
fig = px.bar(
    df,
    x="date_source_file",
    y="amount",
    color="categories",
    barmode="group",
    title="💰 Monthly Expenses by Category",
    hover_data=["categories", "amount"],
)

# Ajoute customdata pour chaque barre (catégorie)
for trace in fig.data:
    trace.customdata = df[df["categories"] == trace.name]["categories"]
    trace.hovertemplate += "<br>Catégorie: %{customdata[0]}"

# Affiche le graphique avec interaction
selected_points = plotly_events(fig, click_event=True, select_event=False)

# Analyse la sélection
if selected_points:
    selected_x = selected_points[0]["x"]
    selected_cat = selected_points[0]["customdata"][0]  # ✅ Précis maintenant

    st.markdown(f"### 📋 Détails pour **{selected_cat}** en **{selected_x}**")
    filtered_df = df[
        (df["date_source_file"] == selected_x) &
        (df["categories"] == selected_cat)
    ]
    st.dataframe(filtered_df)
else:
    st.info("👆 Clique sur une barre pour voir les détails.")



import streamlit as st
import pandas as pd
import altair as alt

# Exemple : Altair selection
selection = alt.selection_point(fields=["date_source_file", "categories"])

chart3 = alt.Chart(monthly_by_category).mark_bar().encode(
    x=alt.X("date_source_file:N", title="Month", axis=alt.Axis(labelAngle=0)),
    y=alt.Y("amount:Q", title="Total Amount (£)"),
    color=alt.Color("categories:N", title="Category"),
    xOffset="categories:N",
    tooltip=["date_source_file", "categories", "amount"],
    opacity=alt.condition(selection, alt.value(1), alt.value(0.3))
).add_params(
    selection
).properties(
    width=700,
    height=400,
    title="💰 Monthly Expenses by Category (Grouped)"
)

st.altair_chart(chart3, use_container_width=True)
st.session_state["Select"] = selection
st.write(selection)

# 🔍 Sélection utilisateur
selected = st.session_state.get("Select")

if selected and "date_source_file" in selected and "categories" in selected:
    date_selected = selected["date_source_file"]
    cat_selected = selected["categories"]

    st.markdown(f"### 📋 Détails pour **{cat_selected}** en **{date_selected}**")
    
    filtered_df = df[
        (df["date_source_file"] == date_selected) & 
        (df["categories"] == cat_selected)
    ]
    st.dataframe(filtered_df)
else:
    st.info("ℹ️ Clique sur une barre du graphique pour afficher les détails.")


########

import altair as alt
import pandas as pd
import streamlit as st

# Exemple de données
df = pd.DataFrame({
    "date_source_file": ["2024-01", "2024-01", "2024-02", "2024-02"],
    "categories": ["Food", "Transport", "Food", "Transport"],
    "amount": [100, 50, 120, 70]
})

# 1. Création de la sélection Altair (sur 2 champs)
selection = alt.selection_point(fields=["date_source_file", "categories"], name="Select")

# 2. Construction du graphique
chart = alt.Chart(df).mark_bar().encode(
    x=alt.X("date_source_file:N", title="Month", axis=alt.Axis(labelAngle=0)),
    y=alt.Y("amount:Q", title="Total Amount (£)"),
    color=alt.Color("categories:N", title="Category"),
    xOffset="categories:N",  # groupement par catégorie
    tooltip=["date_source_file", "categories", "amount"],
    opacity=alt.condition(selection, alt.value(1), alt.value(0.2))  # met en évidence la sélection
).add_params(
    selection
).properties(
    width=700,
    height=400,
    title="💰 Monthly Expenses by Category (Grouped)"
)

# 3. Affichage du graphique dans Streamlit
st.altair_chart(chart, use_container_width=True)

# 4. Filtrage conditionnel selon la sélection (captée dans session_state)
selected = st.session_state.get("Select")

if selected:
    st.write("🎯 Sélection :", selected)
    selected_month = selected.get("date_source_file")
    selected_category = selected.get("categories")

    filtered_df = df[
        (df["date_source_file"] == selected_month) &
        (df["categories"] == selected_category)
    ]
    st.markdown(f"### 📋 Détails pour **{selected_category}** en **{selected_month}**")
    st.dataframe(filtered_df)
else:
    st.info("👆 Clique sur une barre pour afficher les détails.")




#######

import altair as alt
import pandas as pd
import streamlit as st

df = pd.DataFrame({
    "date_source_file": ["2024-01", "2024-01", "2024-02", "2024-02"],
    "categories": ["Food", "Transport", "Food", "Transport"],
    "amount": [100, 50, 120, 70]
})

selection = alt.selection_point(fields=["date_source_file", "categories"], name="select_bar")

chart = alt.Chart(df).mark_bar().encode(
    x="date_source_file:N",
    y="amount:Q",
    color="categories:N",
    xOffset="categories:N",
    tooltip=["date_source_file", "categories", "amount"],
    opacity=alt.condition(selection, alt.value(1), alt.value(0.3))
).add_params(selection).properties(
    width=700,
    height=400
)

st.altair_chart(chart, use_container_width=True)

selected = st.session_state.get("select_bar")
if selected:
    st.write("🎯 Sélection :", selected)
    date = selected.get("date_source_file")
    cat = selected.get("categories")
    st.dataframe(df[(df["date_source_file"] == date) & (df["categories"] == cat)])
