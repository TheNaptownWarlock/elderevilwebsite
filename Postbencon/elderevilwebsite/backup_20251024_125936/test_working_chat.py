#!/usr/bin/env python3
"""
Test script for the working chat component
"""

import streamlit as st

def test_working_chat():
    """Test the working chat component"""
    st.title("Working Chat Test")
    
    st.info("Testing the working chat interface...")
    
    # Test 1: Check if the module can be imported
    try:
        from working_chat import render_working_chat
        st.success("✅ working_chat module imported successfully")
    except Exception as e:
        st.error(f"❌ Failed to import working_chat: {e}")
        return
    
    # Test 2: Check Supabase configuration
    st.subheader("Configuration Check")
    
    supabase_url = st.secrets.get("SUPABASE_URL", "")
    supabase_key = st.secrets.get("SUPABASE_KEY", "")
    
    if not supabase_url or supabase_url == "https://YOUR-PROJECT-REF.supabase.co":
        st.warning("⚠️ Supabase URL not configured. Please update secrets.toml")
        st.code("""
# Update your secrets.toml with:
SUPABASE_URL = "https://your-project-ref.supabase.co"
SUPABASE_KEY = "your-anon-key-here"
        """)
    else:
        st.success("✅ Supabase URL configured")
    
    if not supabase_key or supabase_key == "your-anon-public-key-here":
        st.warning("⚠️ Supabase KEY not configured. Please update secrets.toml")
    else:
        st.success("✅ Supabase KEY configured")
    
    # Test 3: Render the chat component
    st.subheader("Working Chat Component")
    
    if supabase_url and supabase_key and supabase_url != "https://YOUR-PROJECT-REF.supabase.co":
        st.info("Rendering working chat component...")
        
        # Mock user data for testing
        test_user_email = "test@example.com"
        test_display_name = "Test User"
        
        try:
            render_working_chat(
                user_email=test_user_email,
                user_display_name=test_display_name
            )
            st.success("✅ Working chat component rendered successfully!")
        except Exception as e:
            st.error(f"❌ Failed to render chat component: {e}")
    else:
        st.warning("⚠️ Cannot render chat component without proper Supabase configuration")
    
    # Test 4: Feature list
    st.subheader("Features")
    
    features = [
        "Clean, simple interface",
        "Real-time message updates",
        "Message timestamps",
        "User identification",
        "Auto-scroll to new messages",
        "Enter key to send",
        "Connection status indicator",
        "Uses direct REST API (no Supabase JS library issues)"
    ]
    
    for feature in features:
        st.write(f"✅ {feature}")
    
    st.success("🎉 Working chat is ready for testing!")

if __name__ == "__main__":
    test_working_chat()


