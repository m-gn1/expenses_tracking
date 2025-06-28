import pandas as pd
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

# Chargement de la clé API depuis le fichier .env
load_dotenv()
client = OpenAI() 
# Charge ton CSV

categories = []
# Fonction de catégorisation
def classify_description(desc):
    # Chargement de la clé API depuis le fichier .env
    load_dotenv()
    client = OpenAI() 
    prompt = f"""Here is my category list : {", ".join(categories)}.
    From the following description : "{desc}",
    Assign the most suited category. To help you, here are some specificities: 
- When it comes to shop items for the house, put the "Furniture" category (such as John Lewis)
- When it comes to dinner to restaurant, or drinks, put the "Entertainment" category
- Monthly membership fee is a barclays fee, is should be assign to "Home & Bills"
Give only the name of the category."""
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message.content




# Voici une liste de catégories : ["Food & Beverage","Furniture","Transport","Shopping","Other","Tax","Entertainment"]
#     À partir de la description suivante : "['Speakenglishwell.co.uk, Leek', 'SQ *Arome Duke Street, London',
#        'John Lewis, London', 'www.Johnlewis.com, 03456 049 049',
#        'Barbersmiths, London e', 'Maison Estelle, London',
#        'Ryanair D0000000G1D93E,', 'Boots 1940, Stanstead Air e',
#        'Stn Wdf Main, Bassingbourn e', 'Tfl Travel CH, Tfl.Gov.UK/CP e',
#        'National Express Limit, Birmingham',
#        'BA Inflight Sales, Harmondsworth e',
#        'www.Westminster.Gov.UK, London', 'Monthly Membership Fee']", donne la meilleure catégorie possible de cette liste.
#     Donne uniquement le nom de la catégorie.



def classify_expenses(desc, categories):
    load_dotenv()
    client = OpenAI()

    # Initialise le cache s'il n'existe pas encore
    if "classification_cache" not in st.session_state:
        st.session_state["classification_cache"] = {}

    # Retourne le résultat si déjà classé
    if desc in st.session_state["classification_cache"]:
        return st.session_state["classification_cache"][desc]

    prompt = f"""Here is my category list: {", ".join(categories)}.
From the following description: "{desc}",
assign the most suited category. To help you, here are some specificities: 
- When it comes to shop items for the house, put the "Furniture" category (such as John Lewis)
- When it comes to dinner to restaurant, or drinks, put the "Entertainment" category
- Monthly membership fee is a Barclays fee, it should be assigned to "Home & Bills"
Give only the name of the category."""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    category = response.choices[0].message.content.strip()

    # Stocke le résultat dans le cache
    st.session_state["classification_cache"][desc] = category
    return category




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
