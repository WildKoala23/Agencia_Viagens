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
