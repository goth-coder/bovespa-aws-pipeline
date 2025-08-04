-- View para ranking de ações
-- Lista ações ordenadas por participação com informações adicionais

CREATE OR REPLACE VIEW vw_stock_ranking AS
SELECT 
    codigo,
    acao,
    setor,
    part_percent,
    theoretical_qty,
    RANK() OVER (ORDER BY part_percent DESC) as ranking_participacao,
    CASE 
        WHEN part_percent >= 5.0 THEN 'Alto Peso'
        WHEN part_percent >= 2.0 THEN 'Médio Peso'
        WHEN part_percent >= 1.0 THEN 'Baixo Peso'
        ELSE 'Peso Mínimo'
    END AS categoria_peso,
    extraction_date
FROM bovespa_curated
WHERE part_percent > 0;
