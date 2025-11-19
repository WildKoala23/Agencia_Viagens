DO $$
BEGIN
    EXECUTE 'DROP MATERIALIZED VIEW IF EXISTS mv_destinos';
    EXECUTE '
                CREATE MATERIALIZED VIEW mv_destinos
                AS 
                SELECT * FROM destino d
            ';
END $$;

-- Função para executar o refresh da materialized view
CREATE OR REPLACE FUNCTION refresh_mv_destinos()
RETURNS TRIGGER AS $$
BEGIN
    REFRESH MATERIALIZED VIEW mv_destinos;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Trigger para atualizar views sempre que há alteração em base de dados
CREATE OR REPLACE TRIGGER trigger_insertDestinos
AFTER INSERT OR UPDATE OR DELETE ON destino
FOR EACH STATEMENT
EXECUTE FUNCTION refresh_mv_destinos();

-- Cria função que converte materialized view para json 
CREATE OR REPLACE FUNCTION destinosToJson()
RETURNS json AS $$
    SELECT json_agg(row_to_json(d))
    FROM mv_destinos d;
$$ LANGUAGE sql;