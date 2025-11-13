-- Add display_name column to tavern_messages table and populate it from users table
-- This script will:
-- 1. Add a new display_name column to tavern_messages
-- 2. Populate it with the display_name from the users table
-- 3. Create an index for better performance

-- Step 1: Add the display_name column to tavern_messages table
ALTER TABLE tavern_messages 
ADD COLUMN display_name TEXT;

-- Step 2: Update all existing records to populate display_name from users table
UPDATE tavern_messages 
SET display_name = users.display_name
FROM users 
WHERE tavern_messages.user_email = users.email;

-- Step 3: Create an index on user_email for better join performance (optional but recommended)
CREATE INDEX IF NOT EXISTS idx_tavern_messages_user_email ON tavern_messages(user_email);

-- Step 4: Verify the update worked
-- SELECT 
--   tm.id,
--   tm.user_email,
--   tm.display_name,
--   tm.message,
--   tm.created_at
-- FROM tavern_messages tm
-- ORDER BY tm.created_at DESC
-- LIMIT 10;