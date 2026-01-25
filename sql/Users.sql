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
        P.nome::text, 
        D.pais::text || ', ' || D.nome::text AS destino,
        P.data_inicio, 
        P.data_fim, 
        C.estado, 
        C.valor_total,
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

-- =====================================================
-- NOVA PROCEDURE: Cancelar Reserva com Validação
-- =====================================================
DROP FUNCTION IF EXISTS cancelar_reserva_utilizador CASCADE;

CREATE OR REPLACE FUNCTION cancelar_reserva_utilizador(
    p_compra_id INT,
    p_user_id INT
)
RETURNS TABLE (
    sucesso BOOLEAN,
    mensagem TEXT,
    reembolso DECIMAL(10,2)
) AS $$
DECLARE
    v_estado_atual TEXT;
    v_data_inicio DATE;
    v_valor_total DECIMAL(10,2);
    v_dias_antecedencia INT;
    v_reembolso DECIMAL(10,2);
BEGIN
    -- Buscar informações da compra
    SELECT c.estado, p.data_inicio, c.valor_total
    INTO v_estado_atual, v_data_inicio, v_valor_total
    FROM compra c
    JOIN pacote p ON c.pacote_id = p.pacote_id
    WHERE c.compra_id = p_compra_id AND c.user_id = p_user_id;
    
    -- Validar se compra existe e pertence ao utilizador
    IF NOT FOUND THEN
        RETURN QUERY SELECT FALSE, 'Compra não encontrada ou não pertence a este utilizador'::TEXT, 0::DECIMAL(10,2);
        RETURN;
    END IF;
    
    -- Validar se já está cancelada
    IF v_estado_atual = 'cancelada' THEN
        RETURN QUERY SELECT FALSE, 'Esta reserva já está cancelada'::TEXT, 0::DECIMAL(10,2);
        RETURN;
    END IF;
    
    -- Calcular dias de antecedência
    v_dias_antecedencia := v_data_inicio - CURRENT_DATE;
    
    -- Verificar se a viagem já passou
    IF v_dias_antecedencia < 0 THEN
        RETURN QUERY SELECT FALSE, 'Não é possível cancelar uma viagem que já passou'::TEXT, 0::DECIMAL(10,2);
        RETURN;
    END IF;
    
    -- Calcular reembolso baseado na antecedência
    IF v_dias_antecedencia >= 30 THEN
        v_reembolso := v_valor_total;  -- 100% de reembolso
    ELSIF v_dias_antecedencia >= 15 THEN
        v_reembolso := v_valor_total * 0.75;  -- 75% de reembolso
    ELSIF v_dias_antecedencia >= 7 THEN
        v_reembolso := v_valor_total * 0.50;  -- 50% de reembolso
    ELSE
        v_reembolso := v_valor_total * 0.25;  -- 25% de reembolso
    END IF;
    
    -- Atualizar estado da compra
    UPDATE compra
    SET estado = 'cancelada'
    WHERE compra_id = p_compra_id;
    
    -- Retornar sucesso com informações
    RETURN QUERY SELECT 
        TRUE, 
        format('Reserva cancelada com sucesso. Reembolso: %.2f€ (%s%% do valor)', 
               v_reembolso, 
               CASE 
                   WHEN v_dias_antecedencia >= 30 THEN '100'
                   WHEN v_dias_antecedencia >= 15 THEN '75'
                   WHEN v_dias_antecedencia >= 7 THEN '50'
                   ELSE '25'
               END
        )::TEXT,
        v_reembolso;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION cancelar_reserva_utilizador(INT, INT) IS 
'Cancela uma reserva com cálculo automático de reembolso baseado na antecedência';

-- =====================================================
-- NOVA PROCEDURE: Registar Utilizador Validado
-- =====================================================
DROP PROCEDURE IF EXISTS registar_utilizador_validado CASCADE;
DROP FUNCTION IF EXISTS registar_utilizador_validado CASCADE;

CREATE OR REPLACE PROCEDURE registar_utilizador_validado(
    p_email VARCHAR(255),
    p_password VARCHAR(255),
    p_firstname VARCHAR(150),
    p_lastname VARCHAR(150),
    OUT p_sucesso BOOLEAN,
    OUT p_user_id INT,
    OUT p_mensagem TEXT,
    p_telefone INTEGER DEFAULT NULL
) AS $$
DECLARE
    v_email_existe INT;
    v_new_user_id INT;
