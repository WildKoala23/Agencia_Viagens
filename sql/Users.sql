-----------------------------------------------------
--PROCEDURES: 
-----------------------------------------------------

--Inserir utilizador sem "duplicar" email
-----------------------------------------------------
DROP PROCEDURE IF EXISTS sp_inserir_utilizador(
    INTEGER, TEXT, TEXT, TEXT, INTEGER
);

CREATE OR REPLACE PROCEDURE sp_inserir_utilizador(
    p_tipo_user_id INTEGER,
    p_nome TEXT,
    p_email TEXT,
    p_endereco TEXT,
    p_telefone INTEGER
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM utilizador WHERE email = p_email) THEN
        RAISE EXCEPTION 'E-mail já registado: %', p_email;
    END IF;

    INSERT INTO utilizador(tipo_user_id, nome, email, endereco, telefone)
    VALUES (p_tipo_user_id, p_nome, p_email, p_endereco, p_telefone);
END;
$$;

-----------------------------------------------------
--TRIGGERS: 
-----------------------------------------------------

--Garantir que o número de telefone tem pelo menos 9 dígitos
-----------------------------------------------------
DROP TRIGGER IF EXISTS tg_telefone_check ON utilizador;

DROP FUNCTION IF EXISTS trg_check_telefone();

CREATE OR REPLACE FUNCTION trg_check_telefone()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.telefone IS NOT NULL AND NEW.telefone < 100000000 THEN
        RAISE EXCEPTION 'Telefone inválido. Deve ter pelo menos 9 dígitos.'
            USING ERRCODE = 'P0001';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tg_telefone_check
BEFORE INSERT OR UPDATE ON utilizador
FOR EACH ROW EXECUTE FUNCTION trg_check_telefone();