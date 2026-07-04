import pandas as pd
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

def classify_expenses_learning(desc, categories, existing_category=None):
    load_dotenv()
    client = OpenAI()

    categories_list = ", ".join(categories)

    prompt = f"""Here is my category list: {categories_list}.
From the following description: "{desc}",
assign the most suited category. To help you, here are some specificities: 
- When it comes to shop items for the house, put the "Furniture" category (such as John Lewis)
- When it comes to dinner at a restaurant or drinks, put the "Entertainment" category
- Monthly membership fee is a Barclays fee, it should be assigned to "Home & Bills"
"""

    if existing_category:
        prompt += f'\nThis description has already been classified before as: "{existing_category}". You should respect this assignment unless there is a clear mismatch.'

    prompt += "\nReturn only the name of the category."

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message.content.strip()


def classify_expenses_learning_require_key(desc, categories, existing_category=None):
    if "openai_api_key" not in st.session_state or not st.session_state["openai_api_key"]:
        st.warning("Merci de saisir ta clé OpenAI ci-dessus.")
        st.stop()

    # Crée le client avec la clé saisie
    client = OpenAI(api_key=st.session_state["openai_api_key"])

    categories_list = ", ".join(categories)

    prompt = f"""Here is my category list: {categories_list}.
From the following description: "{desc}",
assign the most suited category. To help you, here are some specificities: 
- When it comes to shop items for the house, put the "Furniture" category (such as John Lewis)
- When it comes to dinner at a restaurant or drinks, put the "Entertainment" category
- Monthly membership fee is a Barclays fee, it should be assigned to "Home & Bills
- John Lewis is a shop for home items, it should be assigned to "Furniture
- Gails, Waitrose, Bayleys should be assigned to Food & Beverage
- Use previously assigned categories to help you classify new descriptions."
"""

    if existing_category:
        prompt += f'\nThis description has already been classified before as: "{existing_category}". You should respect this assignment unless there is a clear mismatch.'

    prompt += "\nReturn only the name of the category."

    # Appel OpenAI
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Erreur lors de l'appel à OpenAI : {e}")
        return None


