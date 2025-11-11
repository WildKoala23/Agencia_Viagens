-- Script para popular base de dados com dados de teste

-- Inserir destinos
INSERT INTO destino (nome, pais, descricao) VALUES
('Paris', 'França', 'Cidade da luz, conhecida pela Torre Eiffel'),
('Barcelona', 'Espanha', 'Cidade vibrante com arquitetura de Gaudí'),
('Roma', 'Itália', 'Cidade histórica com o Coliseu'),
('Londres', 'Reino Unido', 'Capital do Reino Unido'),
('Tokyo', 'Japão', 'Cidade moderna e tradicional')
ON CONFLICT DO NOTHING;

-- Inserir hotéis
INSERT INTO hotel (nome, localizacao, classificacao, preco_por_noite) VALUES
('Hotel Paris Luxe', 'Paris, França', 5, 250.00),
('Barcelona Inn', 'Barcelona, Espanha', 4, 150.00),
('Roma Palace', 'Roma, Itália', 5, 300.00),
('London Central', 'Londres, Reino Unido', 4, 200.00),
('Tokyo Stay', 'Tokyo, Japão', 4, 180.00)
ON CONFLICT DO NOTHING;

-- Inserir voos
INSERT INTO voo (companhia_aerea, origem, destino_voo, data_partida, data_chegada, preco) VALUES
('Air France', 'Lisboa', 'Paris', '2025-12-01', '2025-12-01', 150.00),
('Vueling', 'Porto', 'Barcelona', '2025-12-05', '2025-12-05', 120.00),
('TAP', 'Lisboa', 'Roma', '2025-12-10', '2025-12-10', 180.00),
('British Airways', 'Lisboa', 'Londres', '2025-12-15', '2025-12-15', 200.00),
('JAL', 'Lisboa', 'Tokyo', '2026-01-10', '2026-01-11', 800.00)
ON CONFLICT DO NOTHING;

-- Inserir pacotes
INSERT INTO pacote (nome, descricao, preco_total, data_inicio, data_fim, num_pessoas) VALUES
('Pacote Paris Romântico', 'Viagem romântica para Paris com hotel 5 estrelas', 1500.00, '2025-12-01', '2025-12-07', 2),
('Barcelona Aventura', 'Explore Barcelona e sua cultura', 1200.00, '2025-12-05', '2025-12-10', 2),
('Roma Histórica', 'Descubra a história de Roma', 1800.00, '2025-12-10', '2025-12-17', 2),
('Londres Cultural', 'Cultura e tradição em Londres', 1600.00, '2025-12-15', '2025-12-20', 2),
('Tokyo Mistério', 'Aventura no Japão moderno', 3000.00, '2026-01-10', '2026-01-20', 2)
ON CONFLICT DO NOTHING;

-- Associar pacotes com destinos
INSERT INTO pacote_destino (pacote_id, destino_id) VALUES
(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)
ON CONFLICT DO NOTHING;

-- Associar pacotes com hotéis
INSERT INTO pacote_hotel (pacote_id, hotel_id) VALUES
(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)
ON CONFLICT DO NOTHING;

-- Associar pacotes com voos
INSERT INTO pacote_voo (pacote_id, voo_id) VALUES
(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)
ON CONFLICT DO NOTHING;

-- Inserir algumas compras de exemplo (usando o user_id 1 que é o admin)
INSERT INTO compra (user_id, pacote_id, data_compra, valor_total, estado) VALUES
(1, 1, '2025-11-01', 1500.00, 'Confirmada'),
(1, 2, '2025-11-05', 1200.00, 'Pendente')
ON CONFLICT DO NOTHING;

-- Inserir feedbacks
INSERT INTO feedback (user_id, compra_id, avaliacao, comentario, data_feedback) VALUES
(1, 1, 5, 'Viagem maravilhosa! Tudo perfeito!', '2025-11-08')
ON CONFLICT DO NOTHING;

-- Inserir pagamentos
INSERT INTO pagamento (compra_id, data_pagamento, valor, estado) VALUES
(1, '2025-11-01', 1500.00, 'Pago')
ON CONFLICT DO NOTHING;

-- Inserir faturas
INSERT INTO fatura (compra_id, data_emissao, valor_total, estado) VALUES
(1, '2025-11-01', 1500.00, 'Emitida')
ON CONFLICT DO NOTHING;

-- Inserir linhas de fatura
INSERT INTO fatura_linha (fatura_id, descricao, quantidade, preco_unitario, total) VALUES
(1, 'Pacote Paris Romântico', 1, 1500.00, 1500.00)
ON CONFLICT DO NOTHING;

COMMIT;
