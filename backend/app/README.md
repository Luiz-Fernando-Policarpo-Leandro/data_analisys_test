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

# GET /api/operadoras/{cnpj}
**Descrição:**
Retorna os dados cadastrais de uma operadora específica diretamente do banco, normalizando o CNPJ para garantir consistência. Útil para detalhar uma operadora antes de exibir histórico de despesas ou métricas agregadas.
## Parâmetros de Caminho
| Nome | Tipo | Obrigatório | Descrição |
|------|------|------------|-----------|
| cnpj | string | Sim | CNPJ da operadora. Pode conter pontos, barras ou hífens; será normalizado automaticamente (apenas números). |

## Exemplo de Request
```
GET /api/operadoras/27.123.456/0001-89
```
## Exemplo de Response 200 OK
```json
{
  "id_operadora": 123,
  "registro_ans": 27,
  "cnpj": "27123456000189",
  "razao_social": "Operadora Exemplo S/A",
  "nome_fantasia": "Exemplo Saúde",
  "modalidade": "Seguros",
  "uf": "SP",
  "data_registro_ans": "2011-01-01"
}
```
## Códigos de Resposta
| Código | Significado | Condição |
|--------|------------|---------|
| 200 | OK | Operadora encontrada e dados retornados. |
| 404 | Not Found | Nenhuma operadora com o CNPJ informado. |

## Detalhes Técnicos
- Normalização do CNPJ: Todos os caracteres não numéricos são removidos antes da consulta (normalize_cnpj).
- Consulta SQL: Busca pelo CNPJ exato na tabela operadora.
- Tratamento de Erro: Se fetchone() retornar None, a rota dispara HTTPException(404).

## Observações
- Esta rota é essencial para integrar o frontend ao histórico de despesas e às estatísticas.
- Não faz paginação nem filtros: é busca única e direta por CNPJ.
- Ideal para uso em links clicáveis nas tabelas ou gráficos.

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

