-- Initialize test database with sample data
-- This simulates Tejas's production database structure

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    department VARCHAR(50),
    active BOOLEAN DEFAULT true
);

CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10,2),
    status VARCHAR(20) DEFAULT 'pending'
);

-- Insert sample data
INSERT INTO users (username, email, department, active) VALUES
    ('john_doe', 'john@company.com', 'engineering', true),
    ('jane_smith', 'jane@company.com', 'marketing', true),
    ('bob_jones', 'bob@company.com', 'sales', true),
    ('alice_wilson', 'alice@company.com', 'engineering', false),
    ('charlie_brown', 'charlie@company.com', 'hr', true);

INSERT INTO orders (user_id, total_amount, status) VALUES
    (1, 299.99, 'completed'),
    (1, 149.50, 'pending'),
    (2, 89.99, 'completed'),
    (3, 459.00, 'shipped'),
    (2, 199.99, 'pending'),
    (4, 329.99, 'cancelled'),
    (5, 79.99, 'completed');

-- Create a view for testing
CREATE VIEW active_user_orders AS
SELECT 
    u.username,
    u.email,
    u.department,
    o.order_date,
    o.total_amount,
    o.status
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE u.active = true;

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO testuser;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO testuser;