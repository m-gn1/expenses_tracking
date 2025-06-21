from pathlib import Path
import pandas as pd
import streamlit as st

DATA_PATH = Path("data/processed/expenses_1.csv")

@st.cache_data

def load_data():
    return pd.read_csv(DATA_PATH, parse_dates=["date"])

def load_expenses():
    """Load and prepare the cleaned expenses file."""
    df = pd.read_csv(DATA_PATH, parse_dates=["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)
    return df

def filter_by_date(df, start_date, end_date):
    """Return df filtered by start and end date."""
    return df[
        (df["date"] >= pd.to_datetime(start_date)) &
        (df["date"] <= pd.to_datetime(end_date))
    ]
