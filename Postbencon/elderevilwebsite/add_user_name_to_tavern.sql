-- Add user_name column to tavern_messages table
ALTER TABLE tavern_messages 
ADD COLUMN user_name TEXT;

-- Update existing records to populate user_name from users table
UPDATE tavern_messages 
SET user_name = users.display_name 
FROM users 
WHERE tavern_messages.user_email = users.email;

-- Set a default value for any records that didn't get updated
UPDATE tavern_messages 
SET user_name = user_email 
WHERE user_name IS NULL;