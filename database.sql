-- Amai Shop - Base de Datos
CREATE DATABASE IF NOT EXISTS amai_shop CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE amai_shop;

-- Tabla de Usuarios
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Prendas
CREATE TABLE prendas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    categoria ENUM('camisas', 'playeras', 'pantalones', 'vestidos', 'faldas', 'chaquetas', 'zapatos') NOT NULL,
    genero ENUM('hombre', 'mujer') NOT NULL,
    imagen VARCHAR(255) NOT NULL,
    precio DECIMAL(10,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Outfits
CREATE TABLE outfits (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    imagen_resultado VARCHAR(255),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- Tabla intermedia Outfit-Prendas
CREATE TABLE outfit_prendas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    outfit_id INT NOT NULL,
    prenda_id INT NOT NULL,
    posicion_x INT DEFAULT 0,
    posicion_y INT DEFAULT 0,
    escala DECIMAL(3,2) DEFAULT 1.00,
    FOREIGN KEY (outfit_id) REFERENCES outfits(id) ON DELETE CASCADE,
    FOREIGN KEY (prenda_id) REFERENCES prendas(id) ON DELETE CASCADE
);

-- Datos de ejemplo - Hombre
INSERT INTO prendas (nombre, categoria, genero, imagen, precio) VALUES
('Camisa Oxford Blanca', 'camisas', 'hombre', 'ropa/hombre/camisa_oxford.png', 49.99),
('Camisa Denim Azul', 'camisas', 'hombre', 'ropa/hombre/camisa_denim.png', 59.99),
('Playera Básica Negra', 'playeras', 'hombre', 'ropa/hombre/playera_negra.png', 19.99),
('Playera Estampada', 'playeras', 'hombre', 'ropa/hombre/playera_estampada.png', 24.99),
('Jeans Slim Fit', 'pantalones', 'hombre', 'ropa/hombre/jeans_slim.png', 69.99),
('Chinos Caqui', 'pantalones', 'hombre', 'ropa/hombre/chinos_caqui.png', 54.99),
('Chaqueta Bomber', 'chaquetas', 'hombre', 'ropa/hombre/bomber.png', 89.99),
('Zapatos Derby', 'zapatos', 'hombre', 'ropa/hombre/derby.png', 119.99);

-- Datos de ejemplo - Mujer
INSERT INTO prendas (nombre, categoria, genero, imagen, precio) VALUES
('Blusa Seda Blanca', 'camisas', 'mujer', 'ropa/mujer/blusa_seda.png', 55.00),
('Camisa Oversize', 'camisas', 'mujer', 'ropa/mujer/camisa_oversize.png', 45.00),
('Playera Crop Top', 'playeras', 'mujer', 'ropa/mujer/crop_top.png', 22.99),
('Vestido Floral', 'vestidos', 'mujer', 'ropa/mujer/vestido_floral.png', 79.99),
('Vestido Negro Elegante', 'vestidos', 'mujer', 'ropa/mujer/vestido_negro.png', 99.99),
('Falda Midi Plisada', 'faldas', 'mujer', 'ropa/mujer/falda_midi.png', 49.99),
('Jeans Mom Fit', 'pantalones', 'mujer', 'ropa/mujer/jeans_mom.png', 64.99),
('Chaqueta Trench', 'chaquetas', 'mujer', 'ropa/mujer/trench.png', 129.99),
('Zapatillas Blancas', 'zapatos', 'mujer', 'ropa/mujer/zapatillas.png', 89.99),
('Tacones Nude', 'zapatos', 'mujer', 'ropa/mujer/tacones_nude.png', 75.00);