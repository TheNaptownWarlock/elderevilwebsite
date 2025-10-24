"""
Create Supabase Tables via SQL
This script creates the database tables in your Supabase project
"""

# SQL Commands to create tables in Supabase
# Run these commands in your Supabase SQL Editor at:
# https://app.supabase.com/project/uvsdbuonyfzajhtrgnxq/sql

CREATE_TABLES_SQL = """
-- Users table
CREATE TABLE IF NOT EXISTS users (
    email TEXT PRIMARY KEY,
    password_hash TEXT NOT NULL,
    display_name TEXT,
    avatar TEXT,
    pronouns TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Events table
CREATE TABLE IF NOT EXISTS events (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    location TEXT,
    host_email TEXT REFERENCES users(email),
    tags TEXT,
    max_attendees INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add new columns to events if they don't exist
DO $$ 
BEGIN 
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                  WHERE table_name = 'events' AND column_name = 'seat_min') THEN
        ALTER TABLE events ADD COLUMN seat_min INTEGER DEFAULT 1;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                  WHERE table_name = 'events' AND column_name = 'seat_max') THEN
        ALTER TABLE events ADD COLUMN seat_max INTEGER DEFAULT 1;
    END IF;
END $$;

-- RSVPs table
CREATE TABLE IF NOT EXISTS rsvps (
    id TEXT PRIMARY KEY,
    event_id TEXT REFERENCES events(id) ON DELETE CASCADE,
    user_email TEXT REFERENCES users(email),
    status TEXT DEFAULT 'yes',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(event_id, user_email)
);

-- Tavern messages table
CREATE TABLE IF NOT EXISTS tavern_messages (
    id TEXT PRIMARY KEY,
    user_email TEXT REFERENCES users(email),
    message TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Private messages table
CREATE TABLE IF NOT EXISTS private_messages (
    id TEXT PRIMARY KEY,
    sender_email TEXT REFERENCES users(email),
    recipient_email TEXT REFERENCES users(email),
    subject TEXT,
    message TEXT NOT NULL,
    read_status INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_events_date ON events(date);
CREATE INDEX IF NOT EXISTS idx_events_host ON events(host_email);
CREATE INDEX IF NOT EXISTS idx_rsvps_event ON rsvps(event_id);
CREATE INDEX IF NOT EXISTS idx_rsvps_user ON rsvps(user_email);
CREATE INDEX IF NOT EXISTS idx_messages_recipient ON private_messages(recipient_email);
CREATE INDEX IF NOT EXISTS idx_tavern_user ON tavern_messages(user_email);
"""

print("🎯 SUPABASE TABLE SETUP INSTRUCTIONS")
print("=" * 50)
print("1. Go to: https://app.supabase.com/project/uvsdbuonyfzajhtrgnxq/sql")
print("2. Copy and paste the SQL commands below:")
print("3. Click 'Run' to create all tables")
print("=" * 50)
print()
print(CREATE_TABLES_SQL)
print("=" * 50)
print("✅ Once you run this SQL, your fantasy calendar will be ready to use Supabase!")