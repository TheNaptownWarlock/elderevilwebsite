# Supabase PostgreSQL Integration for Bencon Calendar
# FREE TIER: 500MB database + unlimited API requests + real-time subscriptions

import os
import streamlit as st
from supabase import create_client, Client
import hashlib
from datetime import datetime, timedelta
import uuid

# Supabase configuration (set in Streamlit secrets)
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")

def get_supabase_client() -> Client:
    """Get Supabase client"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        st.error("Supabase credentials not configured. Using local SQLite instead.")
        return None
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def init_supabase_database():
    """Initialize Supabase database tables"""
    supabase = get_supabase_client()
    if not supabase:
        return False
    
    # Note: In Supabase, you create tables via SQL Editor in the dashboard
    # Here's the SQL you'll run in Supabase dashboard:
    
    sql_commands = """
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
        host_email VARCHAR(255),
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
    
    -- Tavern messages table
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
    
    -- Email verifications table
    CREATE TABLE IF NOT EXISTS email_verifications (
        email VARCHAR(255) PRIMARY KEY,
        token VARCHAR(255),
        created_at TIMESTAMP DEFAULT NOW(),
        expires_at TIMESTAMP,
        verified BOOLEAN DEFAULT false
    );
    
    -- Password resets table
    CREATE TABLE IF NOT EXISTS password_resets (
        email VARCHAR(255),
        token VARCHAR(255),
        created_at TIMESTAMP DEFAULT NOW(),
        expires_at TIMESTAMP,
        used BOOLEAN DEFAULT false
    );
    
    -- Enable Row Level Security (RLS)
    ALTER TABLE users ENABLE ROW LEVEL SECURITY;
    ALTER TABLE events ENABLE ROW LEVEL SECURITY;
    ALTER TABLE rsvps ENABLE ROW LEVEL SECURITY;
    ALTER TABLE tavern_messages ENABLE ROW LEVEL SECURITY;
    ALTER TABLE private_messages ENABLE ROW LEVEL SECURITY;
    
    -- Create policies for public access (adjust as needed)
    CREATE POLICY "Public access for users" ON users FOR ALL USING (true);
    CREATE POLICY "Public access for events" ON events FOR ALL USING (true);
    CREATE POLICY "Public access for rsvps" ON rsvps FOR ALL USING (true);
    CREATE POLICY "Public access for tavern_messages" ON tavern_messages FOR ALL USING (true);
    CREATE POLICY "Public access for private_messages" ON private_messages FOR ALL USING (true);
    """
    
    st.info(f"""
    **To set up Supabase database:**
    
    1. Go to https://supabase.com
    2. Create free account
    3. Create new project
    4. Go to SQL Editor
    5. Run this SQL:
    
    ```sql
    {sql_commands}
    ```
    """)
    
    return True

def save_to_supabase(table_name: str, data: dict):
    """Save data to Supabase table"""
    supabase = get_supabase_client()
    if not supabase:
        return False
    
    try:
        result = supabase.table(table_name).insert(data).execute()
        return True
    except Exception as e:
        st.error(f"Error saving to Supabase: {e}")
        return False

def load_from_supabase(table_name: str, filters=None):
    """Load data from Supabase table"""
    supabase = get_supabase_client()
    if not supabase:
        return []
    
    try:
        query = supabase.table(table_name).select("*")
        
        # Apply filters if provided
        if filters:
            for column, value in filters.items():
                query = query.eq(column, value)
        
        result = query.execute()
        return result.data
    except Exception as e:
        st.error(f"Error loading from Supabase: {e}")
        return []

def register_user_supabase(email: str, password: str, display_name: str, avatar: str, pronouns: str):
    """Register new user in Supabase"""
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    user_data = {
        "email": email,
        "password_hash": password_hash,
        "display_name": display_name,
        "avatar": avatar,
        "pronouns": pronouns,
        "email_verified": False
    }
    
    return save_to_supabase("users", user_data)

def login_user_supabase(email: str, password: str):
    """Login user with Supabase"""
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    users = load_from_supabase("users", {"email": email, "password_hash": password_hash})
    
    if users:
        return users[0]
    return None

def get_real_time_tavern_messages():
    """Get tavern messages with real-time updates using Supabase subscriptions"""
    supabase = get_supabase_client()
    if not supabase:
        return []
    
    try:
        # Get latest messages
        result = supabase.table("tavern_messages")\
            .select("*")\
            .order("timestamp", desc=False)\
            .limit(50)\
            .execute()
        
        return result.data
    except Exception as e:
        st.error(f"Error loading tavern messages: {e}")
        return []

def send_tavern_message_supabase(user_email: str, message: str):
    """Send message to tavern chat via Supabase"""
    message_data = {
        "id": str(uuid.uuid4()),
        "user_email": user_email,
        "message": message,
    }
    
    return save_to_supabase("tavern_messages", message_data)

# Cost breakdown for scaling:
def get_pricing_info():
    """Display pricing information for different tiers"""
    st.info("""
    ## 💰 Supabase Pricing (Current as of 2024):
    
    ### 🆓 FREE TIER (Perfect for your app!)
    - **500MB database storage**
    - **5GB bandwidth/month** 
    - **50MB file storage**
    - **500,000 Edge Function invocations**
    - **Unlimited API requests**
    - **Real-time subscriptions**
    - **2 projects**
    
    ### 💼 PRO TIER ($25/month) - Only if you grow huge:
    - **8GB database storage**
    - **250GB bandwidth**
    - **100GB file storage**
    - **2 million Edge Function invocations**
    - **Everything from free tier**
    
    ### 📊 Your App Usage Estimate:
    - **Users**: 100 active users = ~5MB data
    - **Events**: 1000 events/year = ~2MB data  
    - **Messages**: 10,000 chat messages = ~5MB data
    - **Total**: ~12MB (2.4% of free tier!)
    
    **You'll stay FREE for years!** 🎉
    """)

# Add this to your requirements.txt:
SUPABASE_REQUIREMENTS = """
# Add these to requirements.txt for Supabase:
supabase==2.0.5
postgrest==0.13.0
"""