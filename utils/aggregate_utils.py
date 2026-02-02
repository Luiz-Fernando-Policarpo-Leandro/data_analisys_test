import pandas as pd

def agregar_dados(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(
            ["REG_ANS", "CNPJ", "RazaoSocial", "Modalidade", "UF", "Ano"],
            dropna=False
        )
        .agg(
            total_despesas=("ValorDespesas", "sum"),
            media_trimestral=("ValorDespesas", "mean"),
            desvio_padrao=("ValorDespesas", "std")
        )
        .reset_index()
        .rename(columns={"REG_ANS": "RegistroANS"})
        .sort_values("total_despesas", ascending=False)
    )
