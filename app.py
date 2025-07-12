import streamlit as st

st.set_page_config(page_title="Home Page", layout="wide")
st.title("🚀 Accueil – Suivi de dépenses")

st.markdown("""
Bienvenue dans l'application de traitement et de catégorisation des dépenses.  
Voici les 5 étapes à suivre dans l'ordre :
""")

pages_info = [
    {
        "title": "1. Importer les fichiers",
        "description": "Charge les fichiers PDF de dépenses et les transforme en tableaux exploitables.",
        "page": "pages/1_Importer_fichiers.py"
    },
    {
        "title": "2. Attribute users",
        "description": "Permet d'attribuer les dépenses à chaque user",
        "page": "pages/2_Attribute_users.py"
    },
    {
        "title": "3_Personal Reimbursment",
        "description": "Annonce qui doit rembourser quoi, et l'état de remboursement.",
        "page": "pages/3_Personal Reimbursment.py"
    },
    {
        "title": "4. Update categories",
        "description": "Automatise la création des catégories, et permet à l'utilisateur de les changer à la main",
        "page": "pages/4_Update_categories.py"
    },
    {
        "title": "5. Expenses",
        "description": "Permet de suivre les dépenses",
        "page": "pages/5_Expenses.py"
    }
]

cols = st.columns(3)


    #st.page_link("pages/1_Importer_fichiers.py", label="➡️ Aller à l’import")


for i, page in enumerate(pages_info):
    col = cols[i % 3]
    with col:
        st.markdown(f"""
        <div style='border: 1px solid #ccc; border-radius: 12px; padding: 1em; margin: 1em 0;
                    background-color: #323e54; height: 200px; display: flex; flex-direction: column;
                    justify-content: space-between; box-shadow: 2px 2px 8px rgba(0,0,0,0.05);'>
            <h4 style='margin-bottom: 0.5em;'>📘 {page["title"]}</h4>
            <p style='font-size: 0.9em;'>{page["description"]}</p>
        </div>
        """, unsafe_allow_html=True)

        # 👉 Ajoute le lien Streamlit en dehors du bloc HTML pour éviter les conflits
        st.page_link(page["page"], label="➡️ Ouvrir", icon="🔗")
