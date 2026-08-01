print("🔍 Chargement du module helpers")

try:
    import pandas as pd
    import os
except Exception as e:
    print("💥 Erreur d'import :", e)

def concat_dataframes(*dfs):
    if not dfs:
        raise ValueError("Aucun DataFrame fourni.")

    first_cols = list(dfs[0].columns)

    for i, df in enumerate(dfs[1:], start=2):
        current_cols = list(df.columns)

        if current_cols != first_cols:
            missing = [c for c in first_cols if c not in current_cols]
            extra = [c for c in current_cols if c not in first_cols]

            raise ValueError(
                f"❌ DataFrame #{i} has different columns.\n\n"
                f"Expected ({len(first_cols)}):\n{first_cols}\n\n"
                f"Found ({len(current_cols)}):\n{current_cols}\n\n"
                f"Missing columns:\n{missing}\n\n"
                f"Extra columns:\n{extra}"
            )

    return pd.concat(dfs, ignore_index=True)

def check_if_existing_processed_file(processed_path, name_df):
    path_df = os.path.join(processed_path, name_df)
    if os.path.exists(path_df):
        df = pd.read_csv(path_df)
        return df
    else:
        return None

# def save_csv_move_pdf(IMPORTED_FOLDER, NEW_PDF, PROCESSED_PDF,file, df):
#     output_path = os.path.join(IMPORTED_FOLDER, file.replace(".pdf", ".csv"))
#     df.to_csv(output_path, index=False)
#     st.success(f"Fichier sauvegardé dans {output_path}")
#     # source = os.path.join(NEW_PDF, file)
#     # destination = os.path.join("./nouveau/dossier", file)
#     # shutil.move(source, destination)