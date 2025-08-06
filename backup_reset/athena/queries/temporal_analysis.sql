-- Query para evolução temporal das participações
-- Análise de mudanças ao longo do tempo

SELECT 
    year,
    month,
    day,
    COUNT(*) as total_acoes_dia,
    SUM(part_percent) as participacao_total_dia,
    AVG(part_percent) as participacao_media_dia
FROM bovespa_curated
GROUP BY year, month, day
ORDER BY year DESC, month DESC, day DESC;
