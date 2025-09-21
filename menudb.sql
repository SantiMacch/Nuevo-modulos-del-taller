-- Crear la base de datos (si no existe)
CREATE DATABASE IF NOT EXISTS Taller_Mecanico;
USE Taller_Mecanico;

-- Tabla persona (para clientes y empleados)
CREATE TABLE IF NOT EXISTS persona (
    dni INT PRIMARY KEY,
    apellido VARCHAR(50) NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    direccion VARCHAR(100),
    tele_contac VARCHAR(20)
);

-- Tabla cliente
CREATE TABLE IF NOT EXISTS cliente (
    cod_cliente INT AUTO_INCREMENT PRIMARY KEY,
    dni INT,
    FOREIGN KEY (dni) REFERENCES persona(dni)
);

-- Tabla proveedor
CREATE TABLE IF NOT EXISTS proveedor (
    cod_proveedor INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    cuit VARCHAR(20) UNIQUE,
    direccion VARCHAR(100),
    telefono VARCHAR(20)
);

-- Tabla repuesto
CREATE TABLE IF NOT EXISTS repuesto (
    cod_repuesto INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    stock INT DEFAULT 0,
    precio DECIMAL(10, 2) NOT NULL
);

-- Tabla empleado
CREATE TABLE IF NOT EXISTS empleado (
    cod_empleado INT AUTO_INCREMENT PRIMARY KEY,
    dni INT,
    puesto VARCHAR(50),
    FOREIGN KEY (dni) REFERENCES persona(dni)
);

-- Tabla detalle_usuario (para el login)
CREATE TABLE IF NOT EXISTS detalle_usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(50) NOT NULL UNIQUE,
    contrasena VARCHAR(100) NOT NULL,
    rol VARCHAR(20)
);

-- Tabla ficha_tecnica (opcional, para registrar vehículos)
CREATE TABLE IF NOT EXISTS ficha_tecnica (
    cod_ficha INT AUTO_INCREMENT PRIMARY KEY,
    patente VARCHAR(20) UNIQUE,
    marca VARCHAR(50),
    modelo VARCHAR(50),
    ano INT,
    dni_cliente INT,
    FOREIGN KEY (dni_cliente) REFERENCES cliente(dni)
);

-- Tabla presupuesto (opcional, para registrar presupuestos)
CREATE TABLE IF NOT EXISTS presupuesto (
    cod_presupuesto INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATE,
    total DECIMAL(10, 2),
    dni_cliente INT,
    cod_ficha INT,
    FOREIGN KEY (dni_cliente) REFERENCES cliente(dni),
    FOREIGN KEY (cod_ficha) REFERENCES ficha_tecnica(cod_ficha)
);

-- Insertar datos de prueba para persona y cliente
INSERT INTO persona (dni, apellido, nombre, direccion, tele_contac)
VALUES
(12345678, 'Pérez', 'Juan', 'Calle Falsa 123', '1122334455'),
(23456789, 'Gómez', 'María', 'Av. Siempre Viva 456', '1133445566'),
(34567890, 'López', 'Carlos', 'Calle Principal 789', '1144556677');

INSERT INTO cliente (dni)
VALUES
(12345678),
(23456789),
(34567890);

-- Insertar datos de prueba para proveedor
INSERT INTO proveedor (nombre, cuit, direccion, telefono)
VALUES
('Proveedor A', '30-12345678-9', 'Calle Comercial 123', '4123-4567'),
('Proveedor B', '30-23456789-0', 'Av. Industrial 456', '4234-5678');

-- Insertar datos de prueba para repuesto
INSERT INTO repuesto (nombre, stock, precio)
VALUES
('Filtro de aceite', 50, 1500.00),
('Pastillas de freno', 30, 3200.00),
('Batería', 15, 12500.00),
('Amortiguador', 20, 8700.00);

-- Insertar datos de prueba para empleado
INSERT INTO persona (dni, apellido, nombre, direccion, tele_contac)
VALUES
(45678901, 'García', 'Ana', 'Calle Laboral 123', '1155667788'),
(56789012, 'Rodríguez', 'Luis', 'Av. Trabajadores 456', '1166778899');

INSERT INTO empleado (dni, puesto)
VALUES
(45678901, 'Mecánico'),
(56789012, 'Administrativo');

-- Insertar un usuario de prueba para el login
INSERT INTO detalle_usuario (usuario, contrasena, rol)
VALUES
('admin', '1234', 'administrador'),
('mecanico', '5678', 'mecanico');
