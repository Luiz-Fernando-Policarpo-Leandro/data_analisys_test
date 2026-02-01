import requests
from pathlib import Path
import zipfile
from bs4 import BeautifulSoup
import re

ARQUIVO_REGEX = re.compile(
    r"(?:(?P<trimestre>[1-4])\s*[Tt]?[-_]*\s*(?P<ano>\d{4})|(?P<ano2>\d{4})[-_]*\s*(?P<trimestre2>[1-4])\s*[Tt]?)",
    re.IGNORECASE
)

BASE_URL = "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis"

def list_files_api(verbose=True):
    try:
        resp = requests.get(BASE_URL)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        years = sorted([a.get("href").strip("/") for a in soup.find_all("a") 
                        if a.get("href") and a.get("href").strip("/").isdigit()], key=int)
        files = []
        for year in years:
            resp_year = requests.get(f"{BASE_URL}/{year}")
            if resp_year.status_code != 200:
                if verbose: print(f"Falha {year} (status {resp_year.status_code})")
                continue
            soup_year = BeautifulSoup(resp_year.text, "html.parser")
            for a in soup_year.find_all("a"):
                href = a.get("href")
                if href and href.endswith(".zip"):
                    match = ARQUIVO_REGEX.search(href)
                    if match:
                        ano = match.group("ano") or match.group("ano2")
                        trimestre = match.group("trimestre") or match.group("trimestre2")
                        if ano and trimestre:
                            files.append({"ano": int(ano), "trimestre": int(trimestre), "filepath": f"{year}/{href}"})
    except Exception as e:
        print(f"Erro ao acessar {BASE_URL}: {e}")
        return []

    files.sort(key=lambda x: (x["ano"], x["trimestre"]))
    result = []
    for ano in sorted({f["ano"] for f in files}):
        ano_files = [f for f in files if f["ano"] == ano]
        result.extend(ano_files[-3:])
    return [(f["ano"], f["trimestre"], f["filepath"]) for f in result]


def download_file(item, download_dir):
    from pathlib import Path
    import requests
    ano, trimestre, filepath = item
    zip_path = Path(download_dir) / Path(filepath).name
    try:
        url = f"{BASE_URL}/{filepath}" if not filepath.startswith("http") else filepath
        resp = requests.get(url, stream=True)
        resp.raise_for_status()
        with open(zip_path, "wb") as f:
            for chunk in resp.iter_content(1024*1024):
                f.write(chunk)
        return zip_path, ano, trimestre
    except Exception as e:
        print(f"[DOWNLOAD FALHOU] {zip_path.name}: {e}")
        return None, ano, trimestre

def extract_zip(zip_path: Path, extract_to: Path):
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(extract_to)
    return extract_to
