# Bencon Fantasy Calendar - Complete Cloud Ready Version with Sidebar!
import streamlit as st
from datetime import datetime, timedelta
import uuid
import random
import sqlite3
import json
import hashlib
import html
import os

# Try to import Supabase for cloud deployment
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

# Check if running on cloud or locally (safe secret access)
try:
    IS_CLOUD = st.secrets.get("SUPABASE_URL", "") != ""
    if IS_CLOUD and SUPABASE_AVAILABLE:
        SUPABASE_URL = st.secrets["SUPABASE_URL"] 
        SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except:
    IS_CLOUD = False

# Database file for local development
DB_FILE = "bencon_calendar.db"

# Avatar and pronoun options
AVATAR_OPTIONS = {
    '🧙‍♂️': 'Wizard', '🧙‍♀️': 'Sorceress', '⚔️': 'Fighter', '🏹': 'Ranger',
    '🗡️': 'Rogue', '🛡️': 'Paladin', '🎭': 'Bard', '🐻': 'Druid',  
    '👹': 'Warlock', '🔮': 'Cleric', '🦾': 'Artificer', '🗿': 'Barbarian'
}

PRONOUN_OPTIONS = ['they/them', 'she/her', 'he/him', 'xe/xir', 'ze/zir', 'prefer not to say']

# Database functions (hybrid SQLite/Supabase)
def init_database():
    if IS_CLOUD:
        return True  # Supabase tables created in dashboard
    else:
        return init_sqlite()

