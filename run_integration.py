from pathlib import Path
import zipfile
import tempfile
import pandas as pd
import os
import shutil
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed

from utils.file_utils import list_files_api, download_file, extract_zip
from utils.dataframe_utils import load_table, normalize_and_parse, separar_consolidados

FILES_PATH = Path("data/despesas")
INVAL_PATH = FILES_PATH / "invalidos"
VAL_PATH = FILES_PATH / "valido"

OUT_ALL = FILES_PATH / "consolidado_despesas.csv"
OUT_VALIDOS = VAL_PATH / "consolidado_validos.csv"
OUT_NEGATIVOS = INVAL_PATH / "consolidado_numero_negativo_invalido.csv"
OUT_ZERO = INVAL_PATH / "consolidado_valor_zero_invalido.csv"
OUT_CNPJ_INVALIDO = INVAL_PATH / "consolidado_cnpj_invalido.csv"
OUT_ZIP = FILES_PATH / "consolidado_despesas.zip"

def process_zip(zip_path_ano_trimestre):
    zip_path, ano, trimestre = zip_path_ano_trimestre
    tmp_extract = zip_path.parent / f"extract_{zip_path.stem}"
    tmp_extract.mkdir(exist_ok=True)
    try:
        extract_zip(zip_path, tmp_extract)
        dfs = []
        for f in tmp_extract.rglob("*"):
            df = load_table(f)
            if not df.empty:
                df_norm = normalize_and_parse(df, f.name)
                if not df_norm.empty:
                    dfs.append(df_norm)
        return pd.concat(dfs, ignore_index=True) if dfs else None
    finally:
        shutil.rmtree(tmp_extract)
        zip_path.unlink(missing_ok=True)

def run():
    # cria pastas
    for p in [FILES_PATH, INVAL_PATH, VAL_PATH]:
        p.mkdir(parents=True, exist_ok=True)

    # ---------------- verifica consolidado existente ----------------
    if OUT_ALL.exists():
        print(f"[INFO] Usando consolidado existente: {OUT_ALL}")
        df_full = pd.read_csv(OUT_ALL, encoding="utf-8")
    elif OUT_ZIP.exists():
        print(f"[INFO] ZIP do consolidado encontrado, extraindo: {OUT_ZIP}")
        with zipfile.ZipFile(OUT_ZIP, "r") as zf:
            zf.extractall(FILES_PATH)
        df_full = pd.read_csv(OUT_ALL, encoding="utf-8")
    else:
        # ---------------- download + processamento ----------------
        with tempfile.TemporaryDirectory(prefix="ans_") as tmp_dir:
            downloads = Path(tmp_dir) / "downloads"
            downloads.mkdir(exist_ok=True)

            # lista arquivos do site
            files_list = (list_files_api(verbose=True))[-3:]
            print(files_list)
            if not files_list:
                print("[ERRO] Nenhum arquivo encontrado na API.")
                return

            # download paralelo
            download_results = []
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = {executor.submit(download_file, item, downloads): item for item in files_list}
                for future in as_completed(futures):
                    zip_path, ano, trimestre = future.result()
                    if zip_path:
                        download_results.append((zip_path, ano, trimestre))

            # processa zips em paralelo
            all_dfs = []
            with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
                futures = [executor.submit(process_zip, item) for item in download_results]
                for future in as_completed(futures):
                    df = future.result()
                    if df is not None and not df.empty:
                        all_dfs.append(df)

            if all_dfs:
                df_full = pd.concat(all_dfs, ignore_index=True)
                df_full.to_csv(OUT_ALL, index=False, encoding="utf-8")
            else:
                print("[ERRO] Nenhum DataFrame processado.")
                return

    # ---------------- separa válidos e inválidos ----------------
    df_validos, df_negativos, df_zero, df_cnpj_invalido = separar_consolidados(df_full)


    df_validos.to_csv(OUT_VALIDOS, index=False, encoding="utf-8")
    df_negativos.to_csv(OUT_NEGATIVOS, index=False, encoding="utf-8")
    df_zero.to_csv(OUT_ZERO, index=False, encoding="utf-8")
    df_cnpj_invalido.to_csv(OUT_CNPJ_INVALIDO, index=False, encoding="utf-8")

    # ---------------- zip final ----------------
    with zipfile.ZipFile(OUT_ZIP, "w") as zf:
        zf.write(OUT_ALL, OUT_ALL.name)

    print("Consolidação completa! CSVs gerados.")


if __name__ == "__main__":
    run()

