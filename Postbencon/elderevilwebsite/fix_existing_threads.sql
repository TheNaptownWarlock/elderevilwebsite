-- Fix existing messages to be properly threaded
-- This script groups messages between the same two users into threads

-- First, for messages that are clearly replies (have "Re:" in subject), 
-- set their thread_id to match the earliest message between those two users

WITH message_pairs AS (
  SELECT 
    pm1.id as reply_id,
    pm1.sender_email,
    pm1.recipient_email,
    pm1.created_at as reply_time,
    (
      SELECT pm2.id 
      FROM private_messages pm2
      WHERE (
        (pm2.sender_email = pm1.sender_email AND pm2.recipient_email = pm1.recipient_email)
        OR 
        (pm2.sender_email = pm1.recipient_email AND pm2.recipient_email = pm1.sender_email)
      )
      AND pm2.created_at < pm1.created_at
      ORDER BY pm2.created_at ASC
      LIMIT 1
    ) as original_message_id
  FROM private_messages pm1
  WHERE pm1.subject LIKE 'Re:%' OR pm1.subject = ''
)
UPDATE private_messages
SET thread_id = COALESCE(
  (SELECT original_message_id FROM message_pairs WHERE reply_id = private_messages.id),
  id
)
WHERE thread_id = id OR thread_id IS NULL;

-- Alternative simpler approach: Group all messages between same two users into one thread
-- Uncomment this if the above doesn't work:

/*
WITH conversation_threads AS (
  SELECT 
    id,
    sender_email,
    recipient_email,
    created_at,
    LEAST(sender_email, recipient_email) || '_' || GREATEST(sender_email, recipient_email) as conversation_key,
    MIN(created_at) OVER (
      PARTITION BY LEAST(sender_email, recipient_email) || '_' || GREATEST(sender_email, recipient_email)
    ) as first_message_time
  FROM private_messages
),
first_messages AS (
  SELECT 
    ct.conversation_key,
    pm.id as first_message_id
  FROM conversation_threads ct
  JOIN private_messages pm ON ct.sender_email = pm.sender_email 
    AND ct.recipient_email = pm.recipient_email 
    AND ct.first_message_time = pm.created_at
)
UPDATE private_messages
SET thread_id = (
  SELECT first_message_id 
  FROM first_messages fm
  WHERE fm.conversation_key = LEAST(private_messages.sender_email, private_messages.recipient_email) || '_' || GREATEST(private_messages.sender_email, private_messages.recipient_email)
);
*/

