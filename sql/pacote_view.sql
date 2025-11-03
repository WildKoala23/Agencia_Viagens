CREATE OR REPLACE VIEW pacote_view AS
SELECT 
    pacote_id,
    nome,
    descricao_item,
    data_inicio,
    data_fim,
    preco_total,
    estado,
    imagem
FROM pacote
WHERE estado = 'Ativo';
