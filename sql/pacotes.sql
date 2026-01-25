-- Insere dados pré definidos para a tabela de pacotes estados
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pacote_estado) THEN
        INSERT INTO pacote_estado VALUES
            (1, 'Ativo'), 
            (2, 'Esgotado'), 
            (3, 'Cancelado');
    END IF;
END $$;

-- Cria uma view na cache de todos os pacotes
DO $$
BEGIN
    EXECUTE 'DROP MATERIALIZED VIEW IF EXISTS mv_pacotes';
    EXECUTE 'CREATE MATERIALIZED VIEW mv_pacotes AS
             SELECT * FROM pacote';
END $$;

-- Cria função que converte materialized view para json 
CREATE OR REPLACE FUNCTION pacotesToJson()
RETURNS json AS $$
    SELECT json_agg(row_to_json(p))
    FROM mv_pacotes p;
$$ LANGUAGE sql;

-- Função para executar o refresh da materialized view
CREATE OR REPLACE FUNCTION refresh_mv_pacotes()
RETURNS TRIGGER AS $$
BEGIN
    REFRESH MATERIALIZED VIEW mv_pacotes;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Trigger para atualizar views sempre que há alteração em base de dados
CREATE OR REPLACE TRIGGER trigger_insertPacotes
AFTER INSERT OR UPDATE OR DELETE ON pacote
FOR EACH STATEMENT
EXECUTE FUNCTION refresh_mv_pacotes();

--  materialized view - destinos agregados (jsonb)
DO $$
BEGIN
    EXECUTE 'DROP MATERIALIZED VIEW IF EXISTS mv_pacotes_full';
    EXECUTE '
    CREATE MATERIALIZED VIEW mv_pacotes_full AS
    SELECT p.pacote_id,
           p.nome,
           p.descricao_item,
           p.preco_total,
           p.data_inicio,
           p.data_fim,
           p.imagem,
           p.estado_id,
           COALESCE(jsonb_agg(jsonb_build_object(
               ''destino_id'', d.destino_id,
               ''nome'', d.nome,
               ''pais'', d.pais
           )) FILTER (WHERE d.destino_id IS NOT NULL), ''[]'') AS destinos
    FROM pacote p
    LEFT JOIN pacote_destino pd ON pd.pacote_id = p.pacote_id
    LEFT JOIN destino d ON d.destino_id = pd.destino_id
    GROUP BY p.pacote_id, p.nome, p.descricao_item, p.preco_total, p.data_inicio, p.data_fim, p.estado_id;
    ';
END $$;

-- Função que converte a materialized view completa para JSON
CREATE OR REPLACE FUNCTION pacotesFullToJson()
RETURNS json AS $$
    SELECT json_agg(row_to_json(p))
    FROM mv_pacotes_full p;
$$ LANGUAGE sql;

