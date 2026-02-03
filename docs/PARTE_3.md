
## 3. Fontes de Dados e Decisão Técnica

### 3.1 Dados utilizados

- `despesas_enriquecidas.csv` → registro detalhado de cada despesa
- `Relatorio_cadop.csv` → cadastro completo das operadoras

### 3.2 Justificativa da Escolha das Fontes e Abordagem

### 3.3 Por que **não** usar os arquivos agregados?

| Problema                  | Impacto                                                                 |
|---------------------------|-------------------------------------------------------------------------|
| Granularidade perdida     | Impossível recalcular médias, desvios, crescimentos, filtros customizados |
| Auditabilidade comprometida | Não se sabe quais registros originais geraram cada total               |
| Flexibilidade limitada    | Novas regras (ex.: excluir negativos, duplicados) exigem reprocessar tudo manualmente |
| Risco de inconsistência   | Qualquer correção nos dados brutos exige regeneração manual dos agregados |
**Decisão tomada:**  
Usar **apenas** os dados granulares (`despesas_enriquecidas.csv` + `Relatorio_cadop.csv`) como **fonte da verdade** (fonte primária e oficial).

Todos os outros arquivos agregados que foram sugeridos (`despesas_agregadas.csv`, `operadoras_agregadas.csv`.) **não são utilizados como fonte de entrada** no pipeline.  

Eles são **gerados apenas para fins de consulta rápida, validação cruzada ou knowledge** (conhecimento de referência), mas **não** participam do fluxo de processamento nem são considerados fonte confiável.

Todas as agregações, métricas derivadas (totais, médias, desvios padrão, crescimentos percentuais, etc.) são **sempre recalculadas diretamente a partir dos dados granulares no banco de dados**, garantindo:

- **Reprodutibilidade** total do processo  
- **Controle completo** sobre os cálculos  
- **Auditabilidade** linha a linha  
- Consistência mesmo após correções ou atualizações nos arquivos originais

### 3.4 Benefícios da abordagem adotada

- Reprocessamento confiável a qualquer momento  
- Métricas calculadas sob demanda e auditáveis  
- Dados rastreáveis até a linha original  
- Suporte a queries analíticas complexas (window functions, CTEs, etc.)  
- Fácil adição de novas agregações / visões sem tocar na fonte original


## 4. Pipeline de Execução

1. Rodar Docker com PostgreSQL  
   `docker-compose up -d`

2. Rodar script de padronização  
   `python scripts/run_format_csv.py`

3. Executar pipeline SQL completo  
   `\i /sql/run_all.sql`  
   (cria tabelas, carrega staging, normaliza dados, gera agregados e validações)

4. Executar queries analíticas  
   via `sql/analytics/07_analytics.sql` ou diretamente no `psql`

**Observação:** todo o pipeline é **reproduzível**, **auditável** e **escalável**.

## 5. Banco de Dados – Modelo e DDL

### 5.1 Abordagem escolhida: normalização

| Escolha                        | Justificativa                                                                 |
|--------------------------------|-------------------------------------------------------------------------------|
| Normalizado (3 tabelas)        | Facilita queries analíticas, evita duplicação, mantém auditabilidade          |
| `DECIMAL` para valores         | Precisão monetária, evita erros de `FLOAT`                                    |
| `DATE` para datas              | Permite cálculos e ordenações corretas                                        |
| `CHAR(14)` para CNPJ           | Identificador fixo, evita perda de zeros à esquerda                           |

### 5.2 Estrutura resumida das tabelas

- **operadora**  
  `id_operadora`, `registro_ans`, `cnpj`, `razao_social`, `nome_fantasia`, `modalidade`, `uf`, `data_registro_ans`

- **despesa**  
  `id_despesa`, `id_operadora (FK)`, `ano`, `trimestre`, `valor`

- **despesa_agregada**  
  `id_operadora (FK)`, `ano`, `total_despesas`, `media_trimestral`, `desvio_padrao`

## 6. Estratégia de Ingestão e Transformação

1. CSVs brutos → tabelas `staging` (`*_raw`)
2. Padronização de tipos via `CAST` e `REGEXP_REPLACE` (CNPJs, datas, valores)
3. Inserção nas tabelas finais
4. Criação da tabela agregada derivada (`despesa_agregada`)
5. Validação pós-carga:
   - Despesas sem operadora
   - Trimestre fora do intervalo 1–4
   - Valores ≤ 0

**Decisão técnica:** uso de staging permite controlar inconsistências e rejeitar/corrigir registros inválidos antes de popular as tabelas finais.

## 7. Queries Analíticas

- **Query 1**: 5 operadoras com maior crescimento percentual entre primeiro e último trimestre
- **Query 2**: Distribuição de despesas por UF + média por operadora
- **Query 3**: Operadoras com despesas acima da média em ≥2 trimestres

**Observações:**

- Operadoras sem todos os trimestres → consideradas apenas nos trimestres existentes
- Base de cálculo → tabela de fatos (`despesa`), **não** agregados do CSV

## 8. Execução com Docker

```bash
# Subir container
cd app/docker/postgres
docker-compose up -d

# Conectar ao Postgres
docker exec -it ans_postgres psql -U ans_user -d ans_db

# Rodar pipeline completo
\i /sql/run_all.sql

```

## Isso irá:

* Criar tabelas staging e finais
* Padronizar dados
* Inserir fatos e dimensões
* Criar agregados e índices
* Executar validações