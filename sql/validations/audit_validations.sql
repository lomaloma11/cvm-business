-- AUDITORIA DE VOLUME E TOTALIZADORES GERAIS
-- Verifica quantidade de linhas, fundos ativos e total consolidado de movimentações.
SELECT 
    COUNT(*) AS total_registros_fato,
    COUNT(DISTINCT cnpj_fundo) AS total_fundos_distintos,
    COUNT(DISTINCT dt_comptc) AS total_dias_operados,
    COUNT(CASE WHEN captc_dia > 0 OR resg_dia > 0 THEN 1 END) AS dias_com_movimentacao,
    ROUND(SUM(captc_dia)::numeric, 2) AS total_captacao_bruta,
    ROUND(SUM(resg_dia)::numeric, 2) AS total_resgate_bruto,
    ROUND(SUM(capt_liquida_dia)::numeric, 2) AS captacao_liquida_total
FROM fact_informe_diario;


-- TESTE DE INTEGRIDADE REFERENCIAL (CHECAGEM DE REGISTROS ÓRFÃOS)
-- Resultado esperado: 0 órfãos (100% dos informes devem apontar para a dim_fund).
SELECT 
    COUNT(*) AS total_informes_orfaos
FROM fact_informe_diario f
LEFT JOIN dim_fund d ON f.cnpj_fundo = d.cnpj_fundo
WHERE d.cnpj_fundo IS NULL;


-- TESTE DE REGRAS DE NEGÓCIO E LIMITES FINANCEIROS (DATA QUALITY GATES)
-- Resultado esperado: 0 para todas as colunas (sem valores negativos ou nulos indevidos).
SELECT 
    COUNT(CASE WHEN vl_patrim_liq <= 0 THEN 1 END) AS pl_invalido_zerado_ou_negativo,
    COUNT(CASE WHEN vl_quota <= 0 THEN 1 END) AS cota_invalida_zerada_ou_negativa,
    COUNT(CASE WHEN captc_dia < 0 THEN 1 END) AS captacao_negativa,
    COUNT(CASE WHEN resg_dia < 0 THEN 1 END) AS resgate_negativo
FROM fact_informe_diario;


-- VALIDAÇÃO DE CRUZAMENTO MODELO DIMENSIONAL (TOP 10 ADMINISTRADORES)
-- Valida o relacionamento entre tabelas e coerência das agregações analíticas.
SELECT 
    d.admin,
    COUNT(DISTINCT d.cnpj_fundo) AS qtd_fundos,
    ROUND(SUM(f.capt_liquida_dia)::numeric, 2) AS captacao_liquida_total,
    ROUND(AVG(f.vl_patrim_liq)::numeric, 2) AS media_patrimonio_liquido
FROM fact_informe_diario f
INNER JOIN dim_fund d ON f.cnpj_fundo = d.cnpj_fundo
GROUP BY d.admin
ORDER BY media_patrimonio_liquido DESC
LIMIT 10;