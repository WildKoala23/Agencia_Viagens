--Views

--View para visualizar todas as compras dado um utilizador
CREATE or REPLACE VIEW comprasUtilizador
AS
SELECT valor_total as Total, data_compra as [Data]
FROM compra
    JOIN utilizador