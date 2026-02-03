# API de Operadoras e Despesas – ANS

## Teste Técnico – Backend & Integração de Dados

Este projeto implementa um pipeline completo de dados (ETL + banco relacional + API REST) utilizando dados públicos da ANS (Agência Nacional de Saúde Suplementar), conforme solicitado no teste técnico.

O escopo deste documento foca exclusivamente no BACKEND, atendendo explicitamente aos requisitos do item 4 do desafio.

---

## Mapeamento com o Enunciado do Teste

| Item do Teste | Atendido | Onde |
|--------------|----------|------|
| 4.1 Uso de dados do banco | Sim | PostgreSQL (ETL completo) |
| 4.2 API em Python | Sim | FastAPI |
| 4.2.1 Escolha do framework | Sim | Seção Backend |
| 4.2.2 Estratégia de paginação | Sim | GET /api/operadoras |
| 4.2.3 Cache vs cálculo | Sim | Estatísticas pré-calculadas |
| 4.2.4 Estrutura da resposta | Sim | Dados + metadados |
| 4.4 Documentação da API | Sim | README + OpenAPI |

---

## Arquitetura Geral do Projeto

```
.
├── backend/                 # Backend FastAPI
│   └── app/
│       ├── main.py          # Entry point da API
│       ├── core/            # Configurações e conexão com banco
│       ├── routers/         # Rotas da API
│       ├── models/          # Schemas Pydantic
│       └── utils/           # Utilidades (ex: normalização de CNPJ)
│
├── data/                    # Dados consolidados do ETL
├── sql/                     # Scripts SQL versionados (DDL, staging, analytics)
├── docker/                  # Infra local (PostgreSQL)
├── docs/                    # Documentação das Partes 1, 2 e 3
└── README.md
```

---

## Banco de Dados

### Escolha do Banco: PostgreSQL

Justificativa técnica:

- Funções analíticas nativas (STDDEV, AVG, CTEs)
- Excelente suporte a ingestão de CSV (COPY)
- Integridade referencial forte
- Compatível com Neon.tech (Postgres serverless)

### Modelo de Dados (Resumo)

- operadora – Entidade mestre
- despesa – Fato financeiro (ano, trimestre, valor)
- despesa_agregada – Estatísticas pré-calculadas
- tabelas _raw – Staging sem validação

O modelo segue o padrão staging → normalização → agregação, típico de pipelines analíticos.

---

## Backend – API REST em Python

### 4.2.1 Escolha do Framework – FastAPI

Opções avaliadas:

- Flask
- FastAPI

Justificativa da escolha:

- Performance superior (ASGI)
- Tipagem explícita com Pydantic
- Documentação automática (Swagger/OpenAPI)
- Melhor manutenção para APIs orientadas a dados

FastAPI foi escolhido por oferecer clareza de contrato, robustez e escalabilidade, mesmo em um projeto de escopo médio.

---

## Rotas Implementadas

### GET /api/operadoras

Lista paginada de operadoras.

Exemplo:

GET /api/operadoras?page=1&limit=20&q=amil

Funcionalidades:

- Paginação
- Busca por razão social ou CNPJ
- Retorno estruturado com metadados

### Estratégia de Paginação

Opções avaliadas:

- Offset-based
- Cursor-based
- Keyset pagination

Escolha: Offset-based

Justificativa:

- Volume de dados moderado
- Dados históricos e pouco mutáveis
- Simplicidade para o frontend
- Fácil compreensão para avaliação técnica

### GET /api/operadoras/{cnpj}

Retorna os dados cadastrais normalizados diretamente do banco.

### GET /api/operadoras/{cnpj}/despesas

Histórico de despesas da operadora.

- Série temporal (ano + trimestre)
- Dados financeiros em DECIMAL

### GET /api/estatisticas

Estatísticas globais:

- Total de despesas
- Média global
- Top 5 operadoras por volume financeiro

### Cache vs Queries Diretas

Opções avaliadas:

- Calcular sempre
- Cache temporário
- Pré-calcular e armazenar

Escolha: Pré-calcular em tabela (despesa_agregada)

Justificativa:

- Dados históricos
- Queries analíticas custosas
- Melhor previsibilidade e performance
- Padrão comum em ambientes analíticos

### GET /api/estatisticas/{cnpj}

Estatísticas por operadora:

- Total de despesas
- Média trimestral
- Desvio padrão

---

## Estrutura de Resposta da API

```json
{
  "data": [],
  "total": 100,
  "page": 1,
  "limit": 20
}
```

Justificativa:

- Facilita paginação no frontend
- Evita chamadas extras
- Padrão amplamente utilizado em APIs REST

---

## Configuração e Execução do Backend

### Variáveis de Ambiente

POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ans_db
POSTGRES_USER=ans_user
POSTGRES_PASSWORD=ans_pass

### Execução Local

cd backend
uvicorn app.main:app --reload

Swagger disponível em:
http://127.0.0.1:8000/docs

---

## Execução com Docker (Banco Local)

cd docker/postgres
docker-compose up -d

---

## Execução em Nuvem (Neon.tech)

- PostgreSQL serverless
- Ajuste apenas as variáveis de ambiente
- Nenhuma alteração no código

---

## Documentação da API

- Todas as rotas documentadas via OpenAPI
- Swagger disponível em /docs
- Coleção Postman exportável

Inclui:

- Exemplos de requisição
- Exemplos de resposta
- Paginação
- Erros (404, entradas inválidas)

---

## Tratamento de Erros

- 404 – Operadora não encontrada
- Validação de parâmetros (CNPJ, paginação)
- Listas vazias retornam [], não erro
- Mensagens claras e específicas para debug

---

## Conclusão Técnica

O backend foi desenvolvido para responder diretamente ao item 4 do teste, com foco em:

- Clareza arquitetural
- Decisões técnicas justificadas
- Performance previsível
- Fácil integração com frontend

