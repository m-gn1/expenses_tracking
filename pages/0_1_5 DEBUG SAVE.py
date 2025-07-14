import os
import pandas as pd
import streamlit as st
from fpdf import FPDF
import base64

# Crée un DataFrame simple
df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
st.dataframe(df)

# Définir les chemins
REMOTE_IMPORTED_FOLDER = "imported_data/"  # adapte si nécessaire
cache_folder = os.path.join(".cache", REMOTE_IMPORTED_FOLDER)
os.makedirs(cache_folder, exist_ok=True)

output_path_pdf = os.path.join(cache_folder, "data.pdf")

# ✅ Créer un PDF à partir du DataFrame
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", size=12)
        self.cell(200, 10, txt="Export PDF", ln=True, align="C")

    def table(self, data_frame):
        self.set_font("Arial", size=10)
        col_widths = [40] * len(data_frame.columns)
        row_height = 10

        # En-têtes
        for col_name in data_frame.columns:
            self.cell(col_widths[0], row_height, col_name, border=1)
        self.ln()

        # Lignes
        for i in range(len(data_frame)):
            for col in data_frame.columns:
                self.cell(col_widths[0], row_height, str(data_frame[col].iloc[i]), border=1)
            self.ln()

pdf = PDF()
pdf.add_page()
pdf.table(df)
pdf.output(output_path_pdf)

st.success("✅ PDF généré dans .cache/")

# 📄 Affichage du PDF dans Streamlit
with open(output_path_pdf, "rb") as f:
    base64_pdf = base64.b64encode(f.read()).decode("utf-8")

pdf_display = f"""
<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="500px" type="application/pdf" style="border: 1px solid #ccc; border-radius: 8px;"></iframe>
"""
st.markdown(pdf_display, unsafe_allow_html=True)
