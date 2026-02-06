CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    is_verified_seller BOOLEAN DEFAULT FALSE
);

CREATE TABLE ads (
    id SERIAL PRIMARY KEY,
    seller_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    category_id INTEGER NOT NULL,
    images_qty INTEGER DEFAULT 0
);

INSERT INTO users (name, is_verified_seller) VALUES 
('Vasya', FALSE),
('Ivan', TRUE);

INSERT INTO ads (seller_id, title, description, category_id, images_qty) VALUES 
(1, 'Phone', 'Good phone', 1, 2),
(2, 'Car', 'Fast car', 2, 5);