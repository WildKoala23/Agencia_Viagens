DROP FUNCTION IF EXISTS comprasUtilizador;

CREATE OR REPLACE FUNCTION comprasUtilizador (idUser INT)
RETURNS TABLE (
	id_compra INT,
	nomePacote TEXT,
	data_partida DATE,
	data_regresso DATE,
	status TEXT,
	total NUMERIC(10,2),
	data_compra DATE
) AS $$
BEGIN
	RETURN QUERY
	SELECT C.compra_id, P.nome, P.data_inicio, P.data_fim, C.estado, P.preco_total, C.data_compra 
	FROM public.compra C JOIN public.pacote P
		ON C.pacote_id = P.pacote_id
	WHERE C.user_id = idUser;
END;
$$ LANGUAGE plpgsql;


DROP FUNCTION IF EXISTS criar_fatura_completa;

CREATE OR REPLACE FUNCTION criar_fatura_completa(
    p_compra_id INT,
    p_pagamento_id INT DEFAULT NULL
)
RETURNS INT AS $$
DECLARE
    v_fatura_id INT;
    v_valor_total DECIMAL(10,2);
    v_pacote_id INT;
    v_pacote_nome TEXT;
BEGIN
    -- Buscar informações da compra e do pacote
    SELECT c.pacote_id, c.valor_total, p.nome
    INTO v_pacote_id, v_valor_total, v_pacote_nome
    FROM compra c
    JOIN pacote p ON c.pacote_id = p.pacote_id
    WHERE c.compra_id = p_compra_id;
    
    -- Verificar se a compra existe
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Compra % não encontrada', p_compra_id;
    END IF;
    
    -- Criar a fatura
    INSERT INTO fatura (compra_id, pagamento_id, data_emissao, valor_total)
    VALUES (p_compra_id, p_pagamento_id, CURRENT_TIMESTAMP, v_valor_total)
    RETURNING fatura_id INTO v_fatura_id;
    
    -- Criar linha da fatura
    INSERT INTO fatura_linha (fatura_id, pacote_id, descricao_item, preco, subtotal)
    VALUES (v_fatura_id, v_pacote_id, v_pacote_nome, v_valor_total, v_valor_total);
    
    -- Retornar o ID da fatura criada
    RETURN v_fatura_id;
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Erro ao criar fatura: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- FUNCTION: Obter Estatísticas de Faturamento
-- =====================================================
-- Retorna estatísticas gerais de faturamento
DROP FUNCTION IF EXISTS estatisticas_faturamento;

CREATE OR REPLACE FUNCTION estatisticas_faturamento()
RETURNS TABLE (
    total_faturas BIGINT,
    valor_total DECIMAL(10,2),
    faturas_pagas BIGINT,
    valor_pago DECIMAL(10,2),
    faturas_pendentes BIGINT,
    valor_pendente DECIMAL(10,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::BIGINT as total_faturas,
        COALESCE(SUM(f.valor_total), 0)::DECIMAL(10,2) as valor_total,
        COUNT(CASE WHEN p.estado = 'pago' THEN 1 END)::BIGINT as faturas_pagas,
        COALESCE(SUM(CASE WHEN p.estado = 'pago' THEN f.valor_total END), 0)::DECIMAL(10,2) as valor_pago,
        COUNT(CASE WHEN p.estado = 'pendente' OR p.estado IS NULL THEN 1 END)::BIGINT as faturas_pendentes,
        COALESCE(SUM(CASE WHEN p.estado = 'pendente' OR p.estado IS NULL THEN f.valor_total END), 0)::DECIMAL(10,2) as valor_pendente
    FROM fatura f
    LEFT JOIN pagamento p ON f.pagamento_id = p.pagamento_id;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- FUNCTION: Top Clientes por Faturamento
-- =====================================================
-- Retorna os clientes com maior valor total em faturas
DROP FUNCTION IF EXISTS top_clientes_faturamento;

CREATE OR REPLACE FUNCTION top_clientes_faturamento(
    p_limite INT DEFAULT 10
)
RETURNS TABLE (
    user_id INT,
    nome_cliente TEXT,
    email TEXT,
    total_faturas BIGINT,
    valor_total DECIMAL(10,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        u.user_id,
        u.nome as nome_cliente,
        u.email,
        COUNT(f.fatura_id)::BIGINT as total_faturas,
        COALESCE(SUM(f.valor_total), 0)::DECIMAL(10,2) as valor_total
    FROM utilizador u
    JOIN compra c ON u.user_id = c.user_id
    JOIN fatura f ON c.compra_id = f.compra_id
    GROUP BY u.user_id, u.nome, u.email
    ORDER BY valor_total DESC
    LIMIT p_limite;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- TRIGGER FUNCTION: Atualizar valor total da fatura
-- =====================================================
-- Recalcula automaticamente o valor total da fatura
-- quando uma linha é inserida, atualizada ou removida
DROP FUNCTION IF EXISTS atualizar_valor_fatura CASCADE;

CREATE OR REPLACE FUNCTION atualizar_valor_fatura()
RETURNS TRIGGER AS $$
DECLARE
    v_novo_total DECIMAL(10,2);
BEGIN
    -- Calcular o novo total
    SELECT COALESCE(SUM(subtotal), 0)
    INTO v_novo_total
    FROM fatura_linha
    WHERE fatura_id = COALESCE(NEW.fatura_id, OLD.fatura_id);
    
    -- Atualizar a fatura
    UPDATE fatura
    SET valor_total = v_novo_total
    WHERE fatura_id = COALESCE(NEW.fatura_id, OLD.fatura_id);
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Criar triggers para INSERT, UPDATE e DELETE
DROP TRIGGER IF EXISTS trigger_atualizar_valor_fatura_insert ON fatura_linha;
DROP TRIGGER IF EXISTS trigger_atualizar_valor_fatura_update ON fatura_linha;
DROP TRIGGER IF EXISTS trigger_atualizar_valor_fatura_delete ON fatura_linha;

CREATE TRIGGER trigger_atualizar_valor_fatura_insert
    AFTER INSERT ON fatura_linha
    FOR EACH ROW
    EXECUTE FUNCTION atualizar_valor_fatura();

CREATE TRIGGER trigger_atualizar_valor_fatura_update
    AFTER UPDATE ON fatura_linha
    FOR EACH ROW
    EXECUTE FUNCTION atualizar_valor_fatura();

CREATE TRIGGER trigger_atualizar_valor_fatura_delete
    AFTER DELETE ON fatura_linha
    FOR EACH ROW
    EXECUTE FUNCTION atualizar_valor_fatura();
