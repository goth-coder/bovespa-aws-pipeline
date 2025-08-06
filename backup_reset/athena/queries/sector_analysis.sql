-- Query para análise de participação por setor
-- Calcula participação total e média por setor no IBOV

SELECT 
    setor,
    COUNT(*) as total_acoes,
    SUM(part_percent) as participacao_total_setor,
    AVG(part_percent) as participacao_media_setor,
    MAX(part_percent) as maior_participacao,
    MIN(part_percent) as menor_participacao
FROM bovespa_curated
WHERE setor IS NOT NULL
GROUP BY setor
ORDER BY participacao_total_setor DESC;
