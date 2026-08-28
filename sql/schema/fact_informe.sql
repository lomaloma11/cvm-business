-- Tabela Fato: Informes Diários
CREATE TABLE IF NOT EXISTS fact_informe_diario (
    informe_id SERIAL PRIMARY KEY,
    cnpj_fundo VARCHAR(14) NOT NULL,
    dt_comptc DATE NOT NULL,
    vl_total NUMERIC(18, 2),
    vl_quota NUMERIC(25, 8),
    vl_patrim_liq NUMERIC(18, 2),
    captc_dia NUMERIC(18, 2),
    resg_dia NUMERIC(18, 2),
    nr_cotst INT,
    capt_liquida_dia NUMERIC(18, 2)
);

CREATE INDEX IF NOT EXISTS idx_fact_cnpj ON fact_informe_diario(cnpj_fundo);
CREATE INDEX IF NOT EXISTS idx_fact_date ON fact_informe_diario(dt_comptc);