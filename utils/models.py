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
