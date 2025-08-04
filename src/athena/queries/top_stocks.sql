-- Query para top 20 ações com maior participação
-- Lista as ações com maior peso no índice IBOV

SELECT 
    codigo,
    acao,
    setor,
    part_percent,
    theoretical_qty,
    RANK() OVER (ORDER BY part_percent DESC) as ranking
FROM bovespa_curated
WHERE part_percent > 0
ORDER BY part_percent DESC
LIMIT 20;
