# Integração e Consolidação de Dados Públicos da ANS

Este repositório contém uma aplicação em Python que implementa um **pipeline completo** de integração, processamento, normalização, validação e consolidação de dados públicos disponibilizados pela **ANS (Agência Nacional de Saúde Suplementar)**.

O projeto foi desenvolvido como solução para um desafio técnico de integração com API pública, com foco em:

* Resiliência a dados inconsistentes
* Decisões técnicas justificáveis
* Organização clara e modular do código

⚠️ **Observação**: Este repositório utiliza exclusivamente **dados públicos**. Nenhuma informação sensível, privada ou confidencial é armazenada ou exposta.

# !!documentação!!
Aqui está documentado com mais detalhes todas as partes do projeto

➡️ **Consulte:** [1. TESTE DE INTEGRAÇÃO COM API PÚBLICA](docs/PARTE_1.md)

➡️ **Consulte:** [2. TESTE DE TRANSFORMAÇÃO E VALIDAÇÃO DE DADOS](docs/PARTE_2.md)

➡️ **Consulte:** [3. TESTE DE BANCO DE DADOS E ANÁLISE](docs/PARTE_3.md)

➡️ **Consulte:** [4.1 TESTE DE API E INTERFACE WEB - BACKEND](backend/app/README.md)

➡️ **Consulte:** [4.2 TESTE DE API E INTERFACE WEB - FRONTEND](frontend/README.md)

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
├── backend/
│   └── app/
│       ├── core/           # Configurações e Conexão com Banco
│       ├── models/         # Definição de Schemas (Pydantic)
│       ├── routers/        # Endpoints da API (Operadoras e Estatísticas)
│       ├── utils/          # Validadores (CNPJ)
│       └── main.py         # Arquivo de entrada do FastAPI
├── data/
│   ├── despesas/           # Fluxo de CSVs de despesas (Validados/Inválidos)
│   └── operadoras/         # CSVs de referência e saídas do pipeline
├── docker/
│   └── postgres/
│       └── docker-compose.yml
├── docs/                   # Documentação das Partes 1, 2 e 3 do desafio
├── frontend/
│   ├── src/
│   │   ├── api/            # Configuração Axios
│   │   ├── components/     # Componentes Vue (Gráficos/Tabelas)
│   │   ├── views/          # Páginas da aplicação
│   │   └── main.ts
│   ├── package.json
│   └── vite.config.ts
├── scripts/                # Scripts Python de ETL e Processamento
├── sql/                    # Scripts SQL organizados por etapas (DDL a Analytics)
├── requirements.txt
└── README.md
```

## Banco de Dados

O projeto utiliza **PostgreSQL 16**, com docker-compose, como banco de dados principal.
A modelagem é **normalizada**, garantindo integridade, rastreabilidade e boa performance para queries analíticas.

### Estrutura principal dos arquvios csv

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
* API FLASK
* Frontend Vue, Typescript
* Sistema operacional Linux, macOS ou Windows

## Instalação e Execução
Para prosseguir, crie dois terminais e cole os comandos
## Terminal 1

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

4. Executar o pipeline

   ```bash
      python main.py
   ```


5. Subir PostgreSQL via Docker, Carregar e processar no PostgreSQL

   ```bash
      cd docker/postgres
      docker compose up -d
      # carregar dados
      docker exec -it ans_postgres psql -U ans_user -d ans_db -f /sql/run_all.sql
      # backup para a nuvem
      docker exec -t ans_postgres pg_dump -U ans_user -d ans_db -Fc   --no-owner --no-privileges   > ../backup/ans_db.dump
   ```

6. Voltar para o `/app`
   ```bash
         cd ../..
   ```


7. Subir Server Backend

   ```bash
      # app/backend
      cd backend
      uvicorn app.main:app --reload

   ```

## Terminal 2

8. Subir Server Frontend

   ```bash
      # /app
      cd frontend
      npm install
      npm run dev
   ```

## Arquivos Gerados

* arquivos zip: `Teste_Luiz_Fernando_Policarpo_leandro.zip` e `consolidado_despesas.zip` estão na raiz do projeto

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
