from utils.nextcloud_tools import connect_to_nextcloud
from utils.nextcloud_helpers import sync_from_nextcloud_to_server
import streamlit as st


# 👤 Connexion
client = connect_to_nextcloud()

if client: 
# 📁 Chemins
    remote_folder = "/test_streamlit"
    local_folder = "./data"  # ou "./cache", etc.

    # 🔄 Synchronisation
    sync_from_nextcloud_to_server(client, remote_folder, local_folder)

    # 🧾 Tu peux ensuite lire tes fichiers localement
    import pandas as pd
    df = pd.read_csv("./data/expenses_data.csv")
    st.dataframe(df)
