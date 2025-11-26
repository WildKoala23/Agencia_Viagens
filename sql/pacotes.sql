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
           COALESCE(jsonb_agg(jsonb_build_object(
               ''destino_id'', d.destino_id,
               ''nome'', d.nome,
               ''pais'', d.pais
           )) FILTER (WHERE d.destino_id IS NOT NULL), ''[]'') AS destinos
    FROM pacote p
    LEFT JOIN pacote_destino pd ON pd.pacote_id = p.pacote_id
    LEFT JOIN destino d ON d.destino_id = pd.destino_id
    GROUP BY p.pacote_id, p.nome, p.descricao_item, p.preco_total, p.data_inicio, p.data_fim;
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


