#!/usr/bin/env python3
"""
Set up the Supabase database tables for the simple chat
"""

import streamlit as st
from supabase import create_client, Client

def setup_database():
    """Set up the database tables"""
    
    # Get Supabase credentials
    SUPABASE_URL = st.secrets.get("SUPABASE_URL")
    SUPABASE_KEY = st.secrets.get("SUPABASE_KEY")
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        st.error("Supabase credentials not found in secrets.toml")
        return False
    
    try:
        # Create Supabase client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        st.info("Setting up database tables...")
        
        # SQL commands to create tables
        sql_commands = """
        -- Create tavern_messages table
        CREATE TABLE IF NOT EXISTS tavern_messages (
            id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
            user_email TEXT,
            message TEXT NOT NULL,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        
        -- Create index for better performance
        CREATE INDEX IF NOT EXISTS idx_tavern_messages_created_at ON tavern_messages(created_at);
        
        -- Enable Row Level Security
        ALTER TABLE tavern_messages ENABLE ROW LEVEL SECURITY;
        
        -- Create policy for public access
        CREATE POLICY IF NOT EXISTS "Public access for tavern_messages" ON tavern_messages FOR ALL USING (true);
        """
        
        # Execute the SQL commands
        result = supabase.rpc('exec_sql', {'sql': sql_commands})
        
        st.success("✅ Database tables created successfully!")
        st.info("You can now test the chat functionality.")
        
        return True
        
    except Exception as e:
        st.error(f"❌ Error setting up database: {e}")
        st.info("You may need to run the SQL commands manually in your Supabase dashboard.")
        return False

if __name__ == "__main__":
    st.title("Database Setup")
    setup_database()


