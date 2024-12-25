-- Insert Sample Users
-- Passwords are assumed to be hashed (e.g., using bcrypt)
INSERT INTO users (username, password, created_at) VALUES 
('john_doe', '$2b$12$abcdefghijABCDEFGHIJ/uvwxyzUVWXYZ1234567890abcdefghi', NOW()), -- bcrypt hash for "password123"
('jane_doe', '$2b$12$1234567890ABCDEFGHIJabcdefghij/uvwxyzUVWXYZabcdefghi', NOW()); -- bcrypt hash for "securepassword"

-- Insert Sample Products
INSERT INTO products (name, price, created_at) VALUES
('Laptop', 799.99, NOW()),
('Smartphone', 499.99, NOW()),
('Tablet', 299.99, NOW());

-- Insert Sample Orders
-- User IDs must match those in the 'users' table
INSERT INTO orders (user_id, total_amount, created_at) VALUES
(1, 1299.98, NOW()), -- Order by john_doe
(2, 499.99, NOW());  -- Order by jane_doe

-- Insert Sample Order Items
-- Order IDs and Product IDs must match those in 'orders' and 'products'
INSERT INTO order_items (order_id, product_id, quantity, created_at) VALUES
(1, 1, 1, NOW()), -- Laptop in order 1
(1, 2, 1, NOW()), -- Smartphone in order 1
(2, 2, 1, NOW()); -- Smartphone in order 2

-- Insert Sample Cart Items
-- User IDs and Product IDs must match those in 'users' and 'products'
INSERT INTO cart_items (user_id, product_id, quantity, created_at) VALUES
(1, 3, 2, NOW()), -- 2 Tablets in john_doe's cart
(2, 1, 1, NOW()); -- 1 Laptop in jane_doe's cart
