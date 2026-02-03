import re
import zipfile
from pathlib import Path
import pandas as pd

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis"

ARQUIVO_REGEX = re.compile(
    r"(?:(?P<trimestre>[1-4])\s*[Tt]?[-_]*\s*(?P<ano>\d{4})|"
    r"(?P<ano2>\d{4})[-_]*\s*(?P<trimestre2>[1-4])\s*[Tt]?)",
    re.IGNORECASE
)

# =========================
# Helpers
# =========================
def _get_html(url: str) -> BeautifulSoup:
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")


# =========================
# Listagem de arquivos ANS
# =========================
def list_files_api(ultimos_trimestres_por_ano: int = 3, verbose: bool = True):
    """
    Retorna lista ordenada de tuplas:
    (ano, trimestre, filepath)
    """
    try:
        soup = _get_html(BASE_URL)

        years = sorted(
            [
                a.get("href").strip("/")
                for a in soup.find_all("a")
                if a.get("href") and a.get("href").strip("/").isdigit()
            ],
            key=int
        )

        files = []

        for year in years:
            year_url = f"{BASE_URL}/{year}"
            try:
                soup_year = _get_html(year_url)
            except Exception as e:
                if verbose:
                    print(f"[WARN] Falha ao acessar {year}: {e}")
                continue

            for a in soup_year.find_all("a"):
                href = a.get("href")
                if not href or not href.endswith(".zip"):
                    continue

                match = ARQUIVO_REGEX.search(href)
                if not match:
                    continue

                ano = match.group("ano") or match.group("ano2")
                trimestre = match.group("trimestre") or match.group("trimestre2")

                if ano and trimestre:
                    files.append(
                        {
                            "ano": int(ano),
                            "trimestre": int(trimestre),
                            "filepath": f"{year}/{href}",
                        }
                    )

        files.sort(key=lambda x: (x["ano"], x["trimestre"]))

        result = []
        for ano in sorted({f["ano"] for f in files}):
            ano_files = [f for f in files if f["ano"] == ano]
            result.extend(ano_files[-ultimos_trimestres_por_ano:])

        return [(f["ano"], f["trimestre"], f["filepath"]) for f in result]

    except Exception as e:
        if verbose:
            print(f"[ERRO] list_files_api: {e}")
        return []


# =========================
# Download
# =========================
def download_file(item, download_dir: Path):
    """
    item: (ano, trimestre, filepath)
    """
    ano, trimestre, filepath = item
    download_dir = Path(download_dir)
    download_dir.mkdir(parents=True, exist_ok=True)

    zip_path = download_dir / Path(filepath).name
    url = f"{BASE_URL}/{filepath}" if not filepath.startswith("http") else filepath

    try:
        resp = requests.get(url, stream=True, timeout=120)
        resp.raise_for_status()

        with open(zip_path, "wb") as f:
            for chunk in resp.iter_content(1024 * 1024):
                f.write(chunk)

        return zip_path, ano, trimestre

    except Exception as e:
        print(f"[DOWNLOAD FALHOU] {zip_path.name}: {e}")
        return None, ano, trimestre


def download_static_file(url: str, download_dir: str | Path) -> Path:
    download_dir = Path(download_dir)
    download_dir.mkdir(parents=True, exist_ok=True)

    output_path = download_dir / Path(url).name

    resp = requests.get(url, stream=True, timeout=60)
    resp.raise_for_status()

    with open(output_path, "wb") as f:
        for chunk in resp.iter_content(1024 * 1024):
            f.write(chunk)

    return output_path


# =========================
# ZIP
# =========================
def extract_zip(zip_path: Path, extract_to: Path) -> Path:
    extract_to.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(extract_to)

    return extract_to

def carregar_despesas(csv_path: Path) -> pd.DataFrame:
    if not csv_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {csv_path.resolve()}")

    df = pd.read_csv(csv_path, dtype=str)

    # normalizações mínimas esperadas pelo pipeline
    df["REG_ANS"] = df["REG_ANS"].astype(str).str.strip()
    df["ValorDespesas"] = df["ValorDespesas"].astype(float)

    return df


def carregar_operadoras(operadoras_dir: Path) -> pd.DataFrame:
    operadoras_dir = Path(operadoras_dir)
    operadoras_dir.mkdir(parents=True, exist_ok=True)

    csv_path = operadoras_dir / "Relatorio_cadop.csv"

    if not csv_path.exists():
        from utils.file_utils import download_static_file  # evita import circular
        csv_path = download_static_file(
            url="https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_ativas/Relatorio_cadop.csv",
            download_dir=operadoras_dir
        )

    df = pd.read_csv(
        csv_path,
        sep=";",
        encoding="latin1",
        dtype=str
    )

    df.columns = df.columns.str.strip().str.replace('"', '')

    df = df.rename(columns={
        "REGISTRO_OPERADORA": "REG_ANS",
        "Razao_Social": "RazaoSocial"
    })

    # garante colunas mínimas
    for col in ["CNPJ", "REG_ANS", "RazaoSocial", "Modalidade", "UF"]:
        if col not in df.columns:
            df[col] = pd.NA
        df[col] = df[col].astype(str).str.strip()

    return df

def zip_dir(source_dir: Path, output_zip: Path):
    if not source_dir.exists():
        raise FileNotFoundError(f"Pasta não encontrada: {source_dir.resolve()}")

    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in source_dir.rglob("*"):
            if file.is_file():
                zf.write(
                    file,
                    arcname=file.relative_to(source_dir)
                )

def rename_csv_columns(file_path: str, rename_map: dict, output_path: str = None):
    """
    Renomeia colunas de um CSV de acordo com o dicionário rename_map.

    Args:
        file_path (str): caminho do CSV original
        rename_map (dict): mapeamento {coluna_csv: coluna_desejada}
        output_path (str, optional): caminho do CSV renomeado. 
                                     Se None, sobrescreve o arquivo original.

    Returns:
        str: caminho do CSV renomeado
    """
    file_path = Path(file_path)
    if output_path is None:
        output_path = file_path

    # Detecta delimitador automaticamente (; ou ,)
    with open(file_path, 'r', encoding='utf-8') as f:
        first_line = f.readline()
        delimiter = ';' if ';' in first_line else ','

    # Lê o CSV
    df = pd.read_csv(file_path, delimiter=delimiter, dtype=str)

    # Renomeia as colunas
    df.rename(columns=rename_map, inplace=True)

    # Salva o CSV
    df.to_csv(output_path, sep=delimiter, index=False, encoding='utf-8')

    return str(output_path)