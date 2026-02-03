
INSERT INTO despesa (id_operadora, ano, trimestre, valor)
SELECT
    o.id_operadora,
    CAST(d.ano AS SMALLINT),
    CAST(d.trimestre AS SMALLINT),
    CAST(d.valor AS DECIMAL(15,2))
FROM despesa_raw d
JOIN operadora o
  ON REGEXP_REPLACE(d.cnpj, '[^0-9]', '', 'g') = o.cnpj
WHERE d.valor ~ '^[0-9]+(\.[0-9]+)?$'; -- Filtra valores válidos, strings inválidas são ignoradas

-- 4.3 Gerar tabela agregada (materializada)
INSERT INTO despesa_agregada (id_operadora, ano, total_despesas, media_trimestral, desvio_padrao)
SELECT
    id_operadora,
    ano,
    SUM(valor) AS total_despesas,
    AVG(valor) AS media_trimestral,
    STDDEV_POP(valor) AS desvio_padrao
FROM despesa
GROUP BY id_operadora, ano;
