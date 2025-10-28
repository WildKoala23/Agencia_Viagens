-- ----------------------------------------
-- Insert TipoUser
-- ----------------------------------------
INSERT INTO tipo_user (descricao_item) VALUES
('Admin'),
('Cliente');

-- ----------------------------------------
-- Insert Utilizador
-- ----------------------------------------
INSERT INTO utilizador (tipo_user_id, nome, email, endereco, telefone) VALUES
(1, 'Alice', 'alice@example.com', '123 Rua A', 912345678),
(2, 'Bob', 'bob@example.com', '456 Rua B', 987654321);

-- ----------------------------------------
-- Insert Destino
-- ----------------------------------------
INSERT INTO destino (pais, nome) VALUES
('Portugal', 'Lisboa'),
('Espanha', 'Barcelona');

-- ----------------------------------------
-- Insert Pacote
-- ----------------------------------------
INSERT INTO pacote (nome, descricao_item, data_inicio, data_fim, preco_total, estado) VALUES
('Pacote Verão Lisboa', 'Pacote completo para Lisboa', '2025-07-01', '2025-07-10', 1200.00, 'Ativo'),
('Pacote Espanha', 'Pacote completo para Barcelona', '2025-08-01', '2025-08-07', 1500.00, 'Ativo');

-- ----------------------------------------
-- Insert Voo
-- ----------------------------------------
INSERT INTO voo (destino_id, companhia, numero_voo, data_saida, data_chegada, preco) VALUES
(1, 'TAP', 123, '2025-07-01', '2025-07-01', 150.00),
(2, 'Iberia', 456, '2025-08-01', '2025-08-01', 180.00);

-- ----------------------------------------
-- Insert Hotel
-- ----------------------------------------
INSERT INTO hotel (destino_id, nome, endereco, preco_diario, descricao_item) VALUES
(1, 'Hotel Lisboa Centro', 'Av. da Liberdade, 100', 100.00, 'Hotel 4 estrelas no centro de Lisboa'),
(2, 'Hotel Barcelona Playa', 'Passeig de Gracia, 50', 120.00, 'Hotel à beira-mar');

-- ----------------------------------------
-- Insert PacoteDestino
-- ----------------------------------------
INSERT INTO pacote_destino (pacote_id, destino_id) VALUES
(1, 1),
(2, 2);

-- ----------------------------------------
-- Insert PacoteHotel
-- ----------------------------------------
INSERT INTO pacote_hotel (pacote_id, hotel_id) VALUES
(1, 1),
(2, 2);

-- ----------------------------------------
-- Insert PacoteVoo
-- ----------------------------------------
INSERT INTO pacote_voo (pacote_id, voo_id) VALUES
(1, 1),
(2, 2);

-- ----------------------------------------
-- Insert Feedback
-- ----------------------------------------
INSERT INTO feedback (pacote_id, avaliacao, comentario, data_feedback) VALUES
(1, 5, 'Excelente pacote!', '2025-07-11'),
(2, 4, 'Muito bom, recomendo', '2025-08-08');

-- ----------------------------------------
-- Insert Compra
-- ----------------------------------------
INSERT INTO compra (pagamento_id, fatura_id, user_id, pacote_id, data_compra, valor_total, estado) VALUES
(1, 1, 1, 1, '2025-06-20', 1200.00, 'Concluída'),
(2, 2, 2, 2, '2025-07-15', 1500.00, 'Concluída');

-- ----------------------------------------
-- Insert Pagamento
-- ----------------------------------------
INSERT INTO pagamento (compra_id, data_pagamento, valor, estado, metodo) VALUES
(1, '2025-06-21', 1200.00, 'Pago', 'Cartão de Crédito'),
(2, '2025-07-16', 1500.00, 'Pago', 'Transferência Bancária');

-- ----------------------------------------
-- Insert Factura
-- ----------------------------------------
INSERT INTO fatura (compra_id, pagamento_id, data_emissao, valor_total) VALUES
(1, 1, '10:00:00', 1200.00),
(2, 2, '15:00:00', 1500.00);

-- ----------------------------------------
-- Insert FacturaLinha
-- ----------------------------------------
INSERT INTO fatura_linha (fatura_id, pacote_id, descricao_item, preco, subtotal) VALUES
(1, 1, 'Pacote Verão Lisboa', 1200.00, 1200.00),
(2, 2, 'Pacote Espanha', 1500.00, 1500.00);
