-- ===================
-- CRIAÇÃO DAS TABELAS ATUALIZADAS
-- ===================

DROP TABLE IF EXISTS fatura CASCADE; 
DROP TABLE IF EXISTS pagamento CASCADE;
DROP TABLE IF EXISTS reserva CASCADE;
DROP TABLE IF EXISTS feedback CASCADE;
DROP TABLE IF EXISTS pacote CASCADE;
DROP TABLE IF EXISTS hotel CASCADE;
DROP TABLE IF EXISTS voo CASCADE;
DROP TABLE IF EXISTS destino CASCADE;
DROP TABLE IF EXISTS utilizador CASCADE;
DROP TABLE IF EXISTS tipo_user CASCADE;
DROP TABLE IF EXISTS compra CASCADE;
DROP TABLE IF EXISTS fatura_linha CASCADE;
DROP TABLE IF EXISTS pacote_destino CASCADE;
DROP TABLE IF EXISTS pacote_hotel CASCADE;
DROP TABLE IF EXISTS pacote_voo CASCADE;

-- Tabela tipo_user
CREATE TABLE tipo_user (
    tipo_user_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    descricao_item TEXT NOT NULL
);

-- Tabela utilizador (cliente)
CREATE TABLE utilizador (
    user_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tipo_user_id INTEGER NOT NULL,
    nome TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    endereco TEXT,
    telefone INTEGER,
    FOREIGN KEY (tipo_user_id) REFERENCES tipo_user(tipo_user_id)
);

-- Tabela destino
CREATE TABLE destino (
    destino_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pais TEXT NOT NULL,
    nome TEXT NOT NULL
);

-- Tabela voo
CREATE TABLE voo (
    voo_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    destino_id INTEGER NOT NULL,
    companhia TEXT NOT NULL,
    numero_voo INTEGER NOT NULL,
    data_saida DATE NOT NULL,
    data_chegada DATE NOT NULL,
    preco DECIMAL(19, 2) NOT NULL,
    FOREIGN KEY (destino_id) REFERENCES destino(destino_id)
);

-- Tabela hotel
CREATE TABLE hotel (
    hotel_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    destino_id INTEGER NOT NULL,
    nome VARCHAR(200) NOT NULL,
    endereco TEXT,
    preco_diario DECIMAL(10, 2) NOT NULL,
    descricao_item TEXT,
    FOREIGN KEY (destino_id) REFERENCES destino(destino_id)
);

-- Tabela fatura_linha
CREATE TABLE fatura_linha (
    fatura_linha_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    fatura_id INT,
    pacote_id INT,
    descricao_item TEXT,
    preco DECIMAL(10, 2),
    subtotal DECIMAL(10, 2),
    FOREIGN KEY (pacote_id) REFERENCES pacote(pacote_id),
    FOREIGN KEY (fatura_id) REFERENCES fatura(fatura_id)
);

-- Tabela pacote
CREATE TABLE pacote (
    pacote_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome TEXT NOT NULL,
    descricao_item TEXT,
    data_inicio DATE NOT NULL,
    data_fim DATE NOT NULL,
    preco_total DECIMAL(10, 2) NOT NULL,
    estado TEXT,
    imagem VARCHAR(100)
);

-- Tabela feedback
CREATE TABLE feedback (
    feedback_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pacote_id INTEGER NOT NULL,
    avaliacao INTEGER CHECK (avaliacao BETWEEN 1 AND 5),
    comentario TEXT,
    data_feedback DATE NOT NULL,
    FOREIGN KEY (pacote_id) REFERENCES pacote(pacote_id)
);

-- Tabela reserva
-- CREATE TABLE reserva (
--     reserva_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
--     data_inicio DATE NOT NULL,
--     data_fim DATE NOT NULL,
--     cliente_id INTEGER NOT NULL,
--     pacote_id INTEGER NOT NULL,
--     FOREIGN KEY (cliente_id) REFERENCES utilizador(user_id),
--     FOREIGN KEY (pacote_id) REFERENCES pacote(pacote_id)
-- );

-- Tabela compra
CREATE TABLE compra (
    compra_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pacote_id INTEGER,
    pagamento_id INTEGER,
    user_id INTEGER NOT NULL,
    data_compra DATE NOT NULL,
    valor_total DECIMAL(10, 2) NOT NULL,
    estado TEXT,
    FOREIGN KEY (user_id) REFERENCES utilizador(user_id),
    FOREIGN KEY (pacote_id) REFERENCES pacote(pacote_id),
    FOREIGN KEY (pagamento_id) REFERENCES pagamento(pagamento_id)
);

-- Tabela pagamento
CREATE TABLE pagamento (
    pagamento_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    compra_id INTEGER NOT NULL,
    data_pagamento DATE NOT NULL,
    valor DECIMAL(10, 2) NOT NULL,
    estado TEXT,
    metodo TEXT,
    FOREIGN KEY (compra_id) REFERENCES compra(compra_id)
);

-- Tabela fatura
CREATE TABLE fatura (
    fatura_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    compra_id INTEGER NOT NULL,
    pagamento_id INTEGER NOT NULL,
    data_emissao TIME NOT NULL,
    valor_total DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (compra_id) REFERENCES compra(compra_id),
    FOREIGN KEY (pagamento_id) REFERENCES pagamento(pagamento_id)
);

-- Tabelas many-to-many
CREATE TABLE pacote_destino (
    pacote_id INTEGER NOT NULL,
    destino_id INTEGER NOT NULL,
    PRIMARY KEY (pacote_id, destino_id),
    FOREIGN KEY (pacote_id) REFERENCES pacote(pacote_id),
    FOREIGN KEY (destino_id) REFERENCES destino(destino_id)
);

CREATE TABLE pacote_hotel (
    pacote_id INTEGER NOT NULL,
    hotel_id INTEGER NOT NULL,
    PRIMARY KEY (pacote_id, hotel_id),
    FOREIGN KEY (pacote_id) REFERENCES pacote(pacote_id),
    FOREIGN KEY (hotel_id) REFERENCES hotel(hotel_id)
);

CREATE TABLE pacote_voo (
    pacote_id INTEGER NOT NULL,
    voo_id INTEGER NOT NULL,
    PRIMARY KEY (pacote_id, voo_id),
    FOREIGN KEY (pacote_id) REFERENCES pacote(pacote_id),
    FOREIGN KEY (voo_id) REFERENCES voo(voo_id)
);
