-- Tabela Dimensão: Cadastro de Fundos com SCD Type 2 (Histórico de Mudanças)
CREATE TABLE IF NOT EXISTS dim_fund (
    fund_sk SERIAL PRIMARY KEY,             -- Surrogate Key única
    cnpj_fundo VARCHAR(14) NOT NULL,
    denom_social VARCHAR(255) NOT NULL,
    classe VARCHAR(100),
    tp_fundo VARCHAR(50),
    publico_alvo VARCHAR(100),
    admin VARCHAR(255),
    gestor VARCHAR(255),
    sg_uf VARCHAR(2),
    municipio VARCHAR(150),
    valid_from DATE NOT NULL DEFAULT CURRENT_DATE,  -- Controle SCD Type 2
    valid_to DATE,                                 -- Controle SCD Type 2
    is_current BOOLEAN NOT NULL DEFAULT TRUE       -- Indicador do registro ativo
);

-- Tabela Dimensão: Calendário
CREATE TABLE IF NOT EXISTS dim_date (
    date_id INT PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    day INT NOT NULL,
    month INT NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    quarter INT NOT NULL,
    year INT NOT NULL
);