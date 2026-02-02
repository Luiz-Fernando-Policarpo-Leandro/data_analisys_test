import pandas as pd
from utils.cnpj_utils import valida_cnpj, normalizar_cnpj

def enriquecer_dados(despesas: pd.DataFrame, operadoras: pd.DataFrame) -> pd.DataFrame:
    operadoras_sel = (
        operadoras[
            ["REG_ANS", "CNPJ", "RazaoSocial", "Modalidade", "UF"]
        ]
        .drop_duplicates("REG_ANS")
    )

    df = despesas.merge(
        operadoras_sel,
        on="REG_ANS",
        how="left",
        validate="m:1",
        suffixes=("", "_cad")
    )

    # Preferir cadastro ANS
    df["CNPJ"] = df["CNPJ"].fillna(df["CNPJ_cad"])
    df["RazaoSocial"] = df["RazaoSocial"].fillna(df["RazaoSocial_cad"])

    # Normalização + validação
    df["CNPJ"] = df["CNPJ"].apply(normalizar_cnpj)
    df = df[df["CNPJ"].apply(valida_cnpj)]

    return df[
        ["REG_ANS", "CNPJ", "RazaoSocial", "Modalidade", "UF",
         "Trimestre", "Ano", "ValorDespesas"]
    ]
