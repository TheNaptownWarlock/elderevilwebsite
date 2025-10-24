-- Bencon Fantasy Calendar - Supabase Database Setup
-- Copy and paste this into Supabase SQL Editor

-- Users table
CREATE TABLE IF NOT EXISTS users (
    email VARCHAR(255) PRIMARY KEY,
    password_hash VARCHAR(255),
    display_name VARCHAR(255),
    avatar VARCHAR(50),
    pronouns VARCHAR(50),
    email_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Events table  
CREATE TABLE IF NOT EXISTS events (
    id VARCHAR(255) PRIMARY KEY,
    title VARCHAR(255),
    description TEXT,
    date VARCHAR(20),
    time VARCHAR(20),
    location VARCHAR(255),
    host_email VARCHAR(255) REFERENCES users(email),
    tags TEXT,
    seat_min INTEGER DEFAULT 1,
    seat_max INTEGER DEFAULT 1,
    max_attendees INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- RSVPs table
CREATE TABLE IF NOT EXISTS rsvps (
    id VARCHAR(255) PRIMARY KEY,
    event_id VARCHAR(255) REFERENCES events(id),
    user_email VARCHAR(255) REFERENCES users(email),
    status VARCHAR(20),
    timestamp TIMESTAMP DEFAULT NOW(),
    UNIQUE(event_id, user_email)
);

-- Tavern messages table (for real-time chat!)
CREATE TABLE IF NOT EXISTS tavern_messages (
    id VARCHAR(255) PRIMARY KEY,
    user_email VARCHAR(255) REFERENCES users(email),
    message TEXT,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Private messages table
CREATE TABLE IF NOT EXISTS private_messages (
    id VARCHAR(255) PRIMARY KEY,
    sender_email VARCHAR(255) REFERENCES users(email),
    recipient_email VARCHAR(255) REFERENCES users(email),
    message TEXT,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Enable Row Level Security (RLS) for security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE events ENABLE ROW LEVEL SECURITY;
ALTER TABLE rsvps ENABLE ROW LEVEL SECURITY;
ALTER TABLE tavern_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE private_messages ENABLE ROW LEVEL SECURITY;

-- Create policies for public access (you can make these more restrictive later)
CREATE POLICY "Public access" ON users FOR ALL USING (true);
CREATE POLICY "Public access" ON events FOR ALL USING (true);
CREATE POLICY "Public access" ON rsvps FOR ALL USING (true);
CREATE POLICY "Public access" ON tavern_messages FOR ALL USING (true);
CREATE POLICY "Public access" ON private_messages FOR ALL USING (true);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_events_date ON events(date);
CREATE INDEX IF NOT EXISTS idx_rsvps_event ON rsvps(event_id);
CREATE INDEX IF NOT EXISTS idx_tavern_time ON tavern_messages(timestamp);

-- Insert some sample data to test
INSERT INTO users (email, password_hash, display_name, avatar, pronouns) VALUES
('admin@bencon.com', 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'Tavern Keeper', '🍺', 'they/them')
ON CONFLICT (email) DO NOTHING;

INSERT INTO tavern_messages (id, user_email, message) VALUES  
('welcome-msg', 'admin@bencon.com', '🏰 Welcome to the Bencon Tavern! Share your adventures here! 🍺')
ON CONFLICT (id) DO NOTHING;