-- Índices para melhorar as pesquisas na materialized view
-- Índice btree para filtragem por preço e data
DO $$
BEGIN
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_mv_pacotes_full_preco ON mv_pacotes_full (preco_total)';
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_mv_pacotes_full_data ON mv_pacotes_full (data_inicio)';
    -- Índice GIN para full-text sobre nome+descricao (Português)
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_mv_pacotes_full_ft ON mv_pacotes_full USING GIN (to_tsvector(''portuguese'', coalesce(nome,'''') || '' '' || coalesce(descricao_item, '''')) )';
    -- Índice GIN para pesquisar dentro do JSONB de destinos
    EXECUTE 'CREATE INDEX IF NOT EXISTS idx_mv_pacotes_full_destinos_gin ON mv_pacotes_full USING GIN (destinos)';
END $$;

-- Trigger para atualizar mv_pacotes_full quando pacote, pacote_destino ou destino mudarem
CREATE OR REPLACE FUNCTION refresh_mv_pacotes_full()
RETURNS TRIGGER AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_pacotes_full;
    RETURN NULL;
EXCEPTION WHEN others THEN
    -- Se não for possível refresh concurrently (por ex. falta de índice), tenta sem concurrently
    REFRESH MATERIALIZED VIEW mv_pacotes_full;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_pacotes_full_pk ON mv_pacotes_full (pacote_id);
-- Triggers para atualizar a mv_pacotes_full automaticamente
DROP TRIGGER IF EXISTS trigger_refresh_mv_pacotes_full_pacote ON pacote;
CREATE TRIGGER trigger_refresh_mv_pacotes_full_pacote
AFTER INSERT OR UPDATE OR DELETE ON pacote
FOR EACH STATEMENT
EXECUTE FUNCTION refresh_mv_pacotes_full();

DROP TRIGGER IF EXISTS trigger_refresh_mv_pacotes_full_pacote_destino ON pacote_destino;
CREATE TRIGGER trigger_refresh_mv_pacotes_full_pacote_destino
AFTER INSERT OR UPDATE OR DELETE ON pacote_destino
FOR EACH STATEMENT
EXECUTE FUNCTION refresh_mv_pacotes_full();

DROP TRIGGER IF EXISTS trigger_refresh_mv_pacotes_full_destino ON destino;
CREATE TRIGGER trigger_refresh_mv_pacotes_full_destino
AFTER INSERT OR UPDATE OR DELETE ON destino
FOR EACH STATEMENT
EXECUTE FUNCTION refresh_mv_pacotes_full();

-- FUNCTION: Calcular preço total da reserva (pacote + hotel + voo)
CREATE OR REPLACE FUNCTION calcular_preco_reserva(
    p_pacote_id INTEGER,
    p_hotel_id INTEGER,
    p_voo_id INTEGER
)
RETURNS TABLE (
    preco_base NUMERIC(10,2),
    num_noites INTEGER,
    preco_hotel_diario NUMERIC(10,2),
    preco_hotel_total NUMERIC(10,2),
    preco_voo NUMERIC(10,2),
    preco_total NUMERIC(10,2)
) AS $$
DECLARE
    v_data_inicio DATE;
    v_data_fim DATE;
    v_preco_base NUMERIC(10,2);
    v_preco_hotel_diario NUMERIC(10,2);
    v_preco_voo NUMERIC(10,2);
    v_num_noites INTEGER;
BEGIN
    -- Buscar dados do pacote
    SELECT p.data_inicio, p.data_fim, p.preco_total
    INTO v_data_inicio, v_data_fim, v_preco_base
    FROM pacote p
    WHERE p.pacote_id = p_pacote_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Pacote % não encontrado', p_pacote_id;
    END IF;
    
    -- Buscar preço do hotel
    SELECT h.preco_diario
    INTO v_preco_hotel_diario
    FROM hotel h
    WHERE h.hotel_id = p_hotel_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Hotel % não encontrado', p_hotel_id;
    END IF;
    
    -- Buscar preço do voo
    SELECT v.preco
    INTO v_preco_voo
    FROM voo v
    WHERE v.voo_id = p_voo_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Voo % não encontrado', p_voo_id;
    END IF;
    
    -- Calcular número de noites
    v_num_noites := v_data_fim - v_data_inicio;
    
    -- Retornar tudo calculado
    RETURN QUERY SELECT
        v_preco_base,
        v_num_noites,
        v_preco_hotel_diario,
        v_preco_hotel_diario * v_num_noites,
        v_preco_voo,
        v_preco_base + (v_preco_hotel_diario * v_num_noites) + v_preco_voo;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION calcular_preco_reserva(INTEGER, INTEGER, INTEGER) IS 
'Calcula o preço total de uma reserva incluindo pacote base, hotel (por noite) e voo';

-- TRIGGER: Validar datas e preços do pacote
CREATE OR REPLACE FUNCTION validar_datas_pacote()
RETURNS TRIGGER AS $$
BEGIN
    -- Validar que data_fim > data_inicio
    IF NEW.data_fim <= NEW.data_inicio THEN
        RAISE EXCEPTION 'A data de fim deve ser posterior à data de início';
    END IF;
    
    -- Validar que data_inicio não é no passado (para novos pacotes)
    IF TG_OP = 'INSERT' AND NEW.data_inicio < CURRENT_DATE THEN
        RAISE EXCEPTION 'A data de início não pode ser no passado';
    END IF;
    
    -- Validar preço positivo
    IF NEW.preco_total <= 0 THEN
        RAISE EXCEPTION 'O preço do pacote deve ser positivo';
    END IF;
    
    -- Validar nome não vazio
    IF NEW.nome IS NULL OR LENGTH(TRIM(NEW.nome)) = 0 THEN
        RAISE EXCEPTION 'O nome do pacote é obrigatório';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_validar_pacote ON pacote;
CREATE TRIGGER trigger_validar_pacote
BEFORE INSERT OR UPDATE ON pacote
FOR EACH ROW
EXECUTE FUNCTION validar_datas_pacote();

-- VIEW: Estatísticas de preços (pacotes, hotéis, voos)
 CREATE OR REPLACE VIEW vw_estatisticas_precos AS
    SELECT 
        'Pacotes' AS tipo,
        COUNT(*) AS total,
        MIN(preco_total) AS preco_minimo,
        MAX(preco_total) AS preco_maximo,
        ROUND(AVG(preco_total), 2) AS preco_medio,
        ROUND(CAST(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY preco_total) AS NUMERIC), 2) AS preco_mediano
    FROM pacote
    UNION ALL
    SELECT 
        'Hotéis (diária)' AS tipo,
        COUNT(*) AS total,
        MIN(preco_diario) AS preco_minimo,
        MAX(preco_diario) AS preco_maximo,
        ROUND(AVG(preco_diario), 2) AS preco_medio,
        ROUND(CAST(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY preco_diario) AS NUMERIC), 2) AS preco_mediano
    FROM hotel
    UNION ALL
    SELECT 
        'Voos' AS tipo,
        COUNT(*) AS total,
        MIN(preco) AS preco_minimo,
        MAX(preco) AS preco_maximo,
        ROUND(AVG(preco), 2) AS preco_medio,
        ROUND(CAST(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY preco) AS NUMERIC), 2) AS preco_mediano
    FROM voo;

