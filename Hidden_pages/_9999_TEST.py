import streamlit as st
import base64
from utils.ui_helpers import pdf_display
import pandas as pd
import os



import streamlit as st


# Initialisation si besoin
if "categories" not in st.session_state:
    st.session_state["categories"] = [
        "Food & Beverage", "Furniture", "Transport", "Shopping",
        "Other", "Tax & household expenses", "Entertainment"
    ]

st.markdown("### 📂 Gérer les catégories")

# 🔠 Ajout de catégorie
with st.form("add_category_form", clear_on_submit=True):
    new_cat = st.text_input("➕ Ajouter une nouvelle catégorie", "")
    submitted = st.form_submit_button("✅ Ajouter")
    if submitted:
        if new_cat:
            if new_cat not in st.session_state["categories"]:
                st.session_state["categories"].append(new_cat)
                st.success(f"✅ '{new_cat}' a été ajouté.")
            else:
                st.warning("⚠️ Cette catégorie existe déjà.")
        else:
            st.warning("⚠️ Entrez un nom valide.")

# 🧹 Suppression de catégorie
st.markdown("#### 📌 Liste des catégories")
cols = st.columns(4)

for i, cat in enumerate(st.session_state["categories"]):
    col = cols[i % 4]
    with col:
        st.markdown(
            f"""
            <div style='background-color: #e0e0e0; color: black; padding: 6px 12px;
                        margin: 4px 0; border-radius: 20px; font-size: 0.9em;
                        display: flex; justify-content: space-between; align-items: center;'>
                <span>{cat}</span>
                <form method="post">
                    <button type="submit" name="remove_{cat}" style='background: none;
                            border: none; color: red; font-weight: bold; margin-left: 10px;
                            cursor: pointer;'></button>
                </form>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Suppression en bouton (hacké via checkbox fallback)
        if st.button(f"❌", key=f"remove_{cat}"):
            st.session_state["categories"].remove(cat)
            st.rerun()

















st.markdown("## OLD")
st.page_link("pages/0_Importer_fichiers.py", label="➡️ Aller à l’attribution", icon="👤")
df_temp = st.session_state.get("df_to_process")
st.dataframe(df_temp, use_container_width=True)
st.warning("cette page n'est pas utile")


processed_path = "./data/processed"
name_df = "expenses_data.csv"

st.write("df qui remplacerea")
df = pd.read_csv(os.path.join(processed_path, name_df))
st.dataframe(df)

unique_values = df["source_file"].unique()


selected_values = []

# with st.container():
#     cols = st.columns(len(unique_values))
#     for i, val in enumerate(unique_values):
#         if cols[i].checkbox(val):
#             selected_values.append(val)

# if selected_values:
#     filtered_df = df[df["source_file"].isin(selected_values)]
#     st.dataframe(filtered_df)
# else:
#     st.info("✅ Coche une ou plusieurs options pour filtrer le tableau.")



default_checked = ["2025_03_Monthly BarclayCard Statement.pdf", "2025_04_Monthly BarclayCard Statement.pdf"]

# Stocke les valeurs sélectionnées
selected_values = []

with st.container():
    cols = st.columns(len(unique_values))
    for i, val in enumerate(unique_values):
        is_checked = val in default_checked  # ✅ test si on doit précocher
        if cols[i].checkbox(val, value=is_checked):
            selected_values.append(val)

if selected_values:
    filtered_df = df[df["source_file"].isin(selected_values)]
    st.dataframe(filtered_df)
else:
    st.info("✅ Coche une ou plusieurs options pour filtrer le tableau.")











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