DROP TABLE IF EXISTS operadora_raw;
CREATE TABLE operadora_raw (
    registro_ans TEXT,             -- Identificador ANS (pode ter duplicados no CSV)
    cnpj TEXT,                     -- CNPJ com possíveis caracteres especiais
    razao_social TEXT,             -- Nome completo da operadora
    nome_fantasia TEXT,            -- Nome fantasia, pode ser NULL
    modalidade TEXT,               -- Tipo de operadora
    logradouro TEXT,
    numero TEXT,
    complemento TEXT,
    bairro TEXT,
    cidade TEXT,
    uf TEXT,                       -- Estado, deve ser CHAR(2) após normalização
    cep TEXT,
    ddd TEXT,
    telefone TEXT,
    fax TEXT,
    endereco_eletronico TEXT,
    representante TEXT,
    cargo_representante TEXT,
    regiao_comercializacao TEXT,
    data_registro_ans TEXT         -- Data de registro no formato CSV, será convertida depois
);


DROP TABLE IF EXISTS despesa_raw;
CREATE TABLE despesa_raw (
    registro_ans TEXT,
    cnpj TEXT,
    razao_social TEXT,
    modalidade TEXT,
    uf TEXT,
    trimestre TEXT,                -- Trimestre como texto, será convertido para SMALLINT
    ano TEXT,                      -- Ano como texto, será convertido
    valor TEXT                     -- Valor como texto, pode conter caracteres inválidos
);