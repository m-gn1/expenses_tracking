import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

# Chargement de la clé API depuis le fichier .env
load_dotenv()
client = OpenAI() 
# Charge ton CSV

# Liste de catégories
categories = ["Food & Beverage","Furniture","Transport","Shopping","Other","Tax & household expenses","Entertainment"]

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
- Monthly membership fee is a barclays fee, is should be assign to "Tax & household expenses"
Give only the name of the category."""
    
    response = client.chat.completions.create(
        model="gpt-4o",
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