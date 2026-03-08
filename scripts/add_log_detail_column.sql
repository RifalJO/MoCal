-- Migration: Add log_detail column to food_logs table
-- Run this if you already have an existing database

-- Add the new column
ALTER TABLE food_logs 
ADD COLUMN log_detail JSONB;

-- Verify the column was added
-- \d food_logs  (for psql)

-- Optional: Add index for faster queries on log_detail
-- CREATE INDEX idx_food_logs_log_detail ON food_logs USING GIN (log_detail);
