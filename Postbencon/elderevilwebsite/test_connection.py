#!/usr/bin/env python3
"""
Test the Supabase connection and simple chat
"""

import streamlit as st
from supabase import create_client, Client

def test_connection():
    """Test the Supabase connection"""
    
    st.title("Supabase Connection Test")
    
    # Get credentials
    SUPABASE_URL = st.secrets.get("SUPABASE_URL")
    SUPABASE_KEY = st.secrets.get("SUPABASE_KEY")
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        st.error("❌ Supabase credentials not found")
        return
    
    st.info(f"Testing connection to: {SUPABASE_URL}")
    
    try:
        # Create client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Test connection by trying to read from tavern_messages
        result = supabase.table('tavern_messages').select('*').limit(1).execute()
        
        st.success("✅ Connection successful!")
        st.info(f"Found {len(result.data)} messages in tavern_messages table")
        
        # Show the simple chat
        st.subheader("Simple Chat Test")
        
        from simple_chat import render_simple_chat
        render_simple_chat("test@example.com", "Test User")
        
    except Exception as e:
        st.error(f"❌ Connection failed: {e}")
        
        if "relation \"tavern_messages\" does not exist" in str(e):
            st.warning("⚠️ The tavern_messages table doesn't exist yet.")
            st.info("You need to create the table first. Go to your Supabase dashboard > SQL Editor and run:")
            st.code("""
CREATE TABLE tavern_messages (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_email TEXT,
    message TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_tavern_messages_created_at ON tavern_messages(created_at);
ALTER TABLE tavern_messages ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public access for tavern_messages" ON tavern_messages FOR ALL USING (true);
            """)

if __name__ == "__main__":
    test_connection()