def init_sqlite():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        email TEXT PRIMARY KEY,
        password_hash TEXT,
        display_name TEXT,
        avatar TEXT,
        pronouns TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS events (
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
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS rsvps (
        id TEXT PRIMARY KEY,
        event_id TEXT,
        user_email TEXT,
        status TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(event_id, user_email)
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS tavern_messages (
        id TEXT PRIMARY KEY,
        user_email TEXT,
        message TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    conn.commit()
    conn.close()
    return True

def save_data(table, data):
    if IS_CLOUD:
        try:
            supabase.table(table).insert(data).execute()
            return True
        except Exception as e:
            st.error(f"Cloud save error: {e}")
            return False
    else:
        return save_sqlite(table, data)

def save_sqlite(table, data):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        if table == "users":
            cursor.execute('''INSERT OR REPLACE INTO users 
                           (email, password_hash, display_name, avatar, pronouns)
                           VALUES (?, ?, ?, ?, ?)''',
                         (data["email"], data["password_hash"], data["display_name"], 
                          data["avatar"], data["pronouns"]))
        
        elif table == "events":
            cursor.execute('''INSERT OR REPLACE INTO events
                           (id, title, description, date, time, location, host_email, tags, max_attendees)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                         (data["id"], data["title"], data["description"], data["date"],
                          data["time"], data["location"], data["host_email"], data["tags"], data["max_attendees"]))
        
        elif table == "tavern_messages":
            cursor.execute('''INSERT INTO tavern_messages (id, user_email, message)
                           VALUES (?, ?, ?)''',
                         (data["id"], data["user_email"], data["message"]))
        
        conn.commit()
        return True
    except Exception as e:
        st.error(f"SQLite save error: {e}")
        return False
    finally:
        conn.close()

def load_data(table, filters=None):
    if IS_CLOUD:
        try:
            query = supabase.table(table).select("*")
            if filters:
                for col, val in filters.items():
                    query = query.eq(col, val)
            if table == "tavern_messages":
                query = query.order("timestamp", desc=False)
            return query.execute().data
        except Exception as e:
            st.error(f"Cloud load error: {e}")
            return []
    else:
        return load_sqlite(table, filters)

def load_sqlite(table, filters=None):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        query = f"SELECT * FROM {table}"
        params = []
        
        if filters:
            where_clauses = []
            for col, val in filters.items():
                where_clauses.append(f"{col} = ?")
                params.append(val)
            query += " WHERE " + " AND ".join(where_clauses)
        
        if table == "tavern_messages":
            query += " ORDER BY timestamp ASC"
            
        cursor.execute(query, params)
        cols = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        
        return [dict(zip(cols, row)) for row in rows]
        
    except Exception as e:
        st.error(f"SQLite load error: {e}")
        return []
    finally:
        conn.close()

# User management
def register_user(email, password, name, avatar, pronouns):
    users = load_data("users", {"email": email})
    if users:
        return False, "Email already exists"
    
    user_data = {
        "email": email,
        "password_hash": hashlib.sha256(password.encode()).hexdigest(),
        "display_name": name,
        "avatar": avatar,
        "pronouns": pronouns
    }
    
    if save_data("users", user_data):
        return True, "Account created!"
    else:
        return False, "Failed to create account"

def login_user(email, password):
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    users = load_data("users", {"email": email, "password_hash": password_hash})
    
    if users:
        return True, users[0]
    else:
        return False, None

def send_tavern_message(user_email, message):
    """Send message to tavern chat"""
    msg_data = {
        "id": str(uuid.uuid4()),
        "user_email": user_email,
        "message": message
    }
    return save_data("tavern_messages", msg_data)

def get_tavern_messages():
    """Get recent tavern messages"""
    return load_data("tavern_messages")

# Initialize
init_database()

# Streamlit App
st.set_page_config(
    page_title="🏰 Bencon Calendar", 
    page_icon="🏰",
    layout="wide"
)

# CSS
st.markdown("""
<style>
.main-header {
    background: linear-gradient(135deg, #2D1B69 0%, #7B2CBF 25%, #9D4EDD 50%, #C77DFF 75%, #E0AAFF 100%);
    color: white; padding: 2rem; text-align: center; border-radius: 15px;
    margin-bottom: 2rem; box-shadow: 0 8px 16px rgba(0,0,0,0.3);
}
.quest-container {
    background: linear-gradient(135deg, #4A148C 0%, #6A1B9A 50%, #8E24AA 100%);
    border: 3px solid #7B2CBF; border-radius: 15px; padding: 20px;
    margin: 15px 0; color: #FFFACD;
}
.tavern-header {
    background: linear-gradient(135deg, #8B4513 0%, #A0522D 25%, #CD853F 50%, #D2691E 75%, #8B4513 100%);
    border: 3px solid #654321; border-radius: 15px; padding: 10px; margin: 10px 0;
    box-shadow: inset 0 2px 4px rgba(255,255,255,0.3), 0 4px 8px rgba(0,0,0,0.3);
    text-align: center; color: #FFFACD;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
}
.chat-message {
    background: #F8F4FF; border-left: 4px solid #7B2CBF;
    padding: 8px; margin: 3px 0; border-radius: 5px; font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🏰 Bencon Fantasy Calendar 🏰</h1>
    <p>Your Realm's Premier Event & Tavern Hub</p>
</div>
""", unsafe_allow_html=True)

# Session state initialization
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "Quest Counter"

# Database status
if IS_CLOUD:
    st.sidebar.success("☁️ Cloud Database Active")
    st.sidebar.caption("🔄 Real-time sync enabled!")
else:
    st.sidebar.info("🏠 Local Database")
    st.sidebar.caption("Deploy for cloud features")

# Authentication
if not st.session_state.current_user:
    st.sidebar.markdown("### 🚪 Enter the Realm")
    
    tab1, tab2 = st.sidebar.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        with st.form("login"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("⚔️ Enter"):
                success, user = login_user(email, password)
                if success:
                    st.session_state.current_user = user
                    st.rerun()
                else:
                    st.error("Invalid credentials")
    
    with tab2:
        with st.form("register"):
            email = st.text_input("Email", key="reg_email")
            password = st.text_input("Password", type="password", key="reg_pass")
            name = st.text_input("Character Name")
            avatar = st.selectbox("Class:", list(AVATAR_OPTIONS.keys()),
                                format_func=lambda x: f"{x} {AVATAR_OPTIONS[x]}")
            pronouns = st.selectbox("Pronouns:", PRONOUN_OPTIONS)
            
            if st.form_submit_button("🗡️ Create Character"):
                success, msg = register_user(email, password, name, avatar, pronouns)
                if success:
                    st.success(msg)
                    st.balloons()
                else:
                    st.error(msg)
    
    # Welcome message for logged out users
    st.markdown("""
    ## 🏰 Welcome to the Bencon Fantasy Calendar!
    
    **Your magical event coordination system featuring:**
    - 📅 Fantasy event planning & RSVPs
    - 🍺 Real-time tavern chat 
    - 👥 Character profiles & classes
    - 🌍 Cloud sync across all devices
    
    **Please login or register to enter the realm!**
    """)

# Main App Content (when logged in)
if st.session_state.current_user:
    user = st.session_state.current_user
    
    # Page Navigation in Sidebar (AFTER authentication)
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🗺️ Navigation")
    
    # Page buttons
    if st.sidebar.button("🏠 Quest Counter", use_container_width=True):
        st.session_state.current_page = "Quest Counter"
        st.rerun()
    if st.sidebar.button("📨 Inbox", use_container_width=True):
        st.session_state.current_page = "Inbox" 
        st.rerun()
    if st.sidebar.button("👤 Profile", use_container_width=True):
        st.session_state.current_page = "Profile"
        st.rerun()
    
    # TAVERN SIDEBAR - SHOWN ON ALL PAGES!
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div class="tavern-header">
        <h4 style="margin: 0;">🍺 The Tavern 🍺</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick tavern message form
    with st.sidebar.form("tavern_chat", clear_on_submit=True):
        message = st.text_input("Message", 
                               placeholder="What's happening at the tavern?",
                               label_visibility="collapsed")
        if st.form_submit_button("📢 Shout to Tavern", use_container_width=True):
            if message:
                if send_tavern_message(user["email"], message):
                    st.success("Message sent!")
                    st.rerun()
    
    # Recent tavern messages in sidebar
    st.sidebar.markdown("**Recent Bar Chatter:**")
    messages = get_tavern_messages()
    
    if messages:
        # Show last 5 messages
        recent_messages = messages[-5:] if len(messages) > 5 else messages
        for msg in recent_messages:
            # Get user info for message
            msg_users = load_data("users", {"email": msg["user_email"]})
            if msg_users:
                msg_user = msg_users[0]
                st.sidebar.markdown(f"""
                <div class="chat-message">
                    <strong>{msg_user['avatar']} {msg_user['display_name']}:</strong><br>
                    {msg['message']}
                </div>
                """, unsafe_allow_html=True)
    else:
        st.sidebar.info("No messages yet. Be the first!")
    
    # User list in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("**👥 Online Adventurers:**")
    all_users = load_data("users")
    for other_user in all_users:
        if other_user["email"] != user["email"]:
            st.sidebar.markdown(f"- {other_user['avatar']} {other_user['display_name']}")
    
    # Logout button
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Leave Tavern", use_container_width=True):
        st.session_state.current_user = None
        st.rerun()
    
    # PAGE CONTENT BASED ON NAVIGATION
    st.markdown(f"## Welcome back, **{user['display_name']}**! {user['avatar']}")
    st.markdown(f"*{AVATAR_OPTIONS.get(user['avatar'], 'Adventurer')} • {user['pronouns']}*")
    
    if st.session_state.current_page == "Quest Counter":
        st.markdown("### 🗓️ Quest Counter")
        st.markdown("*Plan your adventures and coordinate with your party!*")
        
        # Event creation form
        with st.expander("➕ Create New Quest", expanded=False):
            with st.form("create_event"):
                event_title = st.text_input("Quest Name")
                event_desc = st.text_area("Quest Description")
                event_date = st.date_input("Date")
                event_time = st.time_input("Time")
                max_people = st.number_input("Max Adventurers", min_value=2, max_value=20, value=4)
                
                if st.form_submit_button("⚔️ Create Quest"):
                    if event_title and event_desc:
                        event_data = {
                            "id": str(uuid.uuid4()),
                            "title": event_title,
                            "description": event_desc,
                            "date": str(event_date),
                            "time": str(event_time),
                            "location": "TBD",
                            "host_email": user["email"],
                            "tags": "Adventure",
                            "max_attendees": max_people
                        }
                        if save_data("events", event_data):
                            st.success("Quest created successfully! ⚔️")
                            st.balloons()
                            st.rerun()
        
        # Show existing events
        events = load_data("events")
        if events:
            st.markdown("### 📋 Available Quests")
            for event in events:
                with st.container():
                    st.markdown(f"""
                    **🗡️ {event['title']}**  
                    **📅 {event['date']} at {event['time']}**  
                    **🎭 Host:** {event['host_email']}  
                    **👥 Max Party Size:** {event['max_attendees']}  
                    **📖 Description:** {event['description']}
                    """)
                    
                    if st.button(f"Join Quest: {event['title']}", key=f"join_{event['id']}"):
                        st.success(f"Joined quest: {event['title']}! ⚔️")
                    
                    st.divider()
        else:
            st.info("No quests available. Create the first one!")
    
    elif st.session_state.current_page == "Inbox":
        st.markdown("### 📨 Inbox")
        st.markdown("*Messages from fellow adventurers*")
        
        st.info("📬 Inbox functionality coming soon!")
        st.markdown("**Features in development:**")
        st.markdown("- Private messages between adventurers")
        st.markdown("- Quest invitations")
        st.markdown("- Party notifications")
    
    elif st.session_state.current_page == "Profile":
        st.markdown("### 👤 Character Profile")
        st.markdown("*Manage your adventurer details*")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown(f"""
            **Current Character:**
            - **Avatar:** {user['avatar']} ({AVATAR_OPTIONS.get(user['avatar'], 'Unknown')})
            - **Name:** {user['display_name']}
            - **Pronouns:** {user['pronouns']}
            - **Email:** {user['email']}
            """)
        
        with col2:
            st.markdown("**Profile Settings:**")
            
            with st.form("update_profile"):
                new_name = st.text_input("Character Name", value=user['display_name'])
                new_avatar = st.selectbox("Class:", list(AVATAR_OPTIONS.keys()),
                                        index=list(AVATAR_OPTIONS.keys()).index(user['avatar']),
                                        format_func=lambda x: f"{x} {AVATAR_OPTIONS[x]}")
                new_pronouns = st.selectbox("Pronouns:", PRONOUN_OPTIONS, 
                                          index=PRONOUN_OPTIONS.index(user['pronouns']) if user['pronouns'] in PRONOUN_OPTIONS else 0)
                
                if st.form_submit_button("🔄 Update Profile"):
                    # Update user data
                    updated_user = {
                        "email": user["email"],
                        "password_hash": user["password_hash"],
                        "display_name": new_name,
                        "avatar": new_avatar,
                        "pronouns": new_pronouns
                    }
                    if save_data("users", updated_user):
                        st.session_state.current_user = updated_user
                        st.success("Profile updated! ✨")
                        st.rerun()

# Setup instructions for cloud deployment
if not IS_CLOUD and not st.session_state.current_user:
    with st.expander("🚀 Deploy to Cloud (FREE!)"):
        st.markdown("""
        **Make this app live for everyone:**
        
        1. **Create free Supabase account**: https://supabase.com
        2. **Deploy to Streamlit Cloud**: https://share.streamlit.io  
        3. **Add database secrets** in app settings
        4. **Enjoy real-time tavern chat worldwide!** 🌍
        """)

st.markdown("---")
st.markdown("*Built with ❤️ for fantasy adventurers everywhere*")