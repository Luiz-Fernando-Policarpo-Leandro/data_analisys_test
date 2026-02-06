"""
Módulo de Enriquecimento e Agregação de Dados (Parte 2)

Este script consolida os dados de despesas já validados com as informações 
cadastrais das operadoras, gerando relatórios agregados e exportando o resultado final.
"""

from pathlib import Path
import zipfile

# Importação de módulos internos de utilitários
from utils.file_utils import carregar_despesas, carregar_operadoras
from utils.enrich_utils import enriquecer_dados
from utils.aggregate_utils import agregar_dados

# --- Configuração de Caminhos (Paths) ---
BASE_DIR = Path("data/despesas")
OPERADORAS_DIR = Path("data/operadoras")

# Arquivos de entrada e saída
INPUT_VALIDOS = BASE_DIR / "valido" / "consolidado_validos.csv"
OUTPUT_ENRIQUECIDO = OPERADORAS_DIR / "despesas_enriquecidas.csv"
OUTPUT_AGREGADO = OPERADORAS_DIR / "despesas_agregadas.csv"

# Nome do arquivo final para entrega do desafio
ZIP_OUTPUT = Path("Teste_Luiz_Fernando_Policarpo_leandro.zip")


def zip_dir(source_dir: Path, output_zip: Path):
    """
    Compacta um diretório inteiro em um arquivo .zip.

    Args:
        source_dir (Path): Pasta de origem que será compactada.
        output_zip (Path): Nome e caminho do arquivo .zip de saída.

    Raises:
        FileNotFoundError: Caso a pasta de origem não exista.
    """
    if not source_dir.exists():
        raise FileNotFoundError(f"Pasta não encontrada: {source_dir.resolve()}")

    print(f"[INFO] Compactando diretório {source_dir} para {output_zip}...")
    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in source_dir.rglob("*"):
            if file.is_file():
                # O arcname garante que o ZIP não contenha toda a estrutura de pastas do sistema
                zf.write(file, arcname=file.relative_to(source_dir))


def run():
    """
    Executa o pipeline principal da Parte 2:
    1. Carrega dados validados e cadastros.
    2. Cruza informações (Join/Merge).
    3. Gera métricas agregadas.
    4. Compacta os resultados.
    """
    
    # 1. Carga de Dados
    # 'carregar_despesas' lê o CSV gerado na Parte 1
    despesas = carregar_despesas(INPUT_VALIDOS)
    # 'carregar_operadoras' busca arquivos cadastrais (ex: ANS/Relatórios)
    operadoras = carregar_operadoras(OPERADORAS_DIR)

    # 2. Enriquecimento (Join)
    # Adiciona Razão Social ou outros dados cadastrais baseados no CNPJ/Registro ANS
    print("[INFO] Enriquecendo dados de despesas com informações das operadoras...")
    enriquecido = enriquecer_dados(despesas, operadoras)
    enriquecido.to_csv(OUTPUT_ENRIQUECIDO, index=False)

    # 3. Agregação e Transformação
    # Agrupa dados por competência, operadora ou categoria conforme requisitos
    print("[INFO] Gerando base agregada...")
    agregado = agregar_dados(enriquecido)
    agregado.to_csv(OUTPUT_AGREGADO, index=False)

    # 4. Finalização
    # Gera o artefato final solicitado para submissão
    zip_dir(OPERADORAS_DIR, ZIP_OUTPUT)

    print("-" * 30)
    print("[OK] Pipeline executado com sucesso.")
    print(f"[OK] ZIP gerado em: {ZIP_OUTPUT.resolve()}")
    print("-" * 30)


if __name__ == "__main__":
    run()