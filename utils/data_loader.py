from pathlib import Path
import pandas as pd
import streamlit as st
import pdfplumber
import re
from datetime import datetime

DATA_PATH = Path("data/processed/expenses_1.csv")

@st.cache_data

def load_data():
    return pd.read_csv(DATA_PATH, parse_dates=["date"])

def load_expenses():
    """Load and prepare the cleaned expenses file."""
    df = pd.read_csv(DATA_PATH, parse_dates=["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)
    return df

def filter_by_date(df, start_date, end_date):
    """Return df filtered by start and end date."""
    return df[
        (df["date"] >= pd.to_datetime(start_date)) &
        (df["date"] <= pd.to_datetime(end_date))
    ]


DATA_PATH_PDF = Path("data/raw/2025_05_Monthly BarclayCard Statement.pdf")

def extract_balance_due_date_s(fichier):
    """Load and extract data from a PDF file."""
    new_balance = []
    due_date = []

    with pdfplumber.open(fichier) as pdf:
        page1 = pdf.pages[0]

        # 👉 On découpe la page 1 en deux verticalement et on prend la partie gauche
        width = page1.width
        height = page1.height
        left_part = page1.crop((0, 0, width / 2, height))

        # 👉 On extrait le texte uniquement de cette zone
        text = left_part.extract_text()
        lines = text.split("\n")

        for line in lines:
            if "Your new balance" in line:
                new_balance_raw = line
            if "Please pay by" in line:
                due_date_raw = line

    new_balance_match = re.match(r"(.+?):\s+£?([\d,]+\.\d{2})", new_balance_raw)
    if new_balance_match:
        label, value = new_balance_match.groups()
        label = label.strip()
        amount = float(value.replace(",", ""))  # 👉 conversion en float
        new_balance = {label: amount}

    date_match = re.match(r"(.+?):\s+(\d{1,2} \w+ \d{4})", due_date_raw)
    if date_match:
        label, date_str = date_match.groups()
        label = label.strip()
        parsed_date = datetime.strptime(date_str, "%d %B %Y").strftime("%Y-%m-%d")
        due_date = {label: parsed_date}
    
    return(new_balance, due_date)


def extract_expenses_pdf_1(fichier):

    transactions = []

    with pdfplumber.open(fichier) as pdf:
        for page in pdf.pages[1:len(pdf.pages)-1]:  # pages contenant les transactions
            width = page.width
            height = page.height

            # Découpe la page en deux colonnes : gauche et droite
            left = page.crop((0, 0, width / 2, height))
            right = page.crop((width / 2, 0, width, height))

            for subpage in [left, right]:
                text = subpage.extract_text()
                if not text:
                    continue  # ignorer les blocs vides

                lines = text.split("\n")
                buffer = ""

                for line in lines:
                    buffer += " " + line.strip()

                    # Si la ligne contient £xxx.xx → fin probable de transaction
                    if re.search(r"£[\d,]+\.\d{2}$", line):
                        match = re.search(
                            r"(\d{2} \w{3})\s+(\d{3})\s+(.+?)\s+£([\d,]+\.\d{2})",
                            buffer
                        )
                        if match:
                            date, user, desc, amount = match.groups()
                            amount = float(amount.replace(",", ""))
                            transactions.append({
                                "date": date,
                                "user": user,
                                "description": desc.strip(),
                                "amount": amount
                            })
                        buffer = ""  # Réinitialiser pour la prochaine transaction

    # Créer le DataFrame final
    df = pd.DataFrame(transactions)

    # Convertir la date au bon format avec année fictive pour tri
    df["parsed_date"] = pd.to_datetime(df["date"] + " 2025", format="%d %b %Y")
    df = df.sort_values("parsed_date").reset_index(drop=True)

    # Afficher un aperçu
    return(df)
