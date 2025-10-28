-- 1) tipo_user
INSERT INTO tipo_user (descricao_item) VALUES
('Administrador'),
('Cliente'),
('Agente');

-- 2) utilizador
INSERT INTO utilizador (tipo_user_id, nome, email, endereco, telefone) VALUES
(2, 'João Silva', 'joao@example.com', 'Rua A, 10', 912345678),
(2, 'Maria Souza', 'maria@example.com', 'Av. Central, 55', 987654321),
(1, 'Carlos Admin', 'admin@example.com', 'Sede Corporativa', 900000000);

-- 3) destino
INSERT INTO destino (pais, nome, descricao) VALUES
('Portugal', 'Lisboa', 'Cidade histórica e turística'),
('Brasil', 'Rio de Janeiro', 'Praias famosas e vida noturna'),
('França', 'Paris', 'A cidade do amor');

-- 4) voo
INSERT INTO voo (destino_id, companhia, numero_voo, data_saida, data_chegada, origem, destino, preco) VALUES
(1, 'TAP', 101, '2025-05-01', '2025-05-01', 'Porto', 'Lisboa', 120.00),
(2, 'LATAM', 202, '2025-06-10', '2025-06-10', 'São Paulo', 'Rio de Janeiro', 350.00),
(3, 'Air France', 303, '2025-07-15', '2025-07-15', 'Lisboa', 'Paris', 199.00);

-- 5) hotel
INSERT INTO hotel (destino_id, nome, endereco, preco_diario, descricao_item) VALUES
(1, 'Lisboa Center Hotel', 'Rua de Portugal, 80', 95.00, 'Hotel no coração da cidade'),
(2, 'Copacabana Palace', 'Av. Atlântica, 1702', 500.00, 'Luxo em frente à praia'),
(3, 'Paris Tower Hotel', 'Champs-Élysées, 25', 320.00, 'Próximo à Torre Eiffel');

-- 6) fatura_linha
INSERT INTO fatura_linha (descricao, quantidade, preco_unitario) VALUES
('Serviço de reserva de pacote turístico', 1, 799.99),
('Pacote completo com voo e hotel', 1, 1299.50),
('Pacote econômico', 1, 499.00);

-- 7) pacote
INSERT INTO pacote (fatura_linha_id, nome, descricao_item, data_inicio, data_fim, preco_total, estado) VALUES
(1, 'Romântico Europa', 'Pacote com hotel e tour', '2025-07-15', '2025-07-22', 799.99, 'ATIVO'),
(2, 'Praias do Brasil', 'Pacote com hotel All Inclusive', '2025-09-01', '2025-09-08', 1299.50, 'ATIVO'),
(3, 'City Tour Lisboa', 'Passeio guiado pela cidade', '2025-04-10', '2025-04-12', 499.00, 'INATIVO');

-- 8) feedback
INSERT INTO feedback (pacote_id, avaliacao, comentario, data_feedback) VALUES
(1, 5, 'Viagem inesquecível', '2025-08-01'),
(2, 4, 'Muito bom, recomendo', '2025-10-01'),
(3, 4, 'Cidade bonita e acolhedora', '2025-04-20');

-- 9) reserva
INSERT INTO reserva (data_inicio, data_fim, cliente_id, pacote_id) VALUES
('2025-07-15', '2025-07-22', 1, 1),
('2025-09-01', '2025-09-08', 2, 2),
('2025-04-10', '2025-04-12', 1, 3);

-- 10) compra
INSERT INTO compra (user_id, data_compra, valor_total) VALUES
(1, '2025-03-01', 799.99),
(2, '2025-05-10', 1299.50),
(1, '2025-02-20', 499.00);

-- 11) pagamento
INSERT INTO pagamento (compra_id, data_pagamento, valor, estado, metodo) VALUES
(1, '2025-03-02', 799.99, 'PENDENTE', 'Cartão'),
(2, '2025-05-10', 1299.50, 'PAGO', 'Pix'),
(3, '2025-02-21', 499.00, 'RECUSADO', 'Cartão');

-- 12) fatura
INSERT INTO fatura (compra_id, pagamento_id, data_emissao, valor_total) VALUES
(1, 1, '10:00:00', 799.99),
(2, 2, '14:30:00', 1299.50),
(3, 3, '09:15:00', 499.00);

-- 13) pacote_destino
INSERT INTO pacote_destino (pacote_id, destino_id) VALUES
(1, 3),
(2, 2),
(3, 1);

-- 14) pacote_hotel
INSERT INTO pacote_hotel (pacote_id, hotel_id) VALUES
(1, 3),
(2, 2),
(3, 1);

-- 15) pacote_voo
INSERT INTO pacote_voo (pacote_id, voo_id) VALUES
(1, 3),
(2, 2),
(3, 1);

