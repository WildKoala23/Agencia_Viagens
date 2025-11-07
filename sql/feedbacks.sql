-- =====================================================
-- VIEWS E FUNCTIONS PARA FEEDBACKS
-- Desenvolvido por: Rafael (dev--Rafael)
-- =====================================================

-- =====================================================
-- VIEW: Lista completa de feedbacks com informações relacionadas
-- =====================================================
DROP VIEW IF EXISTS view_feedbacks_completos;

CREATE VIEW view_feedbacks_completos AS
SELECT 
    f.feedback_id,
    f.pacote_id,
    f.avaliacao,
    f.comentario,
    f.data_feedback,
    p.nome as nome_pacote,
    p.descricao_item as descricao_pacote,
    p.preco_total,
    d.nome as destino_nome
FROM feedback f
JOIN pacote p ON f.pacote_id = p.pacote_id
LEFT JOIN pacote_destino pd ON p.pacote_id = pd.pacote_id
LEFT JOIN destino d ON pd.destino_id = d.destino_id
ORDER BY f.data_feedback DESC;

-- =====================================================
-- FUNCTION: Obter detalhes de um feedback específico
-- =====================================================
DROP FUNCTION IF EXISTS get_feedback_detalhes;

CREATE OR REPLACE FUNCTION get_feedback_detalhes(p_feedback_id INT)
RETURNS TABLE (
    feedback_id INT,
    pacote_id INT,
    avaliacao INT,
    comentario TEXT,
    data_feedback DATE,
    nome_pacote TEXT,
    descricao_pacote TEXT,
    preco_total DECIMAL(10,2),
    destino_nome TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        f.feedback_id,
        f.pacote_id,
        f.avaliacao,
        f.comentario,
        f.data_feedback,
        p.nome as nome_pacote,
        p.descricao_item as descricao_pacote,
        p.preco_total,
        d.nome as destino_nome
    FROM feedback f
    JOIN pacote p ON f.pacote_id = p.pacote_id
    LEFT JOIN pacote_destino pd ON p.pacote_id = pd.pacote_id
    LEFT JOIN destino d ON pd.destino_id = d.destino_id
    WHERE f.feedback_id = p_feedback_id;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- FUNCTION: Média de avaliação por pacote
-- =====================================================
DROP FUNCTION IF EXISTS get_media_avaliacao_pacote;

CREATE OR REPLACE FUNCTION get_media_avaliacao_pacote(p_pacote_id INT)
RETURNS TABLE (
    pacote_id INT,
    nome_pacote TEXT,
    total_feedbacks BIGINT,
    media_avaliacao DECIMAL(3,2),
    avaliacao_5_estrelas BIGINT,
    avaliacao_4_estrelas BIGINT,
    avaliacao_3_estrelas BIGINT,
    avaliacao_2_estrelas BIGINT,
    avaliacao_1_estrela BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.pacote_id,
        p.nome as nome_pacote,
        COUNT(f.feedback_id)::BIGINT as total_feedbacks,
        COALESCE(AVG(f.avaliacao), 0)::DECIMAL(3,2) as media_avaliacao,
        COUNT(CASE WHEN f.avaliacao = 5 THEN 1 END)::BIGINT as avaliacao_5_estrelas,
        COUNT(CASE WHEN f.avaliacao = 4 THEN 1 END)::BIGINT as avaliacao_4_estrelas,
        COUNT(CASE WHEN f.avaliacao = 3 THEN 1 END)::BIGINT as avaliacao_3_estrelas,
        COUNT(CASE WHEN f.avaliacao = 2 THEN 1 END)::BIGINT as avaliacao_2_estrelas,
        COUNT(CASE WHEN f.avaliacao = 1 THEN 1 END)::BIGINT as avaliacao_1_estrela
    FROM pacote p
    LEFT JOIN feedback f ON p.pacote_id = f.pacote_id
    WHERE p.pacote_id = p_pacote_id
    GROUP BY p.pacote_id, p.nome;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- VIEW: Estatísticas de todos os pacotes
-- =====================================================
DROP VIEW IF EXISTS view_estatisticas_pacotes;

CREATE VIEW view_estatisticas_pacotes AS
SELECT 
    p.pacote_id,
    p.nome as nome_pacote,
    COUNT(f.feedback_id) as total_feedbacks,
    COALESCE(AVG(f.avaliacao), 0)::DECIMAL(3,2) as media_avaliacao,
    COUNT(CASE WHEN f.avaliacao = 5 THEN 1 END) as avaliacao_5_estrelas,
    COUNT(CASE WHEN f.avaliacao = 4 THEN 1 END) as avaliacao_4_estrelas,
    COUNT(CASE WHEN f.avaliacao = 3 THEN 1 END) as avaliacao_3_estrelas,
    COUNT(CASE WHEN f.avaliacao = 2 THEN 1 END) as avaliacao_2_estrelas,
    COUNT(CASE WHEN f.avaliacao = 1 THEN 1 END) as avaliacao_1_estrela
FROM pacote p
LEFT JOIN feedback f ON p.pacote_id = f.pacote_id
GROUP BY p.pacote_id, p.nome
ORDER BY media_avaliacao DESC, total_feedbacks DESC;

-- =====================================================
-- FUNCTION: Feedbacks por avaliação
-- =====================================================
DROP FUNCTION IF EXISTS get_feedbacks_por_avaliacao;

CREATE OR REPLACE FUNCTION get_feedbacks_por_avaliacao(p_avaliacao INT)
RETURNS TABLE (
    feedback_id INT,
    pacote_id INT,
    avaliacao INT,
    comentario TEXT,
    data_feedback DATE,
    nome_pacote TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        f.feedback_id,
        f.pacote_id,
        f.avaliacao,
        f.comentario,
        f.data_feedback,
        p.nome as nome_pacote
    FROM feedback f
    JOIN pacote p ON f.pacote_id = p.pacote_id
    WHERE f.avaliacao = p_avaliacao
    ORDER BY f.data_feedback DESC;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- FUNCTION: Top pacotes mais bem avaliados
-- =====================================================
DROP FUNCTION IF EXISTS get_top_pacotes_avaliados;

CREATE OR REPLACE FUNCTION get_top_pacotes_avaliados(p_limite INT DEFAULT 10)
RETURNS TABLE (
    pacote_id INT,
    nome_pacote TEXT,
    total_feedbacks BIGINT,
    media_avaliacao DECIMAL(3,2),
    preco_total DECIMAL(10,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.pacote_id,
        p.nome as nome_pacote,
        COUNT(f.feedback_id)::BIGINT as total_feedbacks,
        COALESCE(AVG(f.avaliacao), 0)::DECIMAL(3,2) as media_avaliacao,
        p.preco_total
    FROM pacote p
    LEFT JOIN feedback f ON p.pacote_id = f.pacote_id
    GROUP BY p.pacote_id, p.nome, p.preco_total
    HAVING COUNT(f.feedback_id) > 0
    ORDER BY media_avaliacao DESC, total_feedbacks DESC
    LIMIT p_limite;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- FUNCTION: Estatísticas gerais de feedbacks
-- =====================================================
DROP FUNCTION IF EXISTS get_estatisticas_feedbacks;

CREATE OR REPLACE FUNCTION get_estatisticas_feedbacks()
RETURNS TABLE (
    total_feedbacks BIGINT,
    media_geral DECIMAL(3,2),
    total_5_estrelas BIGINT,
    total_4_estrelas BIGINT,
    total_3_estrelas BIGINT,
    total_2_estrelas BIGINT,
    total_1_estrela BIGINT,
    percentual_positivo DECIMAL(5,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::BIGINT as total_feedbacks,
        COALESCE(AVG(avaliacao), 0)::DECIMAL(3,2) as media_geral,
        COUNT(CASE WHEN avaliacao = 5 THEN 1 END)::BIGINT as total_5_estrelas,
        COUNT(CASE WHEN avaliacao = 4 THEN 1 END)::BIGINT as total_4_estrelas,
        COUNT(CASE WHEN avaliacao = 3 THEN 1 END)::BIGINT as total_3_estrelas,
        COUNT(CASE WHEN avaliacao = 2 THEN 1 END)::BIGINT as total_2_estrelas,
        COUNT(CASE WHEN avaliacao = 1 THEN 1 END)::BIGINT as total_1_estrela,
        CASE 
            WHEN COUNT(*) > 0 THEN 
                (COUNT(CASE WHEN avaliacao >= 4 THEN 1 END)::DECIMAL / COUNT(*)::DECIMAL * 100)
            ELSE 0 
        END::DECIMAL(5,2) as percentual_positivo
    FROM feedback;
END;
$$ LANGUAGE plpgsql;

-- Stored Procedure para inserir feedback de utilizador

DROP FUNCTION IF EXISTS inserir_feedback_user;

CREATE OR REPLACE FUNCTION inserir_feedback_user(
    p_reserva_id INT,
    p_avaliacao INT,
    p_comentario TEXT
)
RETURNS INT AS $$
DECLARE
    v_feedback_id INT;
    v_pacote_id INT;
    v_user_id INT;
BEGIN
    -- Buscar informações da reserva/compra
    SELECT pacote_id, user_id
    INTO v_pacote_id, v_user_id
    FROM compra
    WHERE compra_id = p_reserva_id;
    
    -- Verificar se a compra existe
    IF v_pacote_id IS NULL THEN
        RAISE EXCEPTION 'Compra não encontrada';
    END IF;
    
    -- Inserir o feedback
    INSERT INTO feedback (pacote_id, user_id, avaliacao, comentario, data_feedback)
    VALUES (v_pacote_id, v_user_id, p_avaliacao, p_comentario, CURRENT_DATE)
    RETURNING feedback_id INTO v_feedback_id;
    
    RETURN v_feedback_id;
END;
$$ LANGUAGE plpgsql;


-- =====================================================
-- COMENTÁRIOS
-- =====================================================
COMMENT ON VIEW view_feedbacks_completos IS 'Lista completa de feedbacks com informações dos pacotes';
COMMENT ON FUNCTION get_feedback_detalhes IS 'Retorna os detalhes completos de um feedback específico';
COMMENT ON FUNCTION get_media_avaliacao_pacote IS 'Retorna média e distribuição de avaliações de um pacote';
COMMENT ON VIEW view_estatisticas_pacotes IS 'Estatísticas de avaliação para todos os pacotes';
COMMENT ON FUNCTION get_feedbacks_por_avaliacao IS 'Retorna feedbacks filtrados por número de estrelas';
COMMENT ON FUNCTION get_top_pacotes_avaliados IS 'Retorna os pacotes mais bem avaliados';
COMMENT ON FUNCTION get_estatisticas_feedbacks IS 'Retorna estatísticas gerais de todos os feedbacks';
