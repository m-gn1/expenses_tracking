import streamlit as st

st.title("📊 Analyse")

if "full_df" in st.session_state:
    df = st.session_state["full_df"]

    st.subheader("Aperçu des données chargées :")
    st.dataframe(df)

    # Tu peux maintenant faire tous tes filtres, visualisations, etc.
else:
    st.warning("Aucune donnée n'a encore été chargée. Va d'abord dans l'onglet 'Data'.")
