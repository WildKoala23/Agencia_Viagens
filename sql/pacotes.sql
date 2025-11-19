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