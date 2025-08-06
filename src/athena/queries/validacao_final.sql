-- ✅ Queries de Validação Final - Athena
-- Execute estas queries para validar o pipeline completo

-- 1. Verificar total de registros
SELECT 
    COUNT(*) as total_registros,
    COUNT(DISTINCT codigo) as acoes_unicas,
    COUNT(DISTINCT setor) as setores_unicos
FROM bovespa_dados;

-- 2. Verificar distribuição por arquivo fonte
SELECT 
    source_file,
    COUNT(*) as quantidade,
    COUNT(DISTINCT codigo) as acoes_unicas
FROM bovespa_dados 
GROUP BY source_file
ORDER BY quantidade DESC;

-- 3. Top 10 ações por participação (convertendo string para decimal)
SELECT 
    codigo,
    acao,
    setor,
    ROUND(AVG(CAST(REPLACE(part_percent, ',', '.') AS DOUBLE)), 4) as participacao_media,
    COUNT(*) as aparicoes
FROM bovespa_dados 
WHERE part_percent IS NOT NULL
GROUP BY codigo, acao, setor
ORDER BY participacao_media DESC
LIMIT 10;

-- 4. Distribuição por setor
SELECT 
    setor,
    COUNT(*) as quantidade_acoes,
    ROUND(SUM(CAST(REPLACE(part_percent, ',', '.') AS DOUBLE)), 2) as participacao_total
FROM bovespa_dados 
WHERE setor != '' AND part_percent IS NOT NULL
GROUP BY setor
ORDER BY participacao_total DESC;

-- 5. Validar estrutura de partições (ano/mês/dia)
SELECT 
    ano,
    mes,
    dia,
    COUNT(*) as registros
FROM bovespa_dados 
GROUP BY ano, mes, dia
ORDER BY ano, mes, dia;