COMMENT ON VIEW vw_estatisticas_precos IS 
'Estatísticas agregadas de preços de pacotes, hotéis e voos';

-- =====================================================
-- NOVA PROCEDURE: Obter Pacotes Disponíveis com Vagas
-- =====================================================


-- =====================================================
-- STORED PROCEDURE: Atualizar Pacotes Expirados
-- =====================================================
DROP PROCEDURE IF EXISTS atualizar_pacotes_expirados CASCADE;

CREATE OR REPLACE PROCEDURE atualizar_pacotes_expirados()
AS $$
DECLARE
    v_pacotes_atualizados INT;
BEGIN
    -- Atualizar pacotes que já passaram da data de início para 'Esgotado'
    UPDATE pacote
    SET estado_id = 2  -- 2 = 'Esgotado'
    WHERE estado_id = 1  -- 1 = 'Ativo'
      AND data_inicio < CURRENT_DATE;
    
    GET DIAGNOSTICS v_pacotes_atualizados = ROW_COUNT;
    
    -- Log da operação (opcional)
    RAISE NOTICE 'Pacotes atualizados para Esgotado: %', v_pacotes_atualizados;
END;
$$ LANGUAGE plpgsql;

COMMENT ON PROCEDURE atualizar_pacotes_expirados() IS 
'Atualiza pacotes que já passaram da data de início para estado Esgotado';

-- =====================================================
-- FUNÇÃO: Retorna apenas pacotes ativos e futuros
-- =====================================================
DROP FUNCTION IF EXISTS get_pacotes_visiveis CASCADE;

CREATE OR REPLACE FUNCTION get_pacotes_visiveis(
    p_limite INT DEFAULT 100
)
RETURNS TABLE (
    pacote_id INT,
    nome TEXT,
    descricao_item TEXT,
    data_inicio DATE,
    data_fim DATE,
    preco_total DECIMAL(10,2),
    imagem TEXT,
    destinos TEXT,
    vagas_disponiveis INT,
    vagas_totais INT,
    avaliacao_media DECIMAL(3,2),
    total_avaliacoes BIGINT,
    estado TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.pacote_id,
        p.nome::TEXT,
        p.descricao_item::TEXT,
        p.data_inicio,
        p.data_fim,
        p.preco_total,
        p.imagem::TEXT,
        
        -- Agregação de destinos
        COALESCE(
            (SELECT STRING_AGG(d.nome || ', ' || d.pais, ' | ')
             FROM pacote_destino pd
             JOIN destino d ON pd.destino_id = d.destino_id
             WHERE pd.pacote_id = p.pacote_id),
            'N/A'
        )::TEXT AS destinos,
        
        -- Vagas disponíveis
        (p.limite_vagas - COALESCE(
            (SELECT COUNT(*)::INT
             FROM compra c
             WHERE c.pacote_id = p.pacote_id 
             AND c.estado != 'cancelada'),
            0
        ))::INT AS vagas_disponiveis,
        
        p.limite_vagas::INT AS vagas_totais,
        
        -- Avaliação média
        COALESCE(
            (SELECT AVG(f.avaliacao)::DECIMAL(3,2)
             FROM feedback f
             WHERE f.pacote_id = p.pacote_id),
            0::DECIMAL(3,2)
        ) AS avaliacao_media,
        
        -- Total de avaliações
        COALESCE(
            (SELECT COUNT(*)::BIGINT
             FROM feedback f
             WHERE f.pacote_id = p.pacote_id),
            0::BIGINT
        ) AS total_avaliacoes,
        
        pe.desc::TEXT AS estado
        
    FROM pacote p
    JOIN pacote_estado pe ON p.estado_id = pe.estado_id
    
    WHERE pe.desc = 'Ativo'  -- Apenas pacotes ativos
      AND p.data_inicio >= CURRENT_DATE  -- Apenas pacotes futuros
    
    ORDER BY p.data_inicio ASC, p.preco_total ASC
    LIMIT p_limite;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_pacotes_visiveis(INT) IS 
'Retorna apenas pacotes Ativos com data futura (invisível para Esgotados/Cancelados)';
