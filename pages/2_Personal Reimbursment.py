import streamlit as st
import pandas as pd
import os
from utils.data_loader import load_data, filter_by_date
from utils.ui_helpers import display_user_amount_boxes, clear_cache_on_page_change

####### CLEAR CACHE ########
# Identifier cette page par un nom unique
CURRENT_PAGE = "2_Personal Reimbursment.py"  # ex: "Importer", "Analyse", "Résultats"
clear_cache_on_page_change(CURRENT_PAGE)
########################################################################################################

FOYER = 'Foyer'
### affichage

########################## WORKING SESSION #######################

processed_path = "./data/processed"
name_df = "expenses_data.csv"
total_path = os.path.join(processed_path, name_df)

df = pd.read_csv(total_path)

### Title and description

st.title("💸 Personal Reimbursement to the Common Pot")

if df["reimbursed"].notnull().all():
    st.success("✅ Tout est remboursé")
    default_checked = []
    rows_to_reimbursed = df
else: 
    st.warning("Quelqu'un est endetté....")
    files_not_reimbursed = df.copy()
    files_not_reimbursed = files_not_reimbursed[files_not_reimbursed["reimbursed"].isnull()]
    ID_rows_not_reimbursed = files_not_reimbursed["transaction_ID"].unique()
    rows_to_reimbursed =  files_not_reimbursed[(files_not_reimbursed["user"] != FOYER)].copy()
    st.dataframe(rows_to_reimbursed)
    date_min = rows_to_reimbursed["date"].min()
    date_max = rows_to_reimbursed["date"].max()
    source_reimb_manquant = sorted(rows_to_reimbursed["date_source_file"].unique())
    st.write(f"📅 Dates : de {date_min} à {date_max}, c'est à dire dans ces fichiers {source_reimb_manquant}")
    default_checked = source_reimb_manquant

    selected_values = []
    unique_values = sorted(df["date_source_file"].unique())

    with st.container():
        cols = st.columns(len(unique_values))
        for i, val in enumerate(unique_values):
            is_checked = val in default_checked  # ✅ test si on doit précocher
            if cols[i].checkbox(val, value=is_checked):
                selected_values.append(val)

    if selected_values:
        filtered_df = df[df["date_source_file"].isin(selected_values)]
        #st.dataframe(filtered_df)
    else:
        st.info("✅ Coche une ou plusieurs options pour filtrer le tableau.")

    # --- Sum of personal expenses ---
    personal_totals = rows_to_reimbursed.groupby("user")["amount"].sum().sort_values(ascending=False)
### affichage
    st.markdown("## 💰 Amount spent per person individually")
    df_summary_display = personal_totals.reset_index()

    cols = st.columns(len(df_summary_display))
    display_user_amount_boxes (df_summary_display, "user", "amount")

    latest_date = rows_to_reimbursed["date"].max()
    totals = rows_to_reimbursed.loc[rows_to_reimbursed["date"] == latest_date, "balance"].iloc[0]

### affichage
    st.markdown(f"""
    <br>
    </div>
    <div style="width: 100%; justify-content: center;">
        <div style="border: 1px solid #ccc; border-radius: 10px; padding: 1em; background-color: #323e54; text-align: left;">
            <h4 style="margin: 0; font-size: 1.2em;">👤💸 Total individual expenses: {personal_totals.sum():.2f}£</h4>
        </div>
    </div>
    <br>
    """, unsafe_allow_html=True)
    st.markdown(f"""
</div>
<div style="width: 100%; justify-content: center;">
    <div style="border: 1px solid #ccc; border-radius: 10px; padding: 1em; background-color: #323e54; text-align: left;">
        <h4 style="margin: 0; font-size: 1.2em;">💸 Due balance de la periode: {totals}£</h4>
    </div>
</div>
""", unsafe_allow_html=True)
### affichage

    st.markdown("## 💰 Amount each person must repay to the common pot")

    tot_to_reimburse = totals - personal_totals.sum()
    nb_users = rows_to_reimbursed["user"].nunique()

    df_to_reimburse = tot_to_reimburse/nb_users + personal_totals

    df_display = df_to_reimburse.reset_index()
    display_user_amount_boxes(df_display, "user", "amount")


### affichage
    if st.button("✅ Remboursé", key="reimbursed"):
            df_final = df.copy()
            df_final.loc[df_final["transaction_ID"].isin(ID_rows_not_reimbursed), "reimbursed"] = True
            st.success("✅ Tout est remboursé !.")
            df_final.to_csv(total_path, index=False)
            st.dataframe(df_final)





