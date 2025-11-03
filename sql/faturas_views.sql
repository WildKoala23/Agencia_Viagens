-- =====================================================
-- VIEWS E FUNCTIONS PARA FATURAS
-- Desenvolvido por: Rafael (dev--Rafael)
-- =====================================================

-- =====================================================
-- VIEW: Lista completa de faturas com informações relacionadas
-- =====================================================
DROP VIEW IF EXISTS view_faturas_completas;

CREATE VIEW view_faturas_completas AS
SELECT 
    f.fatura_id,
    f.compra_id,
    f.pagamento_id,
    f.data_emissao,
    f.valor_total,
    c.user_id,
    u.nome as nome_cliente,
    u.email as email_cliente,
    pg.metodo as tipo_pagamento,
    pg.estado as estado_pagamento,
    pg.data_pagamento,
    pg.valor as valor_pagamento
FROM fatura f
JOIN compra c ON f.compra_id = c.compra_id
JOIN utilizador u ON c.user_id = u.user_id
LEFT JOIN pagamento pg ON f.pagamento_id = pg.pagamento_id
ORDER BY f.data_emissao DESC;

-- =====================================================
-- FUNCTION: Obter detalhes de uma fatura específica
-- =====================================================
DROP FUNCTION IF EXISTS get_fatura_detalhes;

CREATE OR REPLACE FUNCTION get_fatura_detalhes(p_fatura_id INT)
RETURNS TABLE (
    fatura_id INT,
    compra_id INT,
    pagamento_id INT,
    data_emissao TIMESTAMP,
    valor_total DECIMAL(10,2),
    user_id INT,
    nome_cliente TEXT,
    email TEXT,
    tipo_pagamento TEXT,
    estado_pagamento TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        f.fatura_id,
        f.compra_id,
        f.pagamento_id,
        f.data_emissao,
        f.valor_total,
        c.user_id,
        u.nome as nome_cliente,
        u.email,
        pg.metodo as tipo_pagamento,
        pg.estado as estado_pagamento
    FROM fatura f
    JOIN compra c ON f.compra_id = c.compra_id
    JOIN utilizador u ON c.user_id = u.user_id
    LEFT JOIN pagamento pg ON f.pagamento_id = pg.pagamento_id
    WHERE f.fatura_id = p_fatura_id;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- FUNCTION: Obter linhas de uma fatura
-- =====================================================
DROP FUNCTION IF EXISTS get_fatura_linhas;

CREATE OR REPLACE FUNCTION get_fatura_linhas(p_fatura_id INT)
RETURNS TABLE (
    fatura_linha_id INT,
    pacote_id INT,
    descricao_item TEXT,
    preco DECIMAL(10,2),
    subtotal DECIMAL(10,2),
    nome_pacote TEXT,
    descricao_pacote TEXT,
    destino_nome TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        fl.fatura_linha_id,
        fl.pacote_id,
        fl.descricao_item,
        fl.preco,
        fl.subtotal,
        p.nome as nome_pacote,
        p.descricao_item as descricao_pacote,
        d.nome as destino_nome
    FROM fatura_linha fl
    JOIN pacote p ON fl.pacote_id = p.pacote_id
    LEFT JOIN pacote_destino pd ON p.pacote_id = pd.pacote_id
    LEFT JOIN destino d ON pd.destino_id = d.destino_id
    WHERE fl.fatura_id = p_fatura_id
    ORDER BY fl.fatura_linha_id;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- VIEW: Resumo de faturamento por cliente
-- =====================================================
DROP VIEW IF EXISTS view_faturamento_por_cliente;

CREATE VIEW view_faturamento_por_cliente AS
SELECT 
    u.user_id,
    u.nome as nome_cliente,
    u.email,
    COUNT(f.fatura_id) as total_faturas,
    COALESCE(SUM(f.valor_total), 0) as valor_total_faturas,
    COALESCE(AVG(f.valor_total), 0) as valor_medio_fatura
FROM utilizador u
LEFT JOIN compra c ON u.user_id = c.user_id
LEFT JOIN fatura f ON c.compra_id = f.compra_id
GROUP BY u.user_id, u.nome, u.email
ORDER BY valor_total_faturas DESC;

-- =====================================================
-- COMENTÁRIOS
-- =====================================================
COMMENT ON VIEW view_faturas_completas IS 'Lista completa de faturas com todas as informações relacionadas';
COMMENT ON FUNCTION get_fatura_detalhes IS 'Retorna os detalhes completos de uma fatura específica';
COMMENT ON FUNCTION get_fatura_linhas IS 'Retorna todas as linhas (itens) de uma fatura específica';
COMMENT ON VIEW view_faturamento_por_cliente IS 'Resumo do faturamento agrupado por cliente';
