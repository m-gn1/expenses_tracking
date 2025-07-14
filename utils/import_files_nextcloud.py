try:
    import os
    import streamlit as st
    import shutil

    
except Exception as e:
    print("💥 Erreur d'import :", e)

from utils.import_files import (
    pdf_display,
    handle_extraction_button,
    quick_checks,
    handle_fee_adjustment_button)

from utils.new_nextcloud_tools import copy_file_nextcloud, save_df_to_nextcloud_csv

from utils.debug import list_files_in_folder

def download_pdf(client, remote_folder, file_name, local_subfolder):
    """
    Télécharge un PDF depuis Nextcloud dans le dossier .cache/IMPORTED_FOLDER et l'affiche.

    Args:
        client (Client): Instance WebDAV connectée.
        remote_folder (str): Chemin distant dans Nextcloud (ex: "/Marie/Londres_shared").
        file_name (str): Nom du fichier PDF (ex: "facture.pdf").
        local_subfolder (str): Nom du sous-dossier local dans .cache (par défaut "IMPORTED_FOLDER").
    """
    local_folder = os.path.join(".cache", local_subfolder)
    os.makedirs(local_folder, exist_ok=True)

    remote_path = f"{remote_folder.rstrip('/')}/{file_name}"
    local_path = os.path.join(local_folder, file_name)

    try:
        client.download_sync(remote_path=remote_path, local_path=local_path)
        st.success(f"📥 Fichier téléchargé : {file_name}")
    except Exception as e:
        st.error(f"❌ Erreur lors du téléchargement de {file_name} : {e}")

def display_file_processing_block(client, remote_folder, local_subfolder, file, is_done):

    if is_done:
        st.subheader(f"🗂 {file}")
        st.success("✅ Déjà traité")
        return
    
    else:
        st.subheader(f"🗂 {file}")

        with st.expander("🔧 Traiter ce fichier", expanded=True):
            download_pdf(client, remote_folder, file, local_subfolder)
            path = os.path.join(local_subfolder, file)
            st.write("GROS DEBUG")
            st.write(path)
            st.write(local_subfolder)
            st.write("lister fichier dans dossier")
            list_files_in_folder(local_subfolder)
            st.write("fin liste")
            # pdf_display(path)

            # has_user = st.checkbox("Contient la section 'Cardholders and their references' ?", key=f"user_col_{file}")

            # handle_extraction_button(file, path, has_user)

            #         # Suite logique après extraction
            # if not st.session_state.get(f"extracted_{file}", False):
            #     return

            # df = st.session_state[f"df_{file}"]
            # balance = st.session_state[f"balance_{file}"]
            # due_date = st.session_state[f"due_{file}"]

            # quick_checks(df, balance, due_date)

            # handle_fee_adjustment_button(file)

            # df = st.session_state[f"df_{file}"]

            # if st.session_state.get(f"show_df_{file}", False):
            #     df = st.session_state[f"df_{file}"]

            #     # ✅ Affiche le message de succès si présent
            #     if st.session_state.get(f"fee_adjusted_success_{file}", False):
            #         st.success("✅ Les frais ajustés ont été ajoutés.")
            #         del st.session_state[f"fee_adjusted_success_{file}"]

            #     st.caption("📊 Données extraites :")
            #     st.dataframe(df, use_container_width=True)
            #     st.session_state["df_to_process"] = df


            # st.session_state["df_to_process"] = df
            # st.session_state["active_file"] = file


### logique de la fonction 



def import_pdf_file(client, source_folder, working_folder, IMPORTED_FOLDER, NEW_PDF, PROCESSED_PDF,file):
    if st.session_state.get("active_file") != file:
        return

    df_temp = st.session_state.get("df_to_process")
    if df_temp is None:
        return

    df_temp = st.session_state.get("df_to_process")
    if df_temp is not None:
        if st.button("💾 Sauvegarder ce fichier validé", key=f"save_{file}"):
            # enregistrer le df dans cache_imported
            output_path_imported_cache = os.path.join(".cache/", IMPORTED_FOLDER, file.replace(".pdf", ".csv"))
            df_temp.to_csv(output_path_imported_cache, index=False)
            st.success(f"Fichier sauvegardé dans {output_path_imported_cache}")
            # enregistrer le df dans remote_imported
            save_df_to_nextcloud_csv(client, df_temp, os.path.join(working_folder, IMPORTED_FOLDER), file.replace(".pdf", ".csv"))
            # move le file de new à processed dans cache
            source_cache = os.path.join(NEW_PDF, file)
            destination = os.path.join(PROCESSED_PDF, file)
            shutil.copy(source_cache, destination)
            st.success(f"Fichier bougé dans {destination}")
            # move le file de new à processed dans remote
            copy_file_nextcloud(client, source_folder, os.path.join(working_folder, PROCESSED_PDF), file)
                
            del st.session_state["df_to_process"]
            del st.session_state["active_file"]
            st.rerun()