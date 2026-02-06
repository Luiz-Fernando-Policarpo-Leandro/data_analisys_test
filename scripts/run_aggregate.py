from pathlib import Path
import zipfile

# Importação de funções utilitárias personalizadas para manipulação de arquivos e dados
from utils.file_utils import carregar_despesas, carregar_operadoras
from utils.enrich_utils import enriquecer_dados
from utils.aggregate_utils import agregar_dados

# Definição dos caminhos base para os diretórios de dados
BASE_DIR = Path("data/despesas")
OPERADORAS_DIR = Path("data/operadoras")

# Definição dos caminhos de entrada e saída dos arquivos CSV
INPUT_VALIDOS = BASE_DIR / "valido" / "consolidado_validos.csv"
OUTPUT_ENRIQUECIDO = OPERADORAS_DIR / "despesas_enriquecidas.csv"
OUTPUT_AGREGADO = OPERADORAS_DIR / "despesas_agregadas.csv"

# Nome do arquivo ZIP final que será gerado na raiz do projeto
ZIP_OUTPUT = Path("Teste_Luiz_Fernando_Policarpo_leandro.zip")


def zip_dir(source_dir: Path, output_zip: Path):
    """
    Compacta todos os arquivos de um diretório em um arquivo ZIP.
    """
    if not source_dir.exists():
        raise FileNotFoundError(f"Pasta não encontrada: {source_dir.resolve()}")

    # Cria o arquivo ZIP usando o método de compressão DEFLATED
    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        # Percorre recursivamente todos os arquivos dentro do diretório de origem
        for file in source_dir.rglob("*"):
            if file.is_file():
                # Escreve o arquivo no ZIP mantendo a estrutura relativa de pastas
                zf.write(file, arcname=file.relative_to(source_dir))


def run():
    """
    Função principal que coordena o fluxo de execução (Pipeline) do processamento.
    """
    # Carregamento dos dados iniciais de despesas validadas e informações das operadoras
    despesas = carregar_despesas(INPUT_VALIDOS)
    operadoras = carregar_operadoras(OPERADORAS_DIR)

    # Etapa de Enriquecimento: Une os dados de despesas com os dados cadastrais das operadoras
    enriquecido = enriquecer_dados(despesas, operadoras)
    # Salva o resultado enriquecido em um novo arquivo CSV
    enriquecido.to_csv(OUTPUT_ENRIQUECIDO, index=False)

    # Etapa de Agregação: Consolida os dados enriquecidos (ex: somas por período ou categoria)
    agregado = agregar_dados(enriquecido)
    # Salva o resultado agregado em um arquivo CSV final
    agregado.to_csv(OUTPUT_AGREGADO, index=False)

    # Compacta a pasta de operadoras (contendo os resultados) para o arquivo ZIP final
    zip_dir(OPERADORAS_DIR, ZIP_OUTPUT)

    # Mensagens de confirmação no console
    print("[OK] Pipeline executado com sucesso.")
    print(f"[OK] ZIP gerado em: {ZIP_OUTPUT.resolve()}")


# Ponto de entrada do script
if __name__ == "__main__":
    run()