from pathlib import Path
import tempfile
import pandas as pd
import os
import shutil
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed

from utils.file_utils import (
    list_files_api,
    download_file,
    extract_zip,
    zip_dir
)
from utils.dataframe_utils import load_table, normalize_and_parse, separar_consolidados

# --- Configuração de Caminhos (Requisito 1.3 - Organização de Saída) ---
FILES_PATH = Path("data/despesas")
INVAL_PATH = FILES_PATH / "invalidos"
VAL_PATH = FILES_PATH / "valido"

OUT_ALL = FILES_PATH / "consolidado_despesas.csv"
OUT_VALIDOS = VAL_PATH / "consolidado_validos.csv"
OUT_NEGATIVOS = INVAL_PATH / "consolidado_numero_negativo_invalido.csv"
OUT_ZERO = INVAL_PATH / "consolidado_valor_zero_invalido.csv"
OUT_CNPJ_INVALIDO = INVAL_PATH / "consolidado_cnpj_invalido.csv"

# ZIP final no root conforme solicitado no requisito 1.3
OUT_ZIP = Path.cwd() / "consolidado_despesas.zip"

def process_zip(zip_path_ano_trimestre):
    """
    Processa cada ZIP individualmente. 
    Justificativa Técnica: Uso de ProcessPoolExecutor aqui para contornar o GIL do Python
    visto que a extração e o parse de grandes CSVs são tarefas CPU-bound.
    """
    zip_path, _, _ = zip_path_ano_trimestre
    tmp_extract = zip_path.parent / f"extract_{zip_path.stem}"
    tmp_extract.mkdir(exist_ok=True)

    try:
        extract_zip(zip_path, tmp_extract)
        dfs = []

        # Requisito 1.2: Resiliência a variações de diretório e identificação de arquivos
        for f in tmp_extract.rglob("*"):
            # Filtro de extensões para evitar processar metadados ou arquivos corrompidos
            if f.suffix.lower() in ['.csv', '.xlsx', '.txt']:
                
                # Requisito 1.2: Identificação automática de arquivos de 'Despesas'
                if "despesa" in f.name.lower() or "sinistro" in f.name.lower():
                    print(f"[INFO] Processando arquivo de despesas: {f.name}")
                    
                    df = load_table(f)
                    if not df.empty:
                        # Normalização de colunas variadas e tipos de dados
                        df_norm = normalize_and_parse(df, f.name)
                        if not df_norm.empty:
                            dfs.append(df_norm)

        # Agregação local antes de retornar para o processo principal
        return pd.concat(dfs, ignore_index=True) if dfs else None

    finally:
        # Limpeza de arquivos temporários (Boas práticas de I/O)
        shutil.rmtree(tmp_extract, ignore_errors=True)
        zip_path.unlink(missing_ok=True)


def run():
    # ---------------- Inicialização de Ambiente ----------------
    for p in [FILES_PATH, INVAL_PATH, VAL_PATH]:
        p.mkdir(parents=True, exist_ok=True)

    # ---------------- Verificação de Cache ----------------
    if OUT_ALL.exists():
        print(f"[INFO] Usando consolidado existente: {OUT_ALL}")
        df_full = pd.read_csv(OUT_ALL, encoding="utf-8")
    else:
        # Requisito 1.2 Trade-off: Processamento em memória vs Incremental
        # Decisão: Processamento em memória para os últimos 3 trimestres visando performance,
        # visto que o volume de dados consolidado (~500MB-2GB) é suportado pela RAM moderna.
        with tempfile.TemporaryDirectory(prefix="ans_") as tmp_dir:
            downloads = Path(tmp_dir) / "downloads"
            downloads.mkdir(exist_ok=True)

            # Requisito 1.1: Identificação dos últimos 3 trimestres na API
            files_list = list_files_api(verbose=True)[-3:]

            if not files_list:
                print("[ERRO] Nenhum arquivo encontrado na API.")
                return

            # ---------------- Download Paralelo (I/O Bound) ----------------
            # Justificativa: ThreadPoolExecutor é ideal para downloads simultâneos
            download_results = []
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = {
                    executor.submit(download_file, item, downloads): item
                    for item in files_list
                }
                for future in as_completed(futures):
                    zip_path, ano, trimestre = future.result()
                    if zip_path:
                        download_results.append((zip_path, ano, trimestre))

            # ---------------- Processamento Paralelo (CPU Bound) ----------------
            all_dfs = []
            with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
                futures = [
                    executor.submit(process_zip, item)
                    for item in download_results
                ]
                for future in as_completed(futures):
                    df = future.result()
                    if df is not None and not df.empty:
                        all_dfs.append(df)

            if not all_dfs:
                print("[ERRO] Nenhum DataFrame processado.")
                return

            # Consolidação Final (Requisito 1.3)
            df_full = pd.concat(all_dfs, ignore_index=True)
            df_full.to_csv(OUT_ALL, index=False, encoding="utf-8")

    # ---------------- Requisito 1.3: Análise Crítica e Inconsistências ----------------
    # Separação lógica de dados para garantir integridade analítica
    df_validos, df_negativos, df_zero, df_cnpj_invalido = separar_consolidados(
        df_full,
        validar_cnpj=False # Tratamento de CNPJ customizado na utils
    )

    # Salvando subconjuntos para auditoria (Justificativa de tratamento de erro)
    df_validos.to_csv(OUT_VALIDOS, index=False, encoding="utf-8")
    df_negativos.to_csv(OUT_NEGATIVOS, index=False, encoding="utf-8")
    df_zero.to_csv(OUT_ZERO, index=False, encoding="utf-8")
    df_cnpj_invalido.to_csv(OUT_CNPJ_INVALIDO, index=False, encoding="utf-8")

    # ---------------- Entrega Final (Requisito 1.3) ----------------
    print(f"[INFO] Gerando ZIP final em: {OUT_ZIP}")
    zip_dir(FILES_PATH, OUT_ZIP)


if __name__ == "__main__":
    run()