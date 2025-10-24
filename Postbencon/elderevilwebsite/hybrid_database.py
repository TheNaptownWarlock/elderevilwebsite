# Hybrid Database Manager - Works with both SQLite (local) and Supabase (cloud)

import os
import streamlit as st
import sqlite3
import hashlib
from datetime import datetime, timedelta
import uuid

# Check if we're running locally or on Streamlit Cloud
IS_LOCAL = not st.secrets.get("SUPABASE_URL", "")

if not IS_LOCAL:
    try:
        from supabase import create_client, Client
        SUPABASE_URL = st.secrets["SUPABASE_URL"]
        SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except:
        IS_LOCAL = True
        st.warning("Supabase not configured, using local SQLite")

# Local SQLite setup
DB_FILE = "bencon_calendar.db"

def init_hybrid_database():
    """Initialize database (SQLite locally, Supabase in cloud)"""
    if IS_LOCAL:
        return init_sqlite_database()
    else:
        return init_supabase_database()

def init_sqlite_database():
    """Initialize SQLite database (your existing function)"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create all your existing tables...
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        email TEXT PRIMARY KEY,
        password_hash TEXT,
        display_name TEXT,
        avatar TEXT,
        pronouns TEXT,
        email_verified BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS events (
        id TEXT PRIMARY KEY,
        title TEXT,
        description TEXT,
        date TEXT,
        time TEXT,
        location TEXT,
        host_email TEXT,
        tags TEXT,
        max_attendees INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS rsvps (
        id TEXT PRIMARY KEY,
        event_id TEXT,
        user_email TEXT,
        status TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(event_id, user_email)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tavern_messages (
        id TEXT PRIMARY KEY,
        user_email TEXT,
        message TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS private_messages (
        id TEXT PRIMARY KEY,
        sender_email TEXT,
        recipient_email TEXT,
        message TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()
    return True

def init_supabase_database():
    """Initialize Supabase database"""
    # Tables are created in Supabase dashboard
    return True

def save_to_database(table_name: str, data: dict):
    """Save data to database (hybrid)"""
    if IS_LOCAL:
        return save_to_sqlite(table_name, data)
    else:
        return save_to_supabase(table_name, data)

def save_to_sqlite(table_name: str, data: dict):
    """Save to SQLite (your existing function)"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        if table_name == "users":
            cursor.execute('''
            INSERT OR REPLACE INTO users (email, password_hash, display_name, avatar, pronouns, email_verified)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (data["email"], data["password_hash"], data["display_name"], 
                 data["avatar"], data["pronouns"], data.get("email_verified", False)))
            
        elif table_name == "events":
            cursor.execute('''
            INSERT OR REPLACE INTO events (id, title, description, date, time, location, host_email, tags, max_attendees)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (data["id"], data["title"], data["description"], data["date"],
                 data["time"], data["location"], data["host_email"], data["tags"], data["max_attendees"]))
            
        elif table_name == "rsvps":
            cursor.execute('''
            INSERT OR REPLACE INTO rsvps (id, event_id, user_email, status)
            VALUES (?, ?, ?, ?)
            ''', (data["id"], data["event_id"], data["user_email"], data["status"]))
            
        elif table_name == "tavern_messages":
            cursor.execute('''
            INSERT INTO tavern_messages (id, user_email, message)
            VALUES (?, ?, ?)
            ''', (data["id"], data["user_email"], data["message"]))
            
        elif table_name == "private_messages":
            cursor.execute('''
            INSERT INTO private_messages (id, sender_email, recipient_email, message)
            VALUES (?, ?, ?, ?)
            ''', (data["id"], data["sender_email"], data["recipient_email"], data["message"]))
        
        conn.commit()
        return True
        
    except Exception as e:
        st.error(f"SQLite error: {e}")
        return False
    finally:
        conn.close()

def save_to_supabase(table_name: str, data: dict):
    """Save to Supabase"""
    try:
        result = supabase_client.table(table_name).insert(data).execute()
        return True
    except Exception as e:
        st.error(f"Supabase error: {e}")
        return False

def load_from_database(table_name: str, filters=None):
    """Load from database (hybrid)"""
    if IS_LOCAL:
        return load_from_sqlite(table_name, filters)
    else:
        return load_from_supabase(table_name, filters)

def load_from_sqlite(table_name: str, filters=None):
    """Load from SQLite"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        query = f"SELECT * FROM {table_name}"
        params = []
        
        if filters:
            where_clauses = []
            for column, value in filters.items():
                where_clauses.append(f"{column} = ?")
                params.append(value)
            query += " WHERE " + " AND ".join(where_clauses)
        
        cursor.execute(query, params)
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        
        # Convert to list of dictionaries
        result = []
        for row in rows:
            result.append(dict(zip(columns, row)))
        
        return result
        
    except Exception as e:
        st.error(f"SQLite load error: {e}")
        return []
    finally:
        conn.close()

def load_from_supabase(table_name: str, filters=None):
    """Load from Supabase"""
    try:
        query = supabase_client.table(table_name).select("*")
        
        if filters:
            for column, value in filters.items():
                query = query.eq(column, value)
        
        result = query.execute()
        return result.data
    except Exception as e:
        st.error(f"Supabase load error: {e}")
        return []

def get_database_info():
    """Show which database is being used"""
    if IS_LOCAL:
        st.sidebar.info("🏠 Using Local SQLite Database")
    else:
        st.sidebar.success("☁️ Using Supabase Cloud Database")
        st.sidebar.caption("Real-time sync enabled!")

# Usage in your main app:
def register_user_hybrid(email: str, password: str, display_name: str, avatar: str, pronouns: str):
    """Register user (works with both databases)"""
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    user_data = {
        "email": email,
        "password_hash": password_hash,
        "display_name": display_name,
        "avatar": avatar,
        "pronouns": pronouns,
        "email_verified": False
    }
    
    return save_to_database("users", user_data)

def login_user_hybrid(email: str, password: str):
    """Login user (works with both databases)"""
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    users = load_from_database("users", {"email": email, "password_hash": password_hash})
    
    return users[0] if users else None