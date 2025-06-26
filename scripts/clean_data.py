import pandas as pd

df = pd.read_csv('data/new_pdf/depenses_mars_avril_mai.csv', sep=';')
# Clean the Amount column
df["amount"] = (
    df["Amount (£)"]
    .str.replace("£", "", regex=False)
    .str.replace(" ", "", regex=False)
    .str.replace(",", ".", regex=False)
    .astype(float)
)

# Clean the Date column
df["date_corr"] = pd.to_datetime(df["Dateold"] + " 2025", format="%d %b %Y")

# Create a new DataFrame with the cleaned data
df_expenses = (
    df[["date_corr", "Description", "Catégorie", "Ref", "amount"]]
    .rename(columns={
        "date_corr": "date",
        "Description": "description",
        "Catégorie": "category",
        "Ref": "user"
    })
)

df_expenses.to_csv("data/processed/expenses_1.csv", index=False)
