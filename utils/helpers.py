import pandas as pd
import streamlit as st

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


import pandas as pd

import pandas as pd
import streamlit as st

def concat_all_dataframes_from_session_dict(dict_key):
    """
    Concatène tous les DataFrames d'un dictionnaire stocké dans st.session_state[dict_key].
    Vérifie que toutes les colonnes sont cohérentes.
    """
    if dict_key not in st.session_state:
        st.warning(f"Aucun dictionnaire trouvé dans st.session_state['{dict_key}']")
        return pd.DataFrame()

    df_dict = st.session_state[dict_key]
    valid_items = [(name, df) for name, df in df_dict.items() if isinstance(df, pd.DataFrame)]

    if not valid_items:
        st.warning("Aucun DataFrame valide à concaténer.")
        return pd.DataFrame()

    # Vérification des colonnes
    first_name, first_df = valid_items[0]
    reference_cols = list(first_df.columns)

    for name, df in valid_items[1:]:
        if list(df.columns) != reference_cols:
            raise ValueError(
                f"❌ Les colonnes du DataFrame '{name}' ne correspondent pas à celles de '{first_name}'.\n"
                f"Attendu : {reference_cols}\nTrouvé   : {list(df.columns)}"
            )

    # Concaténation
    all_dfs = [df for _, df in valid_items]
    return pd.concat(all_dfs, ignore_index=True)



def add_df_to_dict(df_name, df_object):
    """
    Ajoute un DataFrame à un dictionnaire si le nom n'existe pas déjà.

    - df_dict : dictionnaire existant {nom_df: DataFrame}
    - df_name : str, nom identifiant le DataFrame
    - df_object : le DataFrame à stocker
    """
    if df_name not in st.session_state.df_dict:
        if isinstance(df_name, str) and isinstance(df_object, pd.DataFrame):
            st.session_state.df_dict[df_name] = df_object
