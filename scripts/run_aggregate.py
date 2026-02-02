from pathlib import Path
import zipfile

from utils.file_utils import carregar_despesas, carregar_operadoras
from utils.enrich_utils import enriquecer_dados
from utils.aggregate_utils import agregar_dados

BASE_DIR = Path("data/despesas")
OPERADORAS_DIR = Path("data/operadoras")

INPUT_VALIDOS = BASE_DIR / "valido" / "consolidado_validos.csv"
OUTPUT_ENRIQUECIDO = OPERADORAS_DIR / "despesas_enriquecidas.csv"
OUTPUT_AGREGADO = OPERADORAS_DIR / "despesas_agregadas.csv"

ZIP_OUTPUT = Path("operadoras.zip")


def zip_dir(source_dir: Path, output_zip: Path):
    if not source_dir.exists():
        raise FileNotFoundError(f"Pasta não encontrada: {source_dir.resolve()}")

    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in source_dir.rglob("*"):
            if file.is_file():
                zf.write(file, arcname=file.relative_to(source_dir))


def run():
    despesas = carregar_despesas(INPUT_VALIDOS)
    operadoras = carregar_operadoras(OPERADORAS_DIR)

    enriquecido = enriquecer_dados(despesas, operadoras)
    enriquecido.to_csv(OUTPUT_ENRIQUECIDO, index=False)

    agregado = agregar_dados(enriquecido)
    agregado.to_csv(OUTPUT_AGREGADO, index=False)

    zip_dir(OPERADORAS_DIR, ZIP_OUTPUT)

    print("[OK] Pipeline executado com sucesso.")
    print(f"[OK] ZIP gerado em: {ZIP_OUTPUT.resolve()}")


if __name__ == "__main__":
    run()
