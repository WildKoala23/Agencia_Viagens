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
