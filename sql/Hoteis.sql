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

