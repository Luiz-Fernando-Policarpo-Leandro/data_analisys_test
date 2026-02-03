WITH primeira_ultima AS (
    SELECT 
        id_operadora,
        MIN(ano*10+trimestre) AS periodo_inicial,
        MAX(ano*10+trimestre) AS periodo_final
    FROM despesa
    GROUP BY id_operadora
),
valores_periodo AS (
    SELECT
        d.id_operadora,
        SUM(CASE WHEN (d.ano*10+d.trimestre) = p.periodo_inicial THEN d.valor ELSE 0 END) AS valor_inicial,
        SUM(CASE WHEN (d.ano*10+d.trimestre) = p.periodo_final THEN d.valor ELSE 0 END) AS valor_final
    FROM despesa d
    JOIN primeira_ultima p ON d.id_operadora = p.id_operadora
    GROUP BY d.id_operadora, p.periodo_inicial, p.periodo_final
)
SELECT 
    o.razao_social,
    vp.valor_inicial,
    vp.valor_final,
    CASE 
        WHEN vp.valor_inicial = 0 THEN NULL
        ELSE ROUND((vp.valor_final - vp.valor_inicial)/vp.valor_inicial*100, 2)
    END AS crescimento_percentual
FROM valores_periodo vp
JOIN operadora o ON vp.id_operadora = o.id_operadora
ORDER BY crescimento_percentual DESC NULLS LAST
LIMIT 5;

-- Query 2: Distribuição de despesas por UF
SELECT 
    o.uf,
    SUM(d.valor) AS total_uf
FROM despesa d
JOIN operadora o ON d.id_operadora = o.id_operadora
GROUP BY o.uf
ORDER BY total_uf DESC
LIMIT 5;

-- Média de despesas por operadora em cada UF
SELECT
    o.uf,
    o.razao_social,
    AVG(d.valor) AS media_operadora
FROM despesa d
JOIN operadora o ON d.id_operadora = o.id_operadora
GROUP BY o.uf, o.razao_social
ORDER BY o.uf, media_operadora DESC;

-- Query 3: Operadoras com despesas acima da média geral em >=2 trimestres
WITH media_geral AS (
    SELECT AVG(valor) AS media_geral FROM despesa
),
por_trimestre AS (
    SELECT 
        id_operadora,
        ano,
        trimestre,
        SUM(valor) AS total_trimestre
    FROM despesa
    GROUP BY id_operadora, ano, trimestre
),
acima_media AS (
    SELECT
        pt.id_operadora,
        COUNT(*) AS trimestres_acima_media
    FROM por_trimestre pt
    CROSS JOIN media_geral mg
    WHERE pt.total_trimestre > mg.media_geral
    GROUP BY pt.id_operadora
)
SELECT 
    o.razao_social,
    a.trimestres_acima_media
FROM acima_media a
JOIN operadora o ON a.id_operadora = o.id_operadora
WHERE a.trimestres_acima_media >= 2
ORDER BY a.trimestres_acima_media DESC;
