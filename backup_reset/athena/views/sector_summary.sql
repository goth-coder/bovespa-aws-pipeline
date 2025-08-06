-- View consolidada para análise de setores
-- Agrega informações por setor para facilitar análises

CREATE OR REPLACE VIEW vw_sector_summary AS
SELECT 
    setor,
    COUNT(*) as qtd_acoes,
    SUM(part_percent) as participacao_total,
    AVG(part_percent) as participacao_media,
    SUM(theoretical_qty) as quantidade_teorica_total,
    MAX(extraction_date) as ultima_atualizacao
FROM bovespa_curated
WHERE setor IS NOT NULL
GROUP BY setor;
