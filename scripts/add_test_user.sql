-- Quick script to add test users to the database
-- Run this in your PostgreSQL database

-- First, let's check if the users table exists
SELECT table_name FROM information_schema.tables WHERE table_name = 'users';

-- Add a test user (password: test123)
-- The password is hashed using bcrypt
INSERT INTO users (id, email, password_hash, created_at)
VALUES (
    gen_random_uuid(),
    'test@mocal.app',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS3MebAJu', -- 'test123'
    NOW()
)
ON CONFLICT (email) DO NOTHING;

-- Verify the user was added
SELECT id, email, created_at FROM users WHERE email = 'test@mocal.app';
