INSERT INTO operadora (
    registro_ans, cnpj, razao_social, nome_fantasia, modalidade, uf, data_registro_ans
)
SELECT DISTINCT
    CAST(registro_ans AS INTEGER),                 -- Conversão segura
    REGEXP_REPLACE(cnpj, '[^0-9]', '', 'g'),      -- Remove caracteres inválidos do CNPJ
    razao_social,
    nome_fantasia,
    modalidade,
    uf,
    CAST(data_registro_ans AS DATE)                -- Converte string para DATE
FROM operadora_raw
WHERE cnpj IS NOT NULL
  AND registro_ans IS NOT NULL;