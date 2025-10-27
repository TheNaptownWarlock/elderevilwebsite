-- Simple fix for existing message threads
-- Groups all messages between the same two users into one thread
-- The thread_id will be the ID of the earliest message between them

UPDATE private_messages pm1
SET thread_id = (
  SELECT MIN(pm2.id)
  FROM private_messages pm2
  WHERE (
    -- Messages where pm1 and pm2 involve the same two people
    (pm2.sender_email = pm1.sender_email AND pm2.recipient_email = pm1.recipient_email)
    OR 
    (pm2.sender_email = pm1.recipient_email AND pm2.recipient_email = pm1.sender_email)
  )
  AND pm2.created_at <= pm1.created_at
  ORDER BY pm2.created_at ASC
  LIMIT 1
);

-- Verify the fix
SELECT 
  id,
  thread_id,
  sender_email,
  recipient_email,
  LEFT(message, 50) as message_preview,
  created_at
FROM private_messages
ORDER BY thread_id, created_at;

