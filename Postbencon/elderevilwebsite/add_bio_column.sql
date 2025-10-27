-- Add bio column to users table
ALTER TABLE users
ADD COLUMN IF NOT EXISTS bio TEXT;

-- Update existing users to have empty bio if null
UPDATE users
SET bio = ''
WHERE bio IS NULL;



