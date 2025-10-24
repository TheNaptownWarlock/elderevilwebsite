#!/usr/bin/env python3
"""
Quick test to verify Supabase connection
"""

import streamlit as st
from supabase import create_client

def main():
    st.title("Quick Supabase Test")
    
    # Get credentials
    SUPABASE_URL = st.secrets.get("SUPABASE_URL")
    SUPABASE_KEY = st.secrets.get("SUPABASE_KEY")
    
    st.write(f"URL: {SUPABASE_URL}")
    if SUPABASE_KEY:
        st.write(f"Key: {SUPABASE_KEY[:20]}...")
    else:
        st.write("Key: None")
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        st.error("❌ Credentials not found")
        st.write("Available secrets keys:", list(st.secrets.keys()))
        return
    
    try:
        # Test connection
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Try to read from tavern_messages
        result = supabase.table('tavern_messages').select('*').limit(1).execute()
        
        st.success("✅ Connection successful!")
        st.write(f"Found {len(result.data)} messages")
        
        # Show the simple chat
        st.subheader("Simple Chat")
        from simple_chat import render_simple_chat
        render_simple_chat("test@example.com", "Test User")
        
    except Exception as e:
        st.error(f"❌ Error: {e}")
        
        if "relation \"tavern_messages\" does not exist" in str(e):
            st.warning("⚠️ Table doesn't exist. You need to create it in Supabase dashboard.")
            st.code("""
CREATE TABLE tavern_messages (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_email TEXT,
    message TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE tavern_messages ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public access" ON tavern_messages FOR ALL USING (true);
            """)

if __name__ == "__main__":
    main()
