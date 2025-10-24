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
    seat_min INTEGER DEFAULT 1,
    seat_max INTEGER DEFAULT 1,
    max_attendees INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

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

-- Typing status table for real-time typing indicators
CREATE TABLE IF NOT EXISTS typing_status (
    user_email TEXT PRIMARY KEY REFERENCES users(email),
    is_typing BOOLEAN DEFAULT false,
    last_seen TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Message reactions table for emoji reactions
CREATE TABLE IF NOT EXISTS message_reactions (
    id TEXT PRIMARY KEY,
    message_id TEXT REFERENCES tavern_messages(id) ON DELETE CASCADE,
    user_email TEXT REFERENCES users(email),
    emoji TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(message_id, user_email, emoji)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_events_date ON events(date);
CREATE INDEX IF NOT EXISTS idx_events_host ON events(host_email);
CREATE INDEX IF NOT EXISTS idx_rsvps_event ON rsvps(event_id);
CREATE INDEX IF NOT EXISTS idx_rsvps_user ON rsvps(user_email);
CREATE INDEX IF NOT EXISTS idx_messages_recipient ON private_messages(recipient_email);
CREATE INDEX IF NOT EXISTS idx_tavern_user ON tavern_messages(user_email);
CREATE INDEX IF NOT EXISTS idx_typing_status ON typing_status(is_typing, updated_at);
CREATE INDEX IF NOT EXISTS idx_reactions_message ON message_reactions(message_id);
CREATE INDEX IF NOT EXISTS idx_reactions_user ON message_reactions(user_email);