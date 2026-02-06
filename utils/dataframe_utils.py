import pandas as pd
from pathlib import Path
from .cnpj_utils import valida_cnpj
from .file_utils import ARQUIVO_REGEX

# Expressão regular para identificar linhas de despesas com eventos ou sinistros
REGEX_SINISTROS = r"Despesas.*(?:Eventos|Sinistros)"

def load_table(path: Path) -> pd.DataFrame:
    """ Carrega arquivos de diferentes formatos (CSV, TXT, Excel) com tratamento de erros e encoding. """
    try:
        if path.suffix.lower() in [".csv", ".txt"]:
            try: 
                # Tenta leitura automática (sniffing de separador) com UTF-8
                return pd.read_csv(path, sep=None, engine="python", encoding="utf-8", on_bad_lines='skip')
            except: 
                # Fallback para ponto-e-vírgula e codificação Latin-1 (comum em arquivos da ANS)
                return pd.read_csv(path, sep=";", engine="python", encoding="latin1", on_bad_lines='skip')
        elif path.suffix.lower() in [".xls", ".xlsx"]:
            return pd.read_excel(path)
    except Exception as e:
        print(f"Erro ao abrir {path}: {e}")
    return pd.DataFrame()

def normalize_and_parse(df, fname=None):
    """ Filtra as LINHAS internamente e padroniza as colunas. """
    df = df.copy()
    
    # 1. Filtro de Linhas (Se não fizer isso aqui, o CSV final terá lixo)
    desc_col = "DESCRICAO" if "DESCRICAO" in df.columns else next((c for c in df.columns if "descr" in c.lower()), None)
    
    if desc_col:
        mask = df[desc_col].astype(str).str.contains(REGEX_SINISTROS, case=False, na=False, regex=True)
        df = df[mask].copy()
    
    if df.empty:
        return pd.DataFrame()

    # 2. Mapeamento de colunas (Resto do seu código original...)
    reg_col = next((c for c in df.columns if "reg" in c.lower()), None)
    cnpj_col = next((c for c in df.columns if "cnpj" in c.lower()), None)
    valor_col = next((c for c in df.columns if "vl_" in c.lower() or "valor" in c.lower()), None)
    data_col = next((c for c in df.columns if "data" in c.lower()), None)
    razao_col = next((c for c in df.columns if "razao" in c.lower()), None)
    
    if not reg_col or not valor_col: return pd.DataFrame()

    # --- PASSO 3: LIMPEZA ---
    df["REG_ANS"] = df[reg_col].astype(str).str.strip()
    df["CNPJ"] = df[cnpj_col].astype(str).str.replace(r"\D", "", regex=True) if cnpj_col else ""
    df["RazaoSocial"] = df[razao_col].astype(str).str.strip() if razao_col else ""
    
    df["ValorDespesas"] = pd.to_numeric(
        df[valor_col].astype(str).str.replace(r"\.", "", regex=True).str.replace(",", ".", regex=False),
        errors='coerce'
    )

    # --- PASSO 4: ANO E TRIMESTRE ---
    # Se não encontrar no CSV, tentamos no nome do arquivo
    df["_ano"] = pd.NA
    df["_trimestre"] = pd.NA

    if data_col:
        try:
            dates = pd.to_datetime(df[data_col], errors='coerce')
            df["_ano"] = dates.dt.year
            df["_trimestre"] = dates.dt.quarter
        except:
            pass

    if fname:
        match = ARQUIVO_REGEX.search(fname)
        if match:
            # fillna garante que se a data_col falhou, o nome do arquivo salva
            try:
                ano_fname = int(match.group("ano") or match.group("ano2"))
                tri_fname = int(match.group("trimestre") or match.group("trimestre2"))
                df["_ano"] = df["_ano"].fillna(ano_fname)
                df["_trimestre"] = df["_trimestre"].fillna(tri_fname)
            except:
                pass

    df["Ano"] = df["_ano"].astype("Int64")
    df["Trimestre"] = df["_trimestre"].astype("Int64")
    
    return df[["REG_ANS", "CNPJ", "RazaoSocial", "Trimestre", "Ano", "ValorDespesas"]]

def separar_consolidados(df_full: pd.DataFrame, validar_cnpj: bool = True ):
    """ Divide o dataframe consolidado em quatro categorias para relatórios de qualidade de dados. """
    df = df_full.copy()

    # Aplica função de validação de CNPJ (Módulo externo)
    if validar_cnpj:
        df["CNPJ_valido"] = df["CNPJ"].apply(valida_cnpj)
    else:
        df["CNPJ_valido"] = True

    # Marca valores negativos ou zerados como inválidos
    df["valor_invalido"] = df["ValorDespesas"] <= 0

    # Grupo 1: Dados prontos para uso (Valor > 0 e CNPJ válido)
    df_validos = df[
        (df["ValorDespesas"] > 0) & (df["CNPJ_valido"])
    ].copy()

    # Grupos de Auditoria: Negativos, Zeros e CNPJs mal formatados
    df_negativos = df[df["ValorDespesas"] < 0].copy()
    df_zero = df[df["ValorDespesas"] == 0].copy()
    df_cnpj_invalido = df[~df["CNPJ_valido"]].copy()

    # Limpa colunas auxiliares antes de retornar
    col_aux = ["CNPJ_valido", "valor_invalido"]
    for d in (df_validos, df_negativos, df_zero, df_cnpj_invalido):
        d.drop(columns=[c for c in col_aux if c in d.columns], inplace=True)

    return df_validos, df_negativos, df_zero, df_cnpj_invalido

def is_eventos_sinistros_df(df: pd.DataFrame) -> bool:
    """ Retorna True APENAS se encontrar a palavra chave na coluna correta. """
    if df is None or df.empty:
        return False

    # Identifica a coluna
    desc_col = "DESCRICAO" if "DESCRICAO" in df.columns else next((c for c in df.columns if "descr" in c.lower()), None)

    if not desc_col:
        return False

    # Verifica o conteúdo (case=False para garantir que pegue DESPESAS ou despesas)
    possui_sinistro = df[desc_col].astype(str).str.contains(REGEX_SINISTROS, case=False, na=False, regex=True).any()
    return possui_sinistro
    if df is None or df.empty:
        return False

    desc_col = "DESCRICAO" if "DESCRICAO" in df.columns else next((c for c in df.columns if "descr" in c.lower()), None)

    if not desc_col:
        return False

    # Mudamos aqui também para evitar o Warning
    return df[desc_col].astype(str).str.contains(REGEX_SINISTROS, case=False, na=False, regex=True).any()
    """ Verifica se o dataframe contém as palavras-chave de sinistros na coluna de descrição. """
    if df is None or df.empty:
        return False

    # Procura especificamente pela coluna 'DESCRICAO' ou variações
    desc_col = "DESCRICAO" if "DESCRICAO" in df.columns else None
    
    if not desc_col:
        # Tenta localizar qualquer coluna que contenha "descr" no nome
        desc_col = next((c for c in df.columns if "descr" in c.lower()), None)

    if not desc_col:
        return False

    # Retorna True se pelo menos uma linha satisfizer a Regex de sinistros
    return df[desc_col].astype(str).str.contains(REGEX_SINISTROS, case=False, na=False, regex=True).any()