BEGIN
    -- Validação 1: Email não pode estar vazio
    IF p_email IS NULL OR TRIM(p_email) = '' THEN
        p_sucesso := FALSE;
        p_user_id := NULL;
        p_mensagem := 'Email é obrigatório';
        RETURN;
    END IF;
    
    -- Validação 2: Email deve ter formato válido
    IF p_email !~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$' THEN
        p_sucesso := FALSE;
        p_user_id := NULL;
        p_mensagem := 'Email com formato inválido';
        RETURN;
    END IF;
    
    -- Validação 3: Verificar se email já existe
    SELECT COUNT(*) INTO v_email_existe
    FROM utilizador
    WHERE LOWER(email) = LOWER(p_email);
    
    IF v_email_existe > 0 THEN
        p_sucesso := FALSE;
        p_user_id := NULL;
        p_mensagem := 'Este email já está registado';
        RETURN;
    END IF;
    
    -- Validação 4: Password deve ter no mínimo 8 caracteres (hash Django)
    IF LENGTH(p_password) < 8 THEN
        p_sucesso := FALSE;
        p_user_id := NULL;
        p_mensagem := 'Password deve ter no mínimo 8 caracteres';
        RETURN;
    END IF;
    
    -- Validação 5: Nome obrigatório
    IF p_firstname IS NULL OR TRIM(p_firstname) = '' THEN
        p_sucesso := FALSE;
        p_user_id := NULL;
        p_mensagem := 'Nome é obrigatório';
        RETURN;
    END IF;
    
    -- Validação 6: Apelido obrigatório
    IF p_lastname IS NULL OR TRIM(p_lastname) = '' THEN
        p_sucesso := FALSE;
        p_user_id := NULL;
        p_mensagem := 'Apelido é obrigatório';
        RETURN;
    END IF;
    
    -- Validação 7: Telefone (se fornecido, validar formato português)
    IF p_telefone IS NOT NULL THEN
        IF p_telefone < 200000000 OR p_telefone > 999999999 THEN
            p_sucesso := FALSE;
            p_user_id := NULL;
            p_mensagem := 'Telefone inválido (deve ter 9 dígitos)';
            RETURN;
        END IF;
    END IF;
    
    -- Inserir novo utilizador
    INSERT INTO utilizador (
        email,
        password,
        first_name,
        last_name,
        telefone,
        is_active,
        is_staff,
        is_superuser,
        date_joined
    )
    VALUES (
        LOWER(TRIM(p_email)),
        p_password,  -- Password já vem hasheada do Django (pbkdf2_sha256)
        TRIM(p_firstname),
        TRIM(p_lastname),
        p_telefone,
        TRUE,
        FALSE,
        FALSE,
        CURRENT_TIMESTAMP
    )
    RETURNING user_id INTO v_new_user_id;
    
    -- Retornar sucesso
    p_sucesso := TRUE;
    p_user_id := v_new_user_id;
    p_mensagem := format('Bem-vindo, %s! Registo efetuado com sucesso.', p_firstname);
END;
$$ LANGUAGE plpgsql;

COMMENT ON PROCEDURE registar_utilizador_validado(VARCHAR, VARCHAR, VARCHAR, VARCHAR, BOOLEAN, INT, TEXT, INTEGER) IS 
'Regista novo utilizador com validações: email único, formato válido, campos obrigatórios';

-- =====================================================
-- Wrapper Function para chamar a PROCEDURE
-- =====================================================
DROP FUNCTION IF EXISTS registar_utilizador_validado_wrapper CASCADE;

CREATE OR REPLACE FUNCTION registar_utilizador_validado_wrapper(
    p_email VARCHAR(255),
    p_password VARCHAR(255),
    p_firstname VARCHAR(150),
    p_lastname VARCHAR(150),
    p_telefone INTEGER DEFAULT NULL
)
RETURNS TABLE (
    sucesso BOOLEAN,
    user_id INT,
    mensagem TEXT
) AS $$
DECLARE
    v_sucesso BOOLEAN;
    v_user_id INT;
    v_mensagem TEXT;
BEGIN
    CALL registar_utilizador_validado(
        p_email, p_password, p_firstname, p_lastname,
        v_sucesso, v_user_id, v_mensagem, p_telefone
    );
    
    RETURN QUERY SELECT v_sucesso, v_user_id, v_mensagem;
END;
$$ LANGUAGE plpgsql;
