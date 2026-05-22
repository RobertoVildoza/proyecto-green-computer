CREATE DATABASE IF NOT EXISTS portal_clientes
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE portal_clientes;

CREATE TABLE IF NOT EXISTS cliente (
  id_cliente  INT AUTO_INCREMENT PRIMARY KEY,
  nombre      VARCHAR(50)  NOT NULL,
  apellido    VARCHAR(50)  NOT NULL,
  email       VARCHAR(120) NOT NULL UNIQUE,
  telefono    VARCHAR(20),
  empresa     VARCHAR(100),
  created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS usuario_portal (
  id_usuario   INT AUTO_INCREMENT PRIMARY KEY,
  id_cliente   INT          NOT NULL,
  username     VARCHAR(60)  NOT NULL UNIQUE,
  contrasenia  VARCHAR(255) NOT NULL,
  activo       TINYINT(1)   DEFAULT 1,
  reset_code   VARCHAR(10)  DEFAULT NULL,
  ultimo_login DATETIME     DEFAULT NULL,
  created_at   DATETIME     DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (id_cliente) REFERENCES cliente(id_cliente)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS equipo (
  id_equipo    INT AUTO_INCREMENT PRIMARY KEY,
  nombre_equipo VARCHAR(100) NOT NULL,
  categoria    VARCHAR(50)  NOT NULL,
  modelo       VARCHAR(100) NOT NULL,
  fabricante   VARCHAR(50)  NOT NULL,
  specs        TEXT,
  numero_serie VARCHAR(80)  UNIQUE,
  estado       ENUM('disponible','alquilado','mantenimiento') DEFAULT 'disponible' NOT NULL,
  created_at   DATETIME     DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS contrato_alquiler (
  id_contrato    INT AUTO_INCREMENT PRIMARY KEY,
  id_cliente     INT          NOT NULL,
  fecha_inicio   DATE         NOT NULL,
  fecha_vencim   DATE,
  valor_mensual  DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  tipo_contrato  ENUM('alquiler','leasing') DEFAULT 'alquiler' NOT NULL,
  cuotas_total   INT          DEFAULT NULL,
  cuotas_pagadas INT          DEFAULT 0,
  estado         ENUM('vigente','pendiente','terminado') DEFAULT 'pendiente' NOT NULL,
  notas          TEXT,
  created_at     DATETIME     DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (id_cliente) REFERENCES cliente(id_cliente)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS detalle_contrato (
  id_contrato  INT NOT NULL,
  id_equipo    INT NOT NULL,
  cantidad     INT DEFAULT 1 NOT NULL,
  PRIMARY KEY (id_contrato, id_equipo),
  FOREIGN KEY (id_contrato) REFERENCES contrato_alquiler(id_contrato),
  FOREIGN KEY (id_equipo)   REFERENCES equipo(id_equipo)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS ticket_soporte (
  id_ticket      INT AUTO_INCREMENT PRIMARY KEY,
  id_cliente     INT          NOT NULL,
  id_equipo      INT          DEFAULT NULL,
  tipo           ENUM('consulta','garantia') NOT NULL,
  asunto         VARCHAR(200) NOT NULL,
  descripcion    TEXT         NOT NULL,
  estado         ENUM('abierto','en_proceso','cerrado') DEFAULT 'abierto' NOT NULL,
  fecha_ticket   DATETIME     DEFAULT CURRENT_TIMESTAMP,
  fecha_cierre   DATETIME     DEFAULT NULL,
  FOREIGN KEY (id_cliente) REFERENCES cliente(id_cliente),
  FOREIGN KEY (id_equipo)  REFERENCES equipo(id_equipo)
) ENGINE=InnoDB;

INSERT INTO cliente (nombre, apellido, email, telefono, empresa) VALUES
('Juan',    'Pérez',    'juan.perez@empresa.com',   '1122334455', 'Empresa SA'),
('María',   'García',   'maria.garcia@startup.io',  '1166778899', 'Startup IO'),
('Carlos',  'López',    'carlos.lopez@corp.net',    '1144556677', 'Corp Net'),
('Lucía',   'Martínez', 'lucia.martinez@design.ar', '1188990011', 'Design AR'),
('Usuario', 'Prueba',   'prueba@greencomputer.com', '1100000000', 'Green Computer Test');

INSERT INTO usuario_portal (id_cliente, username, contrasenia) VALUES
(1, 'jperez',    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMUJged0b0Px.TnPkGf7BVGC2i'),
(2, 'mgarcia',   '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMUJged0b0Px.TnPkGf7BVGC2i'),
(3, 'clopez',    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMUJged0b0Px.TnPkGf7BVGC2i'),
(4, 'lmartinez', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMUJged0b0Px.TnPkGf7BVGC2i'),
(5, 'prueba',    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMUJged0b0Px.TnPkGf7BVGC2i');

INSERT INTO equipo (nombre_equipo, categoria, modelo, fabricante, specs, numero_serie, estado) VALUES
('ThinkPad X1 Carbon Gen 11', 'notebook', 'ThinkPad X1 Carbon', 'Lenovo', 'Intel Core i7-1365U, 16GB RAM, 512GB SSD NVMe, 14" IPS, Wi-Fi 6E',              'TP-X1C-001', 'alquilado'),
('MacBook Pro 14" M3',        'notebook', 'MacBook Pro M3',     'Apple',  'Apple M3 Pro, 18GB RAM unificada, 512GB SSD, 14.2" Liquid Retina XDR, MagSafe 3', 'MBP-14-M3-002', 'alquilado'),
('Dell XPS 15 9530',          'notebook', 'Dell XPS 15',        'Dell',   'Intel Core i9-13900H, 32GB RAM, 1TB SSD, 15.6" OLED 3.5K, Nvidia RTX 4060',      'DXPS-15-003', 'alquilado'),
('iMac 27" M3',               'desktop',  'iMac 27 M3',         'Apple',  'Apple M3 Max, 32GB RAM unificada, 1TB SSD, 27" 5K Retina, Magic Keyboard+Mouse',  'IMAC-27-M3-004', 'alquilado'),
('ThinkPad E14 Gen 5',        'notebook', 'ThinkPad E14 Gen5',  'Lenovo', 'AMD Ryzen 7 7730U, 16GB RAM, 512GB SSD, 14" FHD IPS, USB-C x2',                  'TP-E14-005', 'alquilado'),
('MacBook Air M2',            'notebook', 'MacBook Air M2',     'Apple',  'Apple M2, 8GB RAM, 256GB SSD, 13.6" Liquid Retina, MagSafe 2, Fan-less',          'MBA-M2-006', 'alquilado');

INSERT INTO contrato_alquiler (id_cliente, fecha_inicio, fecha_vencim, valor_mensual, tipo_contrato, cuotas_total, cuotas_pagadas, estado, notas) VALUES
(1, '2024-08-01', NULL,         75000.00, 'alquiler', NULL, 0,  'vigente',   'Contrato corporativo – renovación automática'),
(1, '2024-10-15', NULL,         95000.00, 'alquiler', NULL, 0,  'vigente',   'iMac para home office'),
(1, '2023-05-01', '2024-04-30', 55000.00, 'alquiler', NULL, 0,  'terminado', 'Contrato finalizado por cambio de equipo'),
(2, '2024-09-01', NULL,         90000.00, 'alquiler', NULL, 0,  'vigente',   'MacBook para desarrollo'),
(2, '2025-03-01', '2026-02-28', 70000.00, 'leasing',  24,   2,  'vigente',   'Leasing con opción de compra'),
(3, '2024-06-01', NULL,         85000.00, 'alquiler', NULL, 0,  'vigente',   'Dell XPS para diseño 3D'),
(3, '2023-01-10', '2024-05-31', 65000.00, 'alquiler', NULL, 0,  'terminado', 'Contrato previo'),
(4, '2025-01-01', NULL,         90000.00, 'alquiler', NULL, 0,  'vigente',   'MacBook para diseño gráfico'),
(4, '2024-11-01', NULL,         55000.00, 'leasing',  12,   4,  'vigente',   'MacBook Air leasing'),
(5, '2024-03-01', NULL,         75000.00, 'alquiler', NULL, 0,  'vigente',   'Equipo de prueba vigente'),
(5, '2025-01-15', '2026-01-14', 85000.00, 'leasing',  12,   2,  'vigente',   'Leasing de prueba'),
(5, '2023-06-01', '2024-05-31', 90000.00, 'alquiler', NULL, 0,  'terminado', 'Contrato de prueba terminado');

INSERT INTO detalle_contrato (id_contrato, id_equipo, cantidad) VALUES
(1,  1, 1),
(2,  4, 1),
(3,  6, 1),
(4,  2, 1),
(5,  5, 1),
(6,  3, 1),
(7,  1, 1),
(8,  2, 1),
(9,  6, 1),
(10, 1, 1),
(11, 3, 1),
(12, 4, 1);

INSERT INTO ticket_soporte (id_cliente, id_equipo, tipo, asunto, descripcion, estado, fecha_ticket) VALUES
(1, 1, 'consulta', 'Consulta sobre renovación',  'Quisiera saber las condiciones para renovar el contrato por 12 meses más.',          'abierto',    '2025-02-10 09:30:00'),
(1, 4, 'garantia', 'Teclado Magic Keyboard',     'Una de las teclas del Magic Keyboard no responde correctamente.',                     'en_proceso', '2025-02-28 14:00:00'),
(2, 2, 'consulta', 'Actualización de RAM',       '¿Es posible solicitar un equipo con 32GB de RAM para proyectos de compilación?',     'cerrado',    '2025-01-20 10:15:00'),
(3, 3, 'garantia', 'Pantalla OLED – líneas',     'Aparecieron líneas horizontales en la pantalla al conectar monitor externo.',        'abierto',    '2025-03-01 08:45:00'),
(5, 1, 'consulta', 'Ticket de prueba consulta',  'Este es un ticket de consulta generado para probar el sistema.',                     'abierto',    '2025-02-15 12:00:00'),
(5, 1, 'garantia', 'Ticket de prueba garantía',  'Este es un ticket de garantía generado para probar el sistema.',                     'cerrado',    '2025-01-05 16:30:00');

SELECT 'portal_clientes creado correctamente' AS resultado;
SELECT 'cliente'           AS tabla, COUNT(*) AS registros FROM cliente
UNION ALL SELECT 'usuario_portal',  COUNT(*) FROM usuario_portal
UNION ALL SELECT 'equipo',          COUNT(*) FROM equipo
UNION ALL SELECT 'contrato_alquiler', COUNT(*) FROM contrato_alquiler
UNION ALL SELECT 'detalle_contrato', COUNT(*) FROM detalle_contrato
UNION ALL SELECT 'ticket_soporte',  COUNT(*) FROM ticket_soporte;
