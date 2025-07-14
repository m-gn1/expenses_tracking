import streamlit as st
from utils import nextcloud_tools as nc

st.set_page_config(page_title="🔗 Connexion Nextcloud", layout="centered")
st.title("☁️ Synchronisation Nextcloud")

def init_session():
    st.session_state.setdefault("working_folder", None)
    st.session_state.setdefault("source_folder", None)


init_session()
client = nc.connect_to_nextcloud()

#### Verfiier si fichier de conf existe. 
if client:
    # Étape 1 : vérifier la config
    source_folder, working_folder = None, None

    # Étape 2 : si pas de config → choix manuels
    if not (source_folder and working_folder):
        remote_path = st.text_input("📁 Dossier distant à vérifier/créer", value="/fichiers")
        if st.button("📂 Vérifier/créer le dossier distant"):
            nc.ensure_remote_folder_exists(st.session_state["client"], remote_path)

        source_folder = nc.choose_remote_source_folder()
        working_folder = nc.choose_remote_working_folder()
        st.session_state["source_folder"] = source_folder
        st.session_state["working_folder"] = working_folder
        st.write(st.session_state["source_folder"])
        st.write(st.session_state["working_folder"])
        #save_config(source_folder, working_folder)

# #### Verifier quels dossiers existent / je veux creer
# if client:
#     remote_path = st.text_input("📁 Dossier distant à vérifier/créer", value="/fichiers")
#     if st.button("📂 Vérifier/créer le dossier distant"):
#         nc.ensure_remote_folder_exists(st.session_state["client"], remote_path)


# ### creer mes dossiers. 
# if client:
#     source_folder = nc.choose_remote_source_folder()
#     working_folder = nc.choose_remote_working_folder()
#     st.session_state["source_folder"] = source_folder
#     st.session_state["working_folder"] = working_folder
#     st.write(st.session_state["source_folder"])
#     st.write(st.session_state["working_folder"])

import os
import json

def load_config():
    if st.session_state["working_folder"]:
        CONFIG_NAME = "config_nextcloud.json"
        CONFIG_PATH = os.path.join(st.session_state["working_folder"], CONFIG_NAME)
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r") as f:
                return json.load(f)
        return None

def verify_config(client):
    config = load_config()
    if config:
        working_folder = config.get("working_folder")
        source_folder = config.get("source_folder")
        if working_folder and source_folder:
            return source_folder, working_folder
    return None, None

def save_config(source_folder, working_folder):
    if st.session_state["working_folder"]:
        CONFIG_NAME = "config_nextcloud.json"
        CONFIG_PATH = os.path.join(st.session_state["working_folder"], CONFIG_NAME)
        config = {"source_folder": source_folder, "working_folder": working_folder}
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f)

