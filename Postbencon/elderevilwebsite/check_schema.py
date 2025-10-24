#!/usr/bin/env python3
"""
Check the database schema to see what columns exist
"""

import streamlit as st
from supabase import create_client

def main():
    st.title("Database Schema Check")
    
    # Get credentials
    SUPABASE_URL = st.secrets.get("SUPABASE_URL")
    SUPABASE_KEY = st.secrets.get("SUPABASE_KEY")
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        st.error("❌ Credentials not found")
        return
    
    try:
        # Create client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Try to get table info
        st.write("Checking tavern_messages table...")
        
        # Try to insert a test message to see what error we get
        test_message = {
            "user_email": "test@example.com",
            "message": "Test message",
            "created_at": "2024-01-01T00:00:00Z"
        }
        
        st.write("Test message data:")
        st.json(test_message)
        
        try:
            result = supabase.table('tavern_messages').insert([test_message]).execute()
            st.success("✅ Test message inserted successfully!")
            st.write("Result:", result)
        except Exception as e:
            st.error(f"❌ Insert failed: {e}")
            
            # Try to get table info
            try:
                # Try to describe the table structure
                st.write("Trying to get table structure...")
                
                # Try a simple select to see what columns exist
                result = supabase.table('tavern_messages').select('*').limit(1).execute()
                if result.data:
                    st.write("Sample data structure:")
                    st.json(result.data[0])
                    
                    st.write("Available columns:")
                    for key in result.data[0].keys():
                        st.write(f"- {key}: {type(result.data[0][key]).__name__}")
                else:
                    st.write("No data in table")
                    
            except Exception as e2:
                st.error(f"❌ Could not get table info: {e2}")
        
        # Try different column names
        st.write("\nTrying different column combinations...")
        
        test_variations = [
            {"user_email": "test@example.com", "message": "Test 1"},
            {"user_email": "test@example.com", "message": "Test 2", "timestamp": "2024-01-01T00:00:00Z"},
            {"email": "test@example.com", "message": "Test 3"},
            {"username": "test@example.com", "message": "Test 4"},
        ]
        
        for i, test_data in enumerate(test_variations):
            try:
                result = supabase.table('tavern_messages').insert([test_data]).execute()
                st.success(f"✅ Variation {i+1} worked: {test_data}")
                break
            except Exception as e:
                st.write(f"❌ Variation {i+1} failed: {e}")
        
    except Exception as e:
        st.error(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    main()


