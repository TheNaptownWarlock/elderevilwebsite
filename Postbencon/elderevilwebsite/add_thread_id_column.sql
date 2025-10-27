-- Add thread_id column to private_messages table for message threading
ALTER TABLE private_messages
ADD COLUMN IF NOT EXISTS thread_id TEXT;

-- Create an index on thread_id for faster queries
CREATE INDEX IF NOT EXISTS idx_private_messages_thread_id ON private_messages(thread_id);

-- For existing messages, set thread_id to their own id (each becomes its own thread)
UPDATE private_messages
SET thread_id = id
WHERE thread_id IS NULL;

