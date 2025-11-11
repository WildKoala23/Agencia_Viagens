DROP FUNCTION IF EXISTS comprasUtilizador;

-- Retorna todas as compras de um dado utilizador
CREATE OR REPLACE FUNCTION comprasUtilizador (idUser INT)
RETURNS TABLE (
    id_compra INT,
    nomePacote TEXT,
    destino TEXT,
    data_partida DATE,
    data_regresso DATE,
    status TEXT,
    total NUMERIC(10,2),
    data_compra DATE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        C.compra_id, 
        P.nome, 
        D.pais || ', ' || D.nome AS destino,
        P.data_inicio, 
        P.data_fim, 
        C.estado, 
        P.preco_total,
        C.data_compra
    FROM public.compra C 
    JOIN public.pacote P ON C.pacote_id = P.pacote_id 
    JOIN public.pacote_destino PD ON P.pacote_id = PD.pacote_id
    JOIN public.destino D ON PD.destino_id = D.destino_id
    WHERE C.user_id = idUser;
END;
$$ LANGUAGE plpgsql;

-- Verifica LogIn de utilizador
CREATE OR REPLACE FUNCTION userLogin(
    p_email VARCHAR(150),
    p_pass VARCHAR(50)
)
RETURNS INTEGER
AS $$
DECLARE
    v_user_id INTEGER;
BEGIN
    SELECT user_id INTO v_user_id
    FROM utilizador
    WHERE email = p_email AND password = p_pass;

    IF v_user_id IS NULL THEN
        RAISE EXCEPTION 'Email ou password errados';
    END IF;

    RETURN v_user_id;
END;
$$ LANGUAGE plpgsql;


