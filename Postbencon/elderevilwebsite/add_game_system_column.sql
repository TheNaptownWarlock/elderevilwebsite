-- Add game_system column to events table
ALTER TABLE events ADD COLUMN game_system TEXT DEFAULT 'Not specified';
