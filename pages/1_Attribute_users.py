import streamlit as st
import pandas as pd
from utils.import_files import list_files

RAW_FOLDER = "./data/raw"
IMPORTED_FOLDER = "./data/imported_data"

st.title("👤 Attribute users to expenses")
raw_files, imported_files = list_files(RAW_FOLDER, IMPORTED_FOLDER)
