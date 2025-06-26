print("🔍 Chargement du module helpers")

try:
    import pandas as pd
    import os
except Exception as e:
    print("💥 Erreur d'import :", e)

def concat_dataframes(*dfs):
    """
    Concatène plusieurs DataFrames verticalement (par lignes),
    après avoir vérifié que toutes les colonnes sont identiques (mêmes noms et même ordre).

    Args:
        *dfs: Un nombre variable de pd.DataFrame à concaténer.

    Returns:
        pd.DataFrame: Le DataFrame concaténé.

    Raises:
        ValueError: Si les colonnes ne correspondent pas exactement.
    """
    if not dfs:
        raise ValueError("Aucun DataFrame fourni.")

    first_cols = list(dfs[0].columns)

    for i, df in enumerate(dfs[1:], start=2):
        if list(df.columns) != first_cols:
            raise ValueError(f"❌ Les colonnes du DataFrame n°{i} ne correspondent pas à celles du premier.\n"
                             f"Attendu : {first_cols}\nTrouvé   : {list(df.columns)}")

    return pd.concat(dfs, axis=0, ignore_index=True)

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