DROP TABLE IF EXISTS operadora CASCADE;
CREATE TABLE operadora (
    id_operadora        BIGSERIAL PRIMARY KEY,  -- Chave técnica estável
    registro_ans        INTEGER UNIQUE NOT NULL,-- Identificador ANS único
    cnpj                CHAR(14) UNIQUE NOT NULL, -- CNPJ formatado apenas com números
    razao_social        VARCHAR(255) NOT NULL,  -- Nome legal da operadora
    nome_fantasia       VARCHAR(255),           -- Nome fantasia opcional
    modalidade          VARCHAR(100) NOT NULL,  -- Tipo de operadora
    uf                  CHAR(2) NOT NULL,       -- Estado
    data_registro_ans   DATE NOT NULL           -- Conversão segura do CSV
);

-- Índices para performance de joins e filtros
CREATE INDEX idx_operadora_cnpj ON operadora (cnpj);
CREATE INDEX idx_operadora_uf ON operadora (uf);

-- =========================================================
DROP TABLE IF EXISTS despesa CASCADE;
CREATE TABLE despesa (
    id_despesa      BIGSERIAL PRIMARY KEY,  -- Identificador único do fato financeiro
    id_operadora    BIGINT NOT NULL REFERENCES operadora(id_operadora), -- FK para integridade
    ano             SMALLINT NOT NULL CHECK (ano >= 2000),             -- Restrição de ano válido
    trimestre       SMALLINT NOT NULL CHECK (trimestre BETWEEN 1 AND 4), -- Restrição de trimestre válido
    valor           DECIMAL(15,2) NOT NULL CHECK (valor > 0)          -- DECIMAL para precisão monetária
);

-- Índices para melhorar performance de queries analíticas
CREATE INDEX idx_despesa_operadora ON despesa (id_operadora);
CREATE INDEX idx_despesa_tempo ON despesa (ano, trimestre);

-- =========================================================
DROP TABLE IF EXISTS despesa_agregada;
CREATE TABLE despesa_agregada (
    id_operadora        BIGINT NOT NULL REFERENCES operadora(id_operadora),
    ano                 SMALLINT NOT NULL,
    total_despesas      DECIMAL(18,2) NOT NULL,
    media_trimestral    DECIMAL(18,2) NOT NULL,
    desvio_padrao       DECIMAL(18,4) NOT NULL,
    PRIMARY KEY (id_operadora, ano)
);