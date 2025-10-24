-- Add end_time column to events table
ALTER TABLE events ADD COLUMN IF NOT EXISTS end_time TEXT;

