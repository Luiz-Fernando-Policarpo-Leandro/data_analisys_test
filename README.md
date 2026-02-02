# Integração e Consolidação de Dados Públicos da ANS

Este repositório contém uma aplicação em **Python** que implementa um pipeline completo de **integração, processamento, normalização, validação e consolidação** de dados públicos disponibilizados pela **ANS (Agência Nacional de Saúde Suplementar)**.

O projeto foi desenvolvido como uma solução prática para um desafio técnico de integração com API pública, com foco em **resiliência a dados inconsistentes**, **decisões técnicas justificáveis** e **organização clara do código**.

> ⚠️ **Observação**: Este repositório utiliza **exclusivamente dados públicos**. Nenhuma informação sensível, privada ou confidencial é armazenada ou exposta.

---

## Visão geral da solução

A aplicação automatiza as seguintes etapas:

1. Acesso ao repositório público de dados da ANS (via HTTP/FTP)
2. Identificação automática de arquivos de **Demonstrações Contábeis** organizados por ano e trimestre
3. Seleção dos **últimos 3 trimestres disponíveis de cada ano**
4. Download paralelo dos arquivos compactados (ZIP)
5. Extração automática dos arquivos internos
6. Leitura de múltiplos formatos (CSV, TXT, XLS, XLSX)
7. Normalização dinâmica das colunas relevantes
8. Tratamento de datas e identificação de ano/trimestre mesmo em layouts inconsistentes
9. Consolidação dos dados em um único CSV
10. Validação e classificação dos registros conforme regras de negócio
11. Geração de múltiplos arquivos finais e compactação do consolidado

A aplicação é **idempotente**: caso o arquivo consolidado já exista, o pipeline reutiliza o resultado sem refazer downloads ou processamento.

---

## Estrutura do projeto

```
app/
├─ data/                     # Dados processados e resultados finais
│  ├─ despesas/              # Dados de despesas consolidados
│  │  ├─ valido/             # Registros válidos após validação
│  │  ├─ invalidos/          # Registros inválidos segregados por regra
│  │  └─ consolidado_despesas.csv
│  │
│  └─ operadoras/            # Dados enriquecidos com cadastro ANS
│     ├─ Relatorio_cadop.csv
│     ├─ despesas_enriquecidas.csv
│     └─ despesas_agregadas.csv
│
├─ docs/                     # Documentação técnica
│  ├─ PARTE_1.md             # Coleta, normalização e consolidação
│  └─ PARTE_2.md             # Validação, enriquecimento e agregação
│
├─ scripts/                  # Scripts executáveis
│  ├─ run_integration.py     # Pipeline da Parte 1
│  └─ run_aggregate.py       # Pipeline da Parte 2
│
├─ utils/                    # Funções reutilizáveis
│  ├─ file_utils.py          # Download, leitura e extração de arquivos
│  ├─ cnpj_utils.py          # Normalização e validação de CNPJ
│  ├─ enrich_utils.py        # Enriquecimento com dados cadastrais
│  ├─ aggregate_utils.py     # Agregações estatísticas
│  └─ dataframe_utils.py     # Utilitários genéricos de DataFrame
│
├─ consolidado_despesas.zip  # Entrega Parte 1
├─ operadoras.zip            # Entrega Parte 2
├─ requirements.txt
└─ README.md

```

---

## Requisitos

* Python **3.10 ou superior**
* pip
* Acesso à internet
* Sistema operacional Linux, macOS ou Windows

---

## Instalação

### 1. Clonar o repositório

```bash
git clone <https://github.com/Luiz-Fernando-Policarpo-Leandro/data_analisys_test>
cd app
```

### 2. Criar ambiente virtual (venv)

```bash
python3 -m venv venv
```

### 3. Ativar o ambiente virtual

Linux / macOS:

```bash
source venv/bin/activate
```

Windows:

```bash
venv\\Scripts\\activate
```

### 4. Instalar dependências

```bash
pip install -r requirements.txt
```

---

## Como executar

Com o ambiente virtual ativo:

```bash
python main.py
```

Durante a execução, o programa:

* Lista os arquivos identificados por ano e trimestre
* Realiza downloads paralelos (I/O bound)
* Processa os arquivos em paralelo (CPU bound)
* Normaliza estruturas diferentes automaticamente
* Gera os arquivos finais na pasta `/data`

---

## Arquivos gerados

### Arquivo consolidado

* `consolidado_despesas.csv`

### Arquivos derivados por validação

**Válidos**

* `valido/consolidado_validos.csv`

**Inválidos**

* `invalidos/consolidado_numero_negativo_invalido.csv`
* `invalidos/consolidado_valor_zero.csv`
* `invalidos/consolidado_cnpj_invalido.csv`

**Operadoras**
* `despesas_agregadas.csv`
* `despesas_enriquecidas.csv`
* `Relatorio_cadop.csv`

### Compactados

* `consolidado_despesas.zip`
* `operadoras.zip`

---

## Regras de validação aplicadas

* **CNPJ válido**: validação de formato e dígitos verificadores
* **Valores positivos**: considerados válidos
* **Valores negativos**: classificados separadamente
* **Valores zero**: classificados separadamente
* **CNPJ inválido**: separado independentemente do valor

Essas decisões foram tomadas para preservar **rastreabilidade**, **auditabilidade** e **análise posterior de inconsistências**.

---

## Detalhamento técnico

A explicação detalhada da implementação da **Das partes do projeto** — incluindo decisões técnicas, trade-offs, estratégia de parsing, paralelismo e normalização — está documentada separadamente.

➡️ **Consulte:** [1. TESTE DE INTEGRAÇÃO COM API PÚBLICA](docs/PARTE_1.md)

➡️ **Consulte:** [2. TESTE DE TRANSFORMAÇÃO E VALIDAÇÃO DE DADOS](docs/PARTE_2.md)

---

## Considerações técnicas

* ThreadPoolExecutor para tarefas I/O bound (downloads)
* ProcessPoolExecutor para processamento pesado
* Detecção automática de layout e colunas
* Uso de tipos Int64 (nullable) do pandas
* Código tolerante a inconsistências da origem

---



## Finalidade

Este projeto tem finalidade **educacional e técnica**, demonstrando capacidade de:

* Resolver problemas práticos com dados reais
* Engenharia de dados aplicada, Código modular, limpo e documentado
* Automação de pipelines, Código modular, limpo e documentado
* Tomar decisões técnicas fundamentadas
* Documentar escolhas e trade-offs
* Produzir código organizado, legível e resiliente


