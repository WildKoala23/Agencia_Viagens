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

    IF NEW.data_chegada <= NEW.data_saida THEN
        RAISE EXCEPTION 'A data de chegada deve ser posterior à data de saída.';
    END IF;

    IF NEW.preco <= 0 THEN
        RAISE EXCEPTION 'O preço deve ser um valor positivo.';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trigger_verificar_voo
BEFORE INSERT ON voo
FOR EACH ROW
EXECUTE FUNCTION verificar_insercao_voo();
