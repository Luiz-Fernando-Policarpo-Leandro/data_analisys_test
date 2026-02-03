COPY operadora_raw FROM '/data/operadoras/Relatorio_cadop.csv'
DELIMITER ';'
CSV HEADER
ENCODING 'UTF8';

COPY despesa_raw FROM '/data/operadoras/despesas_enriquecidas.csv'
DELIMITER ','
CSV HEADER
ENCODING 'UTF8';