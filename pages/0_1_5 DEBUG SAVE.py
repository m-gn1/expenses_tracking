import pandas as pd
import os
import streamlit as st

REMOTE_IMPORTED_FOLDER = "data/imported_data/"

df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
st.dataframe(df)
output_path_imported_cache = os.path.join(".cache/", REMOTE_IMPORTED_FOLDER, "data.csv")
df.to_csv(output_path_imported_cache, index=False)
st.success("csv dans cache")


df_test = pd.read_csv(output_path_imported_cache)
st.dataframe(df_test)
