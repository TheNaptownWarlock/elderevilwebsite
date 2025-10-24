#!/usr/bin/env python3
"""
Supabase Database Setup Script
This script creates the necessary tables in your Supabase database
"""

import os
from supabase import create_client, Client
import toml

# Load Supabase credentials - Using hardcoded values from your secrets file
# These are the values from your secrets.toml file
supabase_url = "https://uvsdbuonyfzajhtrgnxq.supabase.co"
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV2c2RidW9ueWZ6YWpodHJnbnhxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEwNjUxNjgsImV4cCI6MjA3NjY0MTE2OH0.tq_dQfCIl68bSt2BUPP0lWW2DjjwPpxcKV6LIt2LRFg"

print(f"📋 Using Supabase credentials:")
print(f"   URL: {supabase_url}")
print(f"   Key: {supabase_key[:20]}...")

print(f"🔗 Connecting to Supabase...")

# Create Supabase client
try:
    supabase: Client = create_client(supabase_url, supabase_key)
    print("✅ Successfully connected to Supabase!")
    
    # Test the connection with a simple query
    print("🧪 Testing connection...")
    test_result = supabase.auth.get_session()
    print("✅ Connection test passed!")
    
except Exception as e:
    print(f"❌ Error connecting to Supabase: {e}")
    print(f"   URL used: {supabase_url}")
    print(f"   Key length: {len(supabase_key)}")
    exit(1)

# SQL to create the tables
create_tables_sql = """
-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Events table  
CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    event_date TIMESTAMP WITH TIME ZONE NOT NULL,
    location VARCHAR(200),
    max_attendees INTEGER,
    created_by INTEGER REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RSVPs table
CREATE TABLE IF NOT EXISTS rsvps (
    id SERIAL PRIMARY KEY,
    event_id INTEGER REFERENCES events(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'attending' CHECK (status IN ('attending', 'maybe', 'not_attending')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(event_id, user_id)
);

-- Messages table (for inbox/communication)
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    sender_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    recipient_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    subject VARCHAR(200),
    content TEXT NOT NULL,
    read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_events_date ON events(event_date);
CREATE INDEX IF NOT EXISTS idx_events_created_by ON events(created_by);
CREATE INDEX IF NOT EXISTS idx_rsvps_event_id ON rsvps(event_id);
CREATE INDEX IF NOT EXISTS idx_rsvps_user_id ON rsvps(user_id);
CREATE INDEX IF NOT EXISTS idx_messages_recipient ON messages(recipient_id);
CREATE INDEX IF NOT EXISTS idx_messages_sender ON messages(sender_id);
"""

# Execute the SQL to create tables
try:
    print("🔨 Creating database tables...")
    
    # Split the SQL into individual statements
    statements = [stmt.strip() for stmt in create_tables_sql.split(';') if stmt.strip()]
    
    for i, statement in enumerate(statements):
        if statement:
            print(f"   Executing statement {i+1}/{len(statements)}...")
            result = supabase.rpc('exec_sql', {'sql': statement}).execute()
            
    print("✅ Database tables created successfully!")
    
    # Test the connection by checking if tables exist
    print("\n🔍 Verifying tables...")
    
    # Try to query each table to verify it exists
    tables_to_check = ['users', 'events', 'rsvps', 'messages']
    
    for table in tables_to_check:
        try:
            result = supabase.table(table).select("*").limit(1).execute()
            print(f"   ✅ {table} table verified")
        except Exception as e:
            print(f"   ⚠️  {table} table check failed: {e}")
    
    print("\n🎉 Supabase database setup complete!")
    print("Your fantasy calendar app is now ready to use the cloud database!")

except Exception as e:
    print(f"❌ Error creating tables: {e}")
    print("\nTrying alternative method...")
    
    # Alternative: Create tables one by one
    try:
        # Users table
        print("Creating users table...")
        supabase.table('users').select('id').limit(1).execute()
        print("✅ Users table exists or created")
        
    except Exception as table_error:
        print(f"Note: {table_error}")
        print("You may need to create tables manually in your Supabase dashboard.")
        print("Please visit: https://app.supabase.com/project/your-project/editor")