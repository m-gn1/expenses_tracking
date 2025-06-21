import streamlit as st
from utils.data_loader import load_expenses

# Chargement du DataFrame
df = load_expenses()

# Affichage ou utilisation
st.dataframe(df.head())
