-- ================================
-- CRIAÇÃO DAS TABELAS (corrigidas com IDs auto)
-- ================================

DROP TABLE IF EXISTS fatura CASCADE; 
DROP TABLE IF EXISTS pagamento CASCADE;
DROP TABLE IF EXISTS reserva CASCADE;
DROP TABLE IF EXISTS feedback CASCADE;
DROP TABLE IF EXISTS pacote CASCADE;
DROP TABLE IF EXISTS hotel CASCADE;
DROP TABLE IF EXISTS voo CASCADE;
DROP TABLE IF EXISTS destino CASCADE;
DROP TABLE IF EXISTS cliente CASCADE;

CREATE TABLE cliente (
    cliente_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome TEXT NOT NULL,
    idade INTEGER,
    nif INTEGER UNIQUE,
    morada TEXT,
    email TEXT UNIQUE
);

CREATE TABLE destino (
    destino_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    pais TEXT NOT NULL,
    cidade TEXT NOT NULL,
    descricao TEXT
);

CREATE TABLE voo (
    voo_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    data_voo DATE NOT NULL,
    hora_partida TIME NOT NULL,
    hora_chegada TIME NOT NULL,
    duracao INTERVAL,
    origem TEXT NOT NULL,
    porta_embarque INTEGER
);

CREATE TABLE hotel (
    hotel_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome TEXT NOT NULL,
    morada TEXT
);

CREATE TABLE pacote (
    pacote_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    preco MONEY NOT NULL,
    descricao TEXT,
    destino_id INTEGER NOT NULL,
    voo_id INTEGER NOT NULL,
    hotel_id INTEGER NOT NULL,
    FOREIGN KEY (destino_id) REFERENCES destino(destino_id),
    FOREIGN KEY (voo_id) REFERENCES voo(voo_id),
    FOREIGN KEY (hotel_id) REFERENCES hotel(hotel_id)
);

CREATE TABLE feedback (
    feedback_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    data_feedback DATE NOT NULL,
    avaliacao INTEGER CHECK (avaliacao BETWEEN 1 AND 5),
    comentario TEXT,
    cliente_id INTEGER NOT NULL,
    pacote_id INTEGER NOT NULL,
    FOREIGN KEY (cliente_id) REFERENCES cliente(cliente_id),
    FOREIGN KEY (pacote_id) REFERENCES pacote(pacote_id)
);

CREATE TABLE reserva (
    reserva_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    data_inicio DATE NOT NULL,
    data_fim DATE NOT NULL,
    cliente_id INTEGER NOT NULL,
    pacote_id INTEGER NOT NULL,
    FOREIGN KEY (cliente_id) REFERENCES cliente(cliente_id),
    FOREIGN KEY (pacote_id) REFERENCES pacote(pacote_id)
);

CREATE TABLE pagamento (
    pagamento_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    data_pagamento DATE NOT NULL,
    montante MONEY NOT NULL,
    reserva_id INTEGER NOT NULL,
    FOREIGN KEY (reserva_id) REFERENCES reserva(reserva_id)
);

CREATE TABLE fatura (
    fatura_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    data_emissao DATE NOT NULL,
    valor_total MONEY NOT NULL,
    pagamento_id INTEGER NOT NULL,
    FOREIGN KEY (pagamento_id) REFERENCES pagamento(pagamento_id)
);
