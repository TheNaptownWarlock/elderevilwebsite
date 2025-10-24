# Enhanced database functions for PostgreSQL (shared database)
import os
import psycopg2
from urllib.parse import urlparse
import streamlit as st

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///bencon_calendar.db')  # Fallback to SQLite

def get_db_connection():
    """Get database connection - works with both PostgreSQL and SQLite"""
    if DATABASE_URL.startswith('postgresql'):
        # PostgreSQL connection for production
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        return conn, 'postgresql'
    else:
        # SQLite connection for local development
        import sqlite3
        conn = sqlite3.connect('bencon_calendar.db')
        return conn, 'sqlite'

def init_database_cloud():
    """Initialize database with cloud-ready setup"""
    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    
    if db_type == 'postgresql':
        # PostgreSQL syntax
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            email VARCHAR(255) PRIMARY KEY,
            password_hash VARCHAR(255),
            display_name VARCHAR(255),
            avatar VARCHAR(50),
            pronouns VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id VARCHAR(255) PRIMARY KEY,
            title VARCHAR(255),
            description TEXT,
            date VARCHAR(20),
            time VARCHAR(20),
            location VARCHAR(255),
            host_email VARCHAR(255),
            tags TEXT,
            max_attendees INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS rsvps (
            id VARCHAR(255) PRIMARY KEY,
            event_id VARCHAR(255),
            user_email VARCHAR(255),
            status VARCHAR(20),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(event_id, user_email)
        )
        ''')
        
    else:
        # SQLite syntax (same as before)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            password_hash TEXT,
            display_name TEXT,
            avatar TEXT,
            pronouns TEXT,
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
    
    conn.commit()
    conn.close()

# Add this to the top of your fantasy_calendar_rsvp.py to enable cloud database
@st.cache_resource
def init_cloud_db():
    init_database_cloud()
    return True