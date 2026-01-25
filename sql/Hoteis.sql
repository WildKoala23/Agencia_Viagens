-- VIEW: hotéis associados a pacotes
CREATE OR REPLACE VIEW vw_pacote_hoteis AS
SELECT 
    p.pacote_id,
    p.nome AS nome_pacote,
    h.hotel_id,
    h.nome AS nome_hotel,
    h.preco_diario,
    h.endereco,
    h.descricao_item AS descricao_hotel,
    p.data_inicio,
    p.data_fim,
    p.preco_total
FROM pacote_hotel ph
JOIN pacote p ON ph.pacote_id = p.pacote_id
JOIN hotel h ON ph.hotel_id = h.hotel_id;

--VIEW: Todos os hoteis
-- VIEW: todos os hotéis
CREATE OR REPLACE VIEW vw_hoteis AS
SELECT 
    h.hotel_id,
    h.nome AS nome_hotel,
    h.preco_diario,
    h.endereco,
    h.descricao_item AS descricao_hotel
FROM hotel h;

-- Cria uma view na cache de todos os hoteis
DO $$
BEGIN
    EXECUTE 'DROP MATERIALIZED VIEW IF EXISTS mv_hoteis';
    EXECUTE 'CREATE MATERIALIZED VIEW mv_hoteis AS
             SELECT * FROM hotel';
END $$;

-- Cria função que converte materialized view para json 
CREATE OR REPLACE FUNCTION hoteisToJson()
RETURNS json AS $$
    SELECT json_agg(row_to_json(h))
    FROM mv_hoteis h;
$$ LANGUAGE sql;

-- Função para executar o refresh da materialized view
CREATE OR REPLACE FUNCTION refresh_mv_hoteis()
RETURNS TRIGGER AS $$
BEGIN
    REFRESH MATERIALIZED VIEW mv_hoteis;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Trigger para atualizar views sempre que há alteração em base de dados
CREATE OR REPLACE TRIGGER trigger_insertHoteis
AFTER INSERT OR UPDATE OR DELETE ON hotel
FOR EACH STATEMENT
EXECUTE FUNCTION refresh_mv_hoteis();

-- Stored Procedure para eliminar hotel com validações
CREATE OR REPLACE PROCEDURE eliminar_hotel(p_hotel_id INTEGER)
LANGUAGE plpgsql AS $$
DECLARE
    v_pacote_exists BOOLEAN;
BEGIN
    -- Verificar se o hotel está associado a algum pacote
    SELECT EXISTS(
        SELECT 1 FROM pacote_hotel 
        WHERE hotel_id = p_hotel_id
    ) INTO v_pacote_exists;
    
    -- Se estiver associado a pacotes, lançar erro
    IF v_pacote_exists THEN
        RAISE EXCEPTION 'Não é possível eliminar este hotel porque está associado a pacotes existentes.';
    END IF;
    
    -- Eliminar o hotel
    DELETE FROM hotel WHERE hotel_id = p_hotel_id;
    
EXCEPTION
    WHEN foreign_key_violation THEN
        RAISE EXCEPTION 'Não é possível eliminar este hotel porque está a ser utilizado por outros registos.';
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Erro ao eliminar hotel: %', SQLERRM;
END;
$$;

-- Comentário do procedimento
COMMENT ON PROCEDURE eliminar_hotel(INTEGER) IS 
'Elimina um hotel se não estiver associado a nenhum pacote. Lança exceção caso contrário.';

-- VIEW: Hotéis disponíveis por pacote
CREATE OR REPLACE VIEW vw_hoteis_por_pacote AS
SELECT 
    p.pacote_id,
    p.nome AS pacote_nome,
    h.hotel_id,
    h.nome AS hotel_nome,
    h.preco_diario,
    h.endereco,
    h.descricao_item,
    d.destino_id,
    d.nome AS destino_nome,
    d.pais AS destino_pais
FROM pacote p
JOIN pacote_destino pd ON pd.pacote_id = p.pacote_id
JOIN destino d ON d.destino_id = pd.destino_id
JOIN hotel h ON h.destino_id = d.destino_id
ORDER BY p.pacote_id, h.nome;

COMMENT ON VIEW vw_hoteis_por_pacote IS 
'Lista todos os hotéis disponíveis para cada pacote, baseado nos destinos do pacote';

