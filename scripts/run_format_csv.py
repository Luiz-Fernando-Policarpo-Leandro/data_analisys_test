import sys
from utils.file_utils import rename_csv_columns
from pathlib import Path


ENRICH_CSV = Path("data/operadoras/despesas_enriquecidas.csv")
RELATORIO_CSV = Path("data/operadoras/Relatorio_cadop.csv")

def run():
    rename_map_despesas = {
        "REG_ANS": "registro_ans",
        "RazaoSocial": "razao_social",
        "ValorDespesas": "valor"
    }

    rename_map_operadoras = {
        "REGISTRO_OPERADORA": "registro_ans",
        "Razao_Social": "razao_social",
        "Nome_Fantasia": "nome_fantasia"
    }

    # Renomeia operadoras
    rename_csv_columns(
        RELATORIO_CSV,
        rename_map_operadoras
    )

    # Renomeia despesas
    rename_csv_columns(
        ENRICH_CSV,
        rename_map_despesas
    )

if __name__ == "__main__":
    run()
