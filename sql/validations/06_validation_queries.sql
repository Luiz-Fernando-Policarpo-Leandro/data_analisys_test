SELECT COUNT(*) AS despesas_sem_operadora
FROM despesa
WHERE id_operadora IS NULL;

-- 5.2 Trimestres inválidos (fora do intervalo 1-4)
SELECT *
FROM despesa
WHERE trimestre NOT BETWEEN 1 AND 4;

-- 5.3 Valores negativos ou zero
SELECT *
FROM despesa
WHERE valor <= 0;