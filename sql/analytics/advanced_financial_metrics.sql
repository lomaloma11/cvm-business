-- 1. Retorno Diário da Cota e Média Móvel de Captação (SMA 7 Dias)
WITH cotas_com_lag AS (
    SELECT 
        cnpj_fundo,
        dt_comptc,
        vl_quota,
        capt_liquida_dia,
        LAG(vl_quota) OVER (
            PARTITION BY cnpj_fundo 
            ORDER BY dt_comptc
        ) AS vl_quota_anterior
    FROM fact_informe_diario
)
SELECT 
    f.denom_social,
    c.cnpj_fundo,
    c.dt_comptc,
    c.vl_quota,
    ROUND(CAST(((c.vl_quota - c.vl_quota_anterior) / NULLIF(c.vl_quota_anterior, 0)) * 100 AS NUMERIC), 4) AS retorno_diario_pct,
    ROUND(AVG(c.capt_liquida_dia) OVER (
        PARTITION BY c.cnpj_fundo 
        ORDER BY c.dt_comptc 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ), 2) AS media_movel_captacao_7d
FROM cotas_com_lag c
JOIN dim_fund f ON c.cnpj_fundo = f.cnpj_fundo AND f.is_current = TRUE
WHERE c.vl_quota_anterior IS NOT NULL;

-- 2. Análise de Drawdown (Queda Máxima em Relação ao Pico Histórico)
WITH pico_historico AS (
    SELECT 
        cnpj_fundo,
        dt_comptc,
        vl_quota,
        MAX(vl_quota) OVER (
            PARTITION BY cnpj_fundo 
            ORDER BY dt_comptc 
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cota_maxima_historica
    FROM fact_informe_diario
)
SELECT 
    p.cnpj_fundo,
    p.dt_comptc,
    p.vl_quota,
    p.cota_maxima_historica,
    ROUND(CAST(((p.vl_quota - p.cota_maxima_historica) / NULLIF(p.cota_maxima_historica, 0)) * 100 AS NUMERIC), 2) AS drawdown_pct
FROM pico_historico p
ORDER BY drawdown_pct ASC;