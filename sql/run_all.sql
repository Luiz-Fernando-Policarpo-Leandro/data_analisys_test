-- run_all.sql
-- 3. Criação das tabelas finais
\i /sql/ddl/01_create_tables.sql

-- 1. Criação das tabelas staging
\i /sql/staging/02_create_staging.sql

-- 2. Carga dos CSVs
\i /sql/staging/03_load_csv.sql

-- 4. Normalização / inserção em tabelas finais
\i /sql/transforms/04_normalize_operadora.sql
\i /sql/transforms/05_normalize_despesa.sql

-- 5. Validações pós-carga
\i /sql/validations/06_validation_queries.sql

-- 6. Queries analíticas
\i /sql/analytics/07_analytics.sql
