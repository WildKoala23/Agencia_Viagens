DO $$
BEGIN
    EXECUTE 'DROP MATERIALIZED VIEW IF EXISTS mv_destinos';
    EXECUTE '
                CREATE MATERIALIZED VIEW mv_destinos
                AS 
                SELECT json_agg(row_to_json(d)) FROM destino d
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
CREATE OR REPLACE TRIGGER insertDestino
AFTER INSERT OR UPDATE OR DELETE ON destino
FOR EACH STATEMENT
EXECUTE FUNCTION refresh_mv_destinos();