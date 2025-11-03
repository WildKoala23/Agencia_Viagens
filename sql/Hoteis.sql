----VIEWS----
--hotéis associados a pacotes

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

--SELECT * FROM vw_pacote_hoteis WHERE nome_pacote ILIKE '%Lisboa%';

---------------------------------------------------------------------------------------------------------------------------------

----FUNCTIONS----

-- Calcular custo total dos hotéis de um pacote
CREATE OR REPLACE FUNCTION fn_custo_hoteis_pacote(p_pacote_id INT)
RETURNS DECIMAL(10,2) AS $$
DECLARE
    total DECIMAL(10,2);
BEGIN
    SELECT COALESCE(SUM(h.preco_diario), 0)
    INTO total
    FROM pacote_hotel ph
    JOIN hotel h ON ph.hotel_id = h.hotel_id
    WHERE ph.pacote_id = p_pacote_id;
    
    RETURN total;
END;
$$ LANGUAGE plpgsql;

-- Calcular o preço médio diário de hotéis de um pacote
CREATE OR REPLACE FUNCTION fn_preco_medio_diario(p_pacote_id INT)
RETURNS DECIMAL(10,2) AS $$
DECLARE
    media DECIMAL(10,2);
BEGIN
    SELECT COALESCE(AVG(h.preco_diario), 0)
    INTO media
    FROM pacote_hotel ph
    JOIN hotel h ON ph.hotel_id = h.hotel_id
    WHERE ph.pacote_id = p_pacote_id;
    
    RETURN media;
END;
$$ LANGUAGE plpgsql;

-- Verificar a disponibilidade de um hotel em um período específico
CREATE OR REPLACE FUNCTION fn_verificar_disponibilidade_hotel(p_hotel_id INT, p_data_inicio DATE, p_data_fim DATE)
RETURNS BOOLEAN AS $$
DECLARE
    reserva_count INT;
BEGIN
    SELECT COUNT(*)
    INTO reserva_count
    FROM reserva r
    JOIN pacote_hotel ph ON r.pacote_id = ph.pacote_id
    WHERE ph.hotel_id = p_hotel_id
    AND ((r.data_inicio BETWEEN p_data_inicio AND p_data_fim)
    OR (r.data_fim BETWEEN p_data_inicio AND p_data_fim));

    IF reserva_count > 0 THEN
        RETURN FALSE;  -- Hotel não disponível
    ELSE
        RETURN TRUE;   -- Hotel disponível
    END IF;
END;
$$ LANGUAGE plpgsql;

------------------------------------------------------------------------------------------------------------------------------------

----TRIGGERS----

-- Atualiza automaticamente o preço total do pacote ao adicionar/remover hotéis
CREATE OR REPLACE FUNCTION trg_atualiza_preco_pacote()
RETURNS TRIGGER AS $$
DECLARE
    novo_total DECIMAL(10,2);
BEGIN
    SELECT COALESCE(SUM(h.preco_diario), 0)
    INTO novo_total
    FROM pacote_hotel ph
    JOIN hotel h ON ph.hotel_id = h.hotel_id
    WHERE ph.pacote_id = COALESCE(NEW.pacote_id, OLD.pacote_id);
    
    UPDATE pacote
    SET preco_total = novo_total
    WHERE pacote_id = COALESCE(NEW.pacote_id, OLD.pacote_id);
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tg_atualiza_preco_pacote
AFTER INSERT OR DELETE OR UPDATE ON pacote_hotel
FOR EACH ROW
EXECUTE FUNCTION trg_atualiza_preco_pacote();

-- Verifica disponibilidade de um hotel ao adicionar uma nova reserva
CREATE OR REPLACE FUNCTION trg_verificar_disponibilidade_reserva()
RETURNS TRIGGER AS $$
BEGIN
    IF NOT fn_verificar_disponibilidade_hotel(NEW.hotel_id, NEW.data_inicio, NEW.data_fim) THEN
        RAISE EXCEPTION 'Hotel não disponível nas datas selecionadas.';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tg_verificar_disponibilidade_reserva
BEFORE INSERT ON reserva
FOR EACH ROW
EXECUTE FUNCTION trg_verificar_disponibilidade_reserva();

------------------------------------------------------------------------------------------------------------------------------------

----PROCEDURES----

-- Adicionar hotel a um pacote
CREATE OR REPLACE PROCEDURE sp_adicionar_hotel_ao_pacote(p_pacote_id INT, p_hotel_id INT)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Verifica se já existe
    IF EXISTS (
        SELECT 1 FROM pacote_hotel 
        WHERE pacote_id = p_pacote_id AND hotel_id = p_hotel_id
    ) THEN
        RAISE NOTICE 'Hotel já está associado a este pacote.';
        RETURN;
    END IF;

    INSERT INTO pacote_hotel (pacote_id, hotel_id)
    VALUES (p_pacote_id, p_hotel_id);

    -- Atualiza o preço total via trigger
    RAISE NOTICE 'Hotel adicionado com sucesso ao pacote %', p_pacote_id;
END;
$$;

-- Remover hotel de um pacote
CREATE OR REPLACE PROCEDURE sp_remover_hotel_do_pacote(p_pacote_id INT, p_hotel_id INT)
LANGUAGE plpgsql
AS $$ 
BEGIN
    DELETE FROM pacote_hotel
    WHERE pacote_id = p_pacote_id AND hotel_id = p_hotel_id;

    RAISE NOTICE 'Hotel removido do pacote %', p_pacote_id;
END;
$$;

-- Alterar preço diário de um hotel
CREATE OR REPLACE PROCEDURE sp_alterar_preco_diario_hotel(p_hotel_id INT, p_novo_preco DECIMAL(10,2))
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE hotel
    SET preco_diario = p_novo_preco
    WHERE hotel_id = p_hotel_id;

    RAISE NOTICE 'Preço diário do hotel % alterado para %', p_hotel_id, p_novo_preco;
END;
$$;

-- Atualizar a descrição do hotel
CREATE OR REPLACE PROCEDURE sp_atualizar_descricao_hotel(p_hotel_id INT, p_nova_descricao TEXT)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE hotel
    SET descricao_item = p_nova_descricao
    WHERE hotel_id = p_hotel_id;

    RAISE NOTICE 'Descrição do hotel % atualizada.', p_hotel_id;
END;
$$;

-- Alterar datas de um pacote
CREATE OR REPLACE PROCEDURE sp_alterar_datas_pacote(p_pacote_id INT, p_nova_data_inicio DATE, p_nova_data_fim DATE)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE pacote
    SET data_inicio = p_nova_data_inicio, data_fim = p_nova_data_fim
    WHERE pacote_id = p_pacote_id;

    -- Atualiza o preço total do pacote
    RAISE NOTICE 'Datas do pacote % alteradas para % até %', p_pacote_id, p_nova_data_inicio, p_nova_data_fim;
END;
$$;