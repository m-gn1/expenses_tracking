
print("🔍 Chargement du module data_loader")

try:
    from pathlib import Path
    import pandas as pd
    import pdfplumber
    import re
    from datetime import datetime
except Exception as e:
    print("💥 Erreur d'import :", e)



DATA_PATH = Path("data/processed/expenses_1.csv")
DATA_PATH_PDF = Path("data/new_pdf/2025_05_Monthly BarclayCard Statement.pdf")


def load_data():
    return pd.read_csv(DATA_PATH, parse_dates=["date"])

def add_month(df, date):
    """Load and prepare the cleaned expenses file."""
    df["month"] = df[date].dt.to_period("M").astype(str)
    return df

def filter_by_date(df, start_date, end_date):
    """Return df filtered by start and end date."""
    return df[
        (df["date"] >= pd.to_datetime(start_date)) &
        (df["date"] <= pd.to_datetime(end_date))
    ]

def filter_dataframe_categoriel(df, filters):
    """
    Filtre dynamiquement un DataFrame selon un dictionnaire de filtres.

    Args:
        df (pd.DataFrame): Le DataFrame à filtrer.
        filters (dict): Un dictionnaire où les clés sont les noms de colonnes
                        et les valeurs sont des listes de valeurs autorisées.

    Returns:
        pd.DataFrame: Le DataFrame filtré.
    """
    filtered_df = df.copy()
    for col, values in filters.items():
        if values:  # si la liste n'est pas vide
            filtered_df = filtered_df[filtered_df[col].isin(values)]
    return filtered_df

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


def extract_balance_due_date(fichier):
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
                            r"(\d{2} \w{3})\s+(.+?)\s+£([\d,]+\.\d{2})",
                            buffer
                        )
                        if match:
                            date, desc, amount = match.groups()
                            amount = float(amount.replace(",", ""))
                            transactions.append({
                                "date": date,
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


def extract_transactions_from_line(line, has_user):
    """
    Prend une ligne brute du PDF et extrait toutes les transactions qu'elle contient.
    Retourne une liste de dictionnaires avec date, user, description, amount.
    """

    if has_user:
        pattern = r"(\d{2} \w{3})\s+(\d{3})\s+(.+?)\s+£([\d,]+\.\d{2})"
        matches = list(re.finditer(pattern, line))

        transactions = []
        for match in matches:
            date, cardholder, desc, amount = match.groups()
            if "Payment By Direct Debit" not in desc:
                transactions.append({
                    "date": date.strip(),
                    "cardholder": cardholder.strip(),
                    "description": desc.strip(),
                    "amount": float(amount.replace(",", ""))
                })
    else:
        # Si pas de user, on n'extrait que date, description et montant
        pattern = r"(\d{2} \w{3})\s+(.+?)\s+£([\d,]+\.\d{2})"
        matches = list(re.finditer(pattern, line))
        transactions = []
        for match in matches:
            date, desc, amount = match.groups()
            if "Payment By Direct Debit" not in desc:
                transactions.append({
                    "date": date.strip(),
                    "description": desc.strip(),
                    "amount": float(amount.replace(",", ""))
                })
    return transactions

def extract_all_transactions(pdf_path, has_user):
    transactions = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages[1:len(pdf.pages)-1]:  # Pages contenant les transactions
            width = page.width
            height = page.height

            # Découpe gauche / droite
            left = page.crop((0, 0, width / 2, height))
            right = page.crop((width / 2, 0, width, height))

            for part in [left, right]:
                text = part.extract_text()
                if not text:
                    continue

                lines = text.split("\n")
                for line in lines:
                    extracted = extract_transactions_from_line(line, has_user)
                    transactions.extend(extracted)

    # Convertir en DataFrame trié
    df = pd.DataFrame(transactions)
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"] + " 2025", format="%d %b %Y")
        df = df.sort_values("date").reset_index(drop=True)

    # Mapper le user
    colonnes = ["date", "cardholder", "user", "description", "amount"]

    if has_user:
        ref_to_name = extract_cardholder_refs(pdf_path)
        df["cardholder"] = df["cardholder"].map(ref_to_name)
        df["user"] = None
    else:
        df["cardholder"] = None
        df["user"] = None

    return df[colonnes]


def extract_cardholder_refs(fichier):
    """
    Extrait un dictionnaire {nom utilisateur : référence} depuis un PDF,
    à partir du bloc 'Cardholders and their references'.

    Args:
        pdf_path (str): Chemin vers le fichier PDF

    Returns:
        dict: Dictionnaire des utilisateurs et leur référence
    """
    cardholder_dict = {}

    with pdfplumber.open(fichier) as pdf:
        page1 = pdf.pages[1]

        # 👉 On découpe la page 1 en deux verticalement et on prend la partie gauche
        width = page1.width
        height = page1.height
        left_part = page1.crop((0, 0, width / 2, height))

        # 👉 On extrait le texte uniquement de cette zone
        text = left_part.extract_text()
        lines = text.split("\n")

        # Détection du bloc
        if "Cardholders and their references" in text:
            lines = text.split("\n")
            start = False
            for line in lines:
                if "Cardholders and their references" in line:
                    start = True
                    continue
                if start:
                    match = re.match(r"(.*?)\s+reference[:]? (\d{3})", line.strip())
                    if match:
                        name, ref = match.groups()
                        cardholder_dict[name.strip()] = ref.strip()
                    elif line.strip() == "":
                        break  # fin du bloc
    ref_to_name = {v: k for k, v in cardholder_dict.items()}


    return ref_to_name
