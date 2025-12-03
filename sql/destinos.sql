DO $$
BEGIN
    EXECUTE 'DROP MATERIALIZED VIEW IF EXISTS mv_destinos';
    EXECUTE '
                CREATE MATERIALIZED VIEW mv_destinos
                AS 
                SELECT * FROM destino d
            ';
END $$;

-- Função para executar o refresh da materialized view
CREATE OR REPLACE FUNCTION refresh_mv_destinos()
RETURNS TRIGGER AS $$
BEGIN
    REFRESH MATERIALIZED VIEW mv_destinos;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Trigger para atualizar views sempre que há alteração em base de dados
CREATE OR REPLACE TRIGGER trigger_insertDestinos
AFTER INSERT OR UPDATE OR DELETE ON destino
FOR EACH STATEMENT
EXECUTE FUNCTION refresh_mv_destinos();

-- FUNCTION: Verificar se um destino pode ser eliminado
CREATE OR REPLACE FUNCTION verificar_uso_destino(p_destino_id INTEGER)
RETURNS TABLE (
    pode_eliminar BOOLEAN,
    usado_em_pacotes INTEGER,
    usado_em_voos INTEGER,
    usado_em_hoteis INTEGER,
    mensagem_erro TEXT
) AS $$
DECLARE
    v_pacotes INTEGER;
    v_voos INTEGER;
    v_hoteis INTEGER;
    v_mensagens TEXT[] := ARRAY[]::TEXT[];
BEGIN
    -- Contar usos
    SELECT COUNT(*) INTO v_pacotes
    FROM pacote_destino WHERE destino_id = p_destino_id;
    
    SELECT COUNT(*) INTO v_voos
    FROM voo WHERE destino_id = p_destino_id;
    
    SELECT COUNT(*) INTO v_hoteis
    FROM hotel WHERE destino_id = p_destino_id;
    
    -- Construir array de mensagens
    IF v_pacotes > 0 THEN
        v_mensagens := array_append(v_mensagens, v_pacotes || ' pacote(s)');
    END IF;
    
    IF v_voos > 0 THEN
        v_mensagens := array_append(v_mensagens, v_voos || ' voo(s)');
    END IF;
    
    IF v_hoteis > 0 THEN
        v_mensagens := array_append(v_mensagens, v_hoteis || ' hotel/hotéis');
    END IF;
    
    -- Retornar resultado
    IF array_length(v_mensagens, 1) > 0 THEN
        RETURN QUERY SELECT 
            FALSE,
            v_pacotes,
            v_voos,
            v_hoteis,
            'Não é possível eliminar este destino porque está a ser utilizado em: ' || array_to_string(v_mensagens, ', ');
    ELSE
        RETURN QUERY SELECT TRUE, 0, 0, 0, 'Pode eliminar';
    END IF;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION verificar_uso_destino(INTEGER) IS 
'Verifica se um destino está a ser usado em pacotes, voos ou hotéis antes de eliminar';

-- FUNCTION: Eliminar destino com validação
CREATE OR REPLACE FUNCTION eliminar_destino(p_destino_id INTEGER)
RETURNS BOOLEAN AS $$
DECLARE
    v_resultado RECORD;
BEGIN
    -- Verificar uso
    SELECT * INTO v_resultado FROM verificar_uso_destino(p_destino_id);
    
    -- Se não pode eliminar, lançar erro
    IF NOT v_resultado.pode_eliminar THEN
        RAISE EXCEPTION '%', v_resultado.mensagem_erro;
    END IF;
    
    -- Eliminar o destino
    DELETE FROM destino WHERE destino_id = p_destino_id;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION eliminar_destino(INTEGER) IS 
'Elimina um destino se não estiver a ser usado. Lança exceção se estiver em uso.';

-- Cria função que converte materialized view para json 
CREATE OR REPLACE FUNCTION destinosToJson()
RETURNS json AS $$
    SELECT json_agg(row_to_json(d))
    FROM mv_destinos d;
$$ LANGUAGE sql;