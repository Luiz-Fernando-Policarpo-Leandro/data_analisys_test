import pandas as pd
from pathlib import Path
from .cnpj_utils import valida_cnpj
from .file_utils import ARQUIVO_REGEX

def load_table(path: Path) -> pd.DataFrame:
    try:
        if path.suffix.lower() in [".csv", ".txt"]:
            try: return pd.read_csv(path, sep=None, engine="python", encoding="utf-8", on_bad_lines='skip')
            except: return pd.read_csv(path, sep=";", engine="python", encoding="latin1", on_bad_lines='skip')
        elif path.suffix.lower() in [".xls", ".xlsx"]:
            return pd.read_excel(path)
    except Exception as e:
        print(f"Erro ao abrir {path}: {e}")
    return pd.DataFrame()

def normalize_and_parse(df, fname=None):
    df = df.copy()
    reg_col = next((c for c in df.columns if "reg" in c.lower()), None)
    cnpj_col = next((c for c in df.columns if "cnpj" in c.lower()), None)
    valor_col = next((c for c in df.columns if "vl_" in c.lower() or "valor" in c.lower()), None)
    data_col = next((c for c in df.columns if "data" in c.lower()), None)
    razao_col = next((c for c in df.columns if "razao" in c.lower()), None)
    if not reg_col or not valor_col: return pd.DataFrame()

    df["REG_ANS"] = df[reg_col].astype(str).str.strip()
    df["CNPJ"] = df[cnpj_col].astype(str).str.replace(r"\D", "", regex=True) if cnpj_col else ""
    df["RazaoSocial"] = df[razao_col].astype(str).str.strip() if razao_col else ""
    df["ValorDespesas"] = pd.to_numeric(
        df[valor_col].astype(str).str.replace(r"\.", "", regex=True).str.replace(",", ".", regex=False),
        errors='coerce'
    )

    if data_col:
        df["_ano"] = pd.to_datetime(df[data_col], errors='coerce').dt.year
        df["_trimestre"] = pd.to_datetime(df[data_col], errors='coerce').dt.quarter
    else:
        df["_ano"] = df["_trimestre"] = pd.NA

    if fname:
        match = ARQUIVO_REGEX.search(fname)
        if match:
            ano = int(match.group("ano") or match.group("ano2"))
            trimestre = int(match.group("trimestre") or match.group("trimestre2"))
            df["_ano"] = df["_ano"].fillna(ano)
            df["_trimestre"] = df["_trimestre"].fillna(trimestre)

    df["Ano"] = df["_ano"].astype("Int64")
    df["Trimestre"] = df["_trimestre"].astype("Int64")
    return df[["REG_ANS", "CNPJ", "RazaoSocial", "Trimestre", "Ano", "ValorDespesas"]]

def separar_consolidados(df_full: pd.DataFrame):
    df_full["CNPJ_valido"] = df_full["CNPJ"].apply(valida_cnpj)
    df_full["valor_invalido"] = df_full["ValorDespesas"] <= 0

    df_validos = df_full[(df_full["ValorDespesas"] > 0) & df_full["CNPJ_valido"]].copy()
    df_negativos = df_full[df_full["ValorDespesas"] < 0].copy()
    df_zero = df_full[df_full["ValorDespesas"] == 0].copy()
    df_cnpj_invalido = df_full[~df_full["CNPJ_valido"]].copy()

    for df in [df_validos, df_negativos, df_zero, df_cnpj_invalido]:
        df.drop(columns=[c for c in ["CNPJ_valido","valor_invalido"] if c in df.columns], inplace=True)

    return df_validos, df_negativos,df_zero, df_cnpj_invalido 
