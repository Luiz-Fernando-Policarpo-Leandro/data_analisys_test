# Integração e Consolidação de Dados Públicos da ANS

Este repositório contém uma aplicação em Python que implementa um **pipeline completo** de integração, processamento, normalização, validação e consolidação de dados públicos disponibilizados pela **ANS (Agência Nacional de Saúde Suplementar)**.

O projeto foi desenvolvido como solução para um desafio técnico de integração com API pública, com foco em:

* Resiliência a dados inconsistentes
* Decisões técnicas justificáveis
* Organização clara e modular do código

⚠️ **Observação**: Este repositório utiliza exclusivamente **dados públicos**. Nenhuma informação sensível, privada ou confidencial é armazenada ou exposta.

## Visão Geral da Solução

A aplicação automatiza as seguintes etapas:

1. Acesso ao repositório público de dados da ANS (via HTTP/FTP)
2. Identificação automática de arquivos de Demonstrações Contábeis organizados por ano e trimestre
3. Seleção dos **últimos 3 trimestres disponíveis** de cada ano
4. Download paralelo dos arquivos compactados (ZIP)
5. Extração automática dos arquivos internos
6. Leitura de múltiplos formatos (CSV, TXT, XLS, XLSX)
7. Normalização dinâmica das colunas relevantes
8. Tratamento de datas e identificação de ano/trimestre mesmo em layouts inconsistentes
9. Consolidação dos dados em um único CSV
10. Validação e classificação dos registros conforme regras de negócio
11. Enriquecimento com dados cadastrais de operadoras
12. Agregação por operadora e UF
13. Criação de tabelas normalizadas e carregamento em **PostgreSQL**
14. Geração de arquivos derivados e compactação

A aplicação é **idempotente**: caso os arquivos finais já existam, o pipeline reutiliza os resultados sem refazer downloads ou processamento.

## Estrutura do Projeto

```
app/
├─ data/
│  ├─ csv/                   # CSVs brutos
│  ├─ despesas/
│  │  ├─ valido/
│  │  ├─ invalidos/
│  │  └─ consolidado_despesas.csv
│  │
│  └─ operadoras/
│     ├─ Relatorio_cadop.csv
│     ├─ despesas_enriquecidas.csv
│     └─ despesas_agregadas.csv
│
├─ docs/
│  ├─ PARTE_1.md
│  ├─ PARTE_2.md
│  └─ PARTE_3.md             # Pipeline de banco de dados, normalização e queries analíticas
│
├─ scripts/
│  ├─ run_integration.py     # Coleta e consolidação
│  └─ run_aggregate.py       # Validação, enriquecimento e agregação
│
├─ utils/
│  ├─ file_utils.py
│  ├─ cnpj_utils.py
│  ├─ enrich_utils.py
│  ├─ aggregate_utils.py
│  └─ dataframe_utils.py
│
├─ docker/
│  └─ postgres/
│     └─ docker-compose.yml
│
├─ sql/
│  ├─ ddl/                   # Criação das tabelas
│  │  └─ 01_create_tables.sql
│  ├─ staging/               # Staging para importação segura
│  │  ├─ 02_create_staging.sql
│  │  └─ 03_load_csv.sql
│  ├─ transforms/            # Normalização
│  │  ├─ 04_normalize_operadora.sql
│  │  └─ 05_normalize_despesa.sql
│  ├─ validations/           # Validações
│  │  └─ 06_validation_queries.sql
│  └─ analytics/             # Queries analíticas
│     └─ 07_analytics.sql
│
├─ consolidado_despesas.zip
├─ operadoras.zip
├─ requirements.txt
└─ README.md
```

## Banco de Dados

O projeto utiliza **PostgreSQL 16** como banco de dados principal.
A modelagem é **normalizada**, garantindo integridade, rastreabilidade e boa performance para queries analíticas.

### Estrutura principal

* `operadora` → dimensões das operadoras
* `despesa` → fatos financeiros atômicos (despesas por trimestre)
* `despesa_agregada` → agregados de performance / relatórios

### Observações técnicas

* Tipos de dados escolhidos para precisão monetária (`DECIMAL`) e consistência temporal (`SMALLINT`, `TINYINT`, `DATE`)
* Tabelas **staging** para importação segura de CSVs antes da normalização
* Índices estratégicos para joins e filtros frequentes
* Pipeline de carregamento em duas versões:

  * Docker local para desenvolvimento (`docker compose up`)
  * Neon.tech (PostgreSQL serverless) para demonstração e produção

Para detalhes completos sobre a modelagem, DDL, staging e queries analíticas, consulte:
➡️ **PARTE 3 — Banco de dados e análise**

## Requisitos

* Python 3.10 ou superior
* pip
* Docker (para ambiente local)
* Acesso à internet
* Sistema operacional Linux, macOS ou Windows

## Instalação e Execução

1. Clonar o repositório

   ```bash
   git clone https://github.com/Luiz-Fernando-Policarpo-Leandro/data_analisys_test
   cd app
   ```

2. Criar e ativar ambiente virtual

   ```bash
   python3 -m venv venv  # Linux / macOS
   source venv/bin/activate

   # Windows
   venv\Scripts\activate
   ```

3. Instalar dependências

   ```bash
   pip install -r requirements.txt
   ```

4. Subir PostgreSQL via Docker (opcional – local)

   ```bash
   cd docker/postgres
   docker compose up -d
   ```

5. Executar o pipeline

   ```bash
   python main.py
   ```

6. Carregar e processar no PostgreSQL

   ```sql
   \i sql/run_all.sql
   ```

   > No Neon.tech, substitua COPY por \copy para importar CSVs do cliente local.

## Arquivos Gerados

* Despesas consolidadas: `data/despesas/consolidado_despesas.csv`

* Despesas válidas: `data/despesas/valido/consolidado_validos.csv`

* Despesas inválidas: `data/despesas/invalidos/` (CNPJ inválido, valor zero, valor negativo)

* Operadoras:

  * `data/operadoras/Relatorio_cadop.csv`
  * `data/operadoras/despesas_enriquecidas.csv`
  * `data/operadoras/despesas_agregadas.csv`

* Compactados:

  * `consolidado_despesas.zip`
  * `operadoras.zip`

## Regras de Validação Aplicadas

* CNPJ válido (formato e dígitos verificadores)
* Valores positivos → válidos
* Valores negativos → classificados separadamente
* Valores zero → classificados separadamente
* CNPJs sem cadastro → separados

Essas decisões garantem rastreabilidade, auditabilidade e consistência para análises posteriores.

## Considerações Técnicas

* Pipeline idempotente
* `ThreadPoolExecutor` para downloads (I/O bound)
* `ProcessPoolExecutor` para processamento pesado (CPU bound)
* Tratamento automático de múltiplos formatos e layouts inconsistentes
* Uso de staging para validação e normalização antes do carregamento final
* Docker e Neon.tech garantem portabilidade e reprodutibilidade

## Finalidade do Projeto

O projeto demonstra capacidade de:

* Resolver problemas práticos com dados reais
* Implementar engenharia de dados robusta
* Produzir código modular, limpo e bem documentado
* Tomar decisões técnicas fundamentadas e justificar trade-offs
* Criar pipelines reprodutíveis e escaláveis
