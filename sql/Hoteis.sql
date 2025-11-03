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

