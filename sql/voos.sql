CREATE OR REPLACE FUNCTION verificar_insercao_voo()
RETURNS TRIGGER AS $$
BEGIN

    IF NEW.destino_id IS NULL THEN
        RAISE EXCEPTION 'É obrigatório selecionar um destino.';
    END IF;

    IF NEW.companhia IS NULL OR LENGTH(TRIM(NEW.companhia)) = 0 THEN
        RAISE EXCEPTION 'O campo "companhia" não pode estar vazio.';
    END IF;

    IF NEW.numero_voo IS NULL THEN
        RAISE EXCEPTION 'O número do voo é obrigatório.';
    END IF;

    IF NEW.data_saida IS NULL THEN
        RAISE EXCEPTION 'A data de saída é obrigatória.';
    END IF;

    IF NEW.data_chegada IS NULL THEN
        RAISE EXCEPTION 'A data de chegada é obrigatória.';
    END IF;

    IF NEW.data_chegada <= NEW.data_saida THEN
        RAISE EXCEPTION 'A data de chegada deve ser posterior à data de saída.';
    END IF;

    IF NEW.preco IS NULL OR NEW.preco <= 0 THEN
        RAISE EXCEPTION 'O preço deve ser um valor positivo.';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trigger_verificar_voo
BEFORE INSERT OR UPDATE ON voo
FOR EACH ROW
EXECUTE FUNCTION verificar_insercao_voo();

-- Cria uma view na cache de todos os voos
DO $$
BEGIN
    EXECUTE 'DROP MATERIALIZED VIEW IF EXISTS mv_voos';
    EXECUTE 'CREATE MATERIALIZED VIEW mv_voos AS
             SELECT v.*, d.nome as destino_nome, d.pais as destino_pais
             FROM voo v
             INNER JOIN destino d ON v.destino_id = d.destino_id';
END $$;

-- Cria função que converte materialized view para json 
CREATE OR REPLACE FUNCTION voosToJson()
RETURNS json AS $$
    SELECT json_agg(row_to_json(v))
    FROM mv_voos v;
$$ LANGUAGE sql;

-- Função para executar o refresh da materialized view
CREATE OR REPLACE FUNCTION refresh_mv_voos()
RETURNS TRIGGER AS $$
BEGIN
    REFRESH MATERIALIZED VIEW mv_voos;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Trigger para atualizar views sempre que há alteração em base de dados
CREATE OR REPLACE TRIGGER trigger_insertVoos
AFTER INSERT OR UPDATE OR DELETE ON voo
FOR EACH STATEMENT
EXECUTE FUNCTION refresh_mv_voos();

-- VIEW: Voos disponíveis por pacote
CREATE OR REPLACE VIEW vw_voos_por_pacote AS
SELECT 
    p.pacote_id,
    p.nome AS pacote_nome,
    v.voo_id,
    v.companhia,
    v.numero_voo,
    v.data_saida,
    v.data_chegada,
    v.preco,
    d.destino_id,
    d.nome AS destino_nome,
    d.pais AS destino_pais
FROM pacote p
JOIN pacote_destino pd ON pd.pacote_id = p.pacote_id
JOIN destino d ON d.destino_id = pd.destino_id
JOIN voo v ON v.destino_id = d.destino_id
ORDER BY p.pacote_id, v.data_saida;

COMMENT ON VIEW vw_voos_por_pacote IS 
'Lista todos os voos disponíveis para cada pacote, baseado nos destinos do pacote';

