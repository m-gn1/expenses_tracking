import streamlit as st
import base64
from utils.ui_helpers import pdf_display
import pandas as pd

st.page_link("pages/0_Importer_fichiers.py", label="➡️ Aller à l’attribution", icon="👤")
df_temp = st.session_state.get("df_to_process")
st.dataframe(df_temp, use_container_width=True)

def analyse():
    st.title("📊 Analyse")



    if st.button("Changer de page"):
        # Nouveau bouton pour aller à la page d’attribution
        st.markdown("[➡️ Aller à la page d'attribution des utilisateurs](./Data)", unsafe_allow_html=True)



    # Création d'un DataFrame factice
    df = pd.DataFrame({
        "date": pd.to_datetime([
            "2025-03-15", "2025-03-16", "2025-03-18", "2025-03-20"
        ]),
        "description": [
            "Courses Monoprix", "Abonnement Netflix", "Essence Total", "Dîner restaurant"
        ],
        "amount": [52.34, 13.99, 44.60, 82.10],
        "category": ["Courses", "Loisir", "Transport", "Restaurant"],
        "user": [None, None, None, None]  # à remplir dans l’app
    })

    if st.button("📄 Ouvrir le DataFrame"):
        st.session_state["df_open"] = True

    if st.session_state.get("df_open", False):
        st.markdown("### ✍️ Attribution des users")

        updated_rows = []

        for i, row in df.iterrows():
            with st.expander(f"Ligne {i+1} - {row['description']}"):
                st.write(row.drop("user"))  # affiche le reste
                selected_user = st.selectbox(
                    "Affecter un user :", 
                    options=["Foyer", "Alice", "Bob", "Marie"],  # ou ta liste dynamique
                    key=f"user_select_{i}"
                )
                updated_rows.append((i, selected_user))

        if st.button("💾 Enregistrer les affectations"):
            for i, user in updated_rows:
                df.at[i, "user"] = user
            st.dataframe(df, use_container_width=True)
            #df.to_csv("data/processed/my_cleaned_file.csv", index=False)
            st.success("✅ Données enregistrées")

analyse()