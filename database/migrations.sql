-- ── Create Database ──────────────────────────────
CREATE DATABASE IF NOT EXISTS ai_sales_agent;
USE ai_sales_agent;

-- ── Drop tables in reverse FK order ──────────────
DROP TABLE IF EXISTS followups;
DROP TABLE IF EXISTS conversations;
DROP TABLE IF EXISTS leads;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;

-- ── Customers ─────────────────────────────────────
CREATE TABLE customers (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(255),
    phone       VARCHAR(50) UNIQUE,
    email       VARCHAR(255),
    channel     ENUM('whatsapp','instagram','web') DEFAULT 'web',
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── Products ──────────────────────────────────────
CREATE TABLE products (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(255) NOT NULL,
    category        VARCHAR(100),
    description     TEXT,
    price           DECIMAL(10, 2) NOT NULL,
    stock           INT DEFAULT 0,
    min_price       DECIMAL(10, 2),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── Orders ────────────────────────────────────────
CREATE TABLE orders (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    customer_id     INT,
    product_id      INT,
    quantity        INT DEFAULT 1,
    total_price     DECIMAL(10, 2),
    status          ENUM('pending','confirmed','shipped','delivered','cancelled') DEFAULT 'pending',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (product_id)  REFERENCES products(id)
);

-- ── Leads ─────────────────────────────────────────
CREATE TABLE leads (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    customer_id     INT,
    interest        TEXT,
    status          ENUM('new','contacted','converted','lost') DEFAULT 'new',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- ── Conversations ─────────────────────────────────
CREATE TABLE conversations (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    customer_id     INT,
    role            ENUM('user','assistant') NOT NULL,
    message         TEXT NOT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- ── Follow-ups ────────────────────────────────────
CREATE TABLE followups (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    customer_id     INT,
    message         TEXT,
    scheduled_at    DATETIME,
    sent            BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- ── Seed Sample Products ──────────────────────────
INSERT INTO products (name, category, description, price, stock, min_price) VALUES
('iPhone 15 Pro',       'Smartphones',  'Apple iPhone 15 Pro 256GB',        1199.00, 50,  999.00),
('Samsung Galaxy S24',  'Smartphones',  'Samsung Galaxy S24 128GB',          999.00, 40,  849.00),
('MacBook Air M3',      'Laptops',      'Apple MacBook Air 13-inch M3 chip', 1299.00, 30, 1099.00),
('Sony WH-1000XM5',    'Headphones',   'Sony Noise Cancelling Headphones',   349.00, 60,  279.00),
('iPad Pro 12.9',       'Tablets',      'Apple iPad Pro 12.9-inch M2',       1099.00, 25,  899.00);

SELECT CONCAT('✅ Products seeded: ', COUNT(*), ' rows') AS status FROM products;