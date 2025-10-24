# Bencon Fantasy Calendar - Cloud Ready Version!
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

def init_database():
    """Initialize the SQLite database with all necessary tables"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Users table
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
    
    # Events table
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
    
    # RSVPs table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS rsvps (
        id TEXT PRIMARY KEY,
        event_id TEXT,
        user_email TEXT,
        status TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (event_id) REFERENCES events (id),
        UNIQUE(event_id, user_email)
    )
    ''')
    
    # Tavern messages table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tavern_messages (
        id TEXT PRIMARY KEY,
        user_email TEXT,
        message TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_email) REFERENCES users (email)
    )
    ''')
    
    # Private messages table  
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS private_messages (
        id TEXT PRIMARY KEY,
        sender_email TEXT,
        recipient_email TEXT,
        subject TEXT,
        message TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        read_status INTEGER DEFAULT 0,
        FOREIGN KEY (sender_email) REFERENCES users (email),
        FOREIGN KEY (recipient_email) REFERENCES users (email)
    )
    ''')
    
    conn.commit()
    conn.close()

def save_to_database(table, data):
    """Generic function to save data to database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    if table == "users":
        cursor.execute('''
        INSERT OR REPLACE INTO users (email, password_hash, display_name, avatar, pronouns)
        VALUES (?, ?, ?, ?, ?)
        ''', (data["email"], data["password_hash"], data["display_name"], data["avatar"], data["pronouns"]))
    
    elif table == "events":
        cursor.execute('''
        INSERT OR REPLACE INTO events (id, title, description, date, time, location, host_email, tags, max_attendees)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (data["id"], data["title"], data["description"], data["date"], data["time"], 
              data["location"], data["host_email"], json.dumps(data["tags"]), data["max_attendees"]))
    
    elif table == "rsvps":
        cursor.execute('''
        INSERT OR REPLACE INTO rsvps (id, event_id, user_email, status)
        VALUES (?, ?, ?, ?)
        ''', (data["id"], data["event_id"], data["user_email"], data["status"]))
    
    elif table == "tavern_messages":
        cursor.execute('''
        INSERT INTO tavern_messages (id, user_email, message)
        VALUES (?, ?, ?)
        ''', (data["id"], data["user_email"], data["message"]))
        
    elif table == "private_messages":
        cursor.execute('''
        INSERT INTO private_messages (id, sender_email, recipient_email, subject, message)
        VALUES (?, ?, ?, ?, ?)
        ''', (data["id"], data["sender_email"], data["recipient_email"], data["subject"], data["message"]))
    
    conn.commit()
    conn.close()

def load_from_database(table, conditions=None):
    """Generic function to load data from database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    if conditions:
        query = f"SELECT * FROM {table} WHERE {conditions}"
    else:
        query = f"SELECT * FROM {table}"
    
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

# Initialize database on app start
init_database()

# Fantasy tags with icons
TAGS = {
    "Bird Games": "♟️",
    "RPG with Pals, Lovers and Enemies": "🎲",
    "B.Y.B.L.F": "👺",
    "Vidya James": "🎮"
}

# Calendar days
DAYS = [
    ("2026-02-05", "Thursday, Feb 5"),
    ("2026-02-06", "Friday, Feb 6"),
    ("2026-02-07", "Saturday, Feb 7"),
]

# Generate 30-minute time slots
def generate_time_slots(start="09:00", end="22:00"):
    slots = []
    current = datetime.strptime(start, "%H:%M")
    end_time = datetime.strptime(end, "%H:%M")
    while current <= end_time:
        # Convert to 12-hour format with AM/PM
        am_pm_time = current.strftime("%I:%M %p").lstrip('0')
        slots.append(am_pm_time)
        current += timedelta(minutes=30)
    return slots

TIME_SLOTS = generate_time_slots()

# Avatar options
AVATAR_OPTIONS = {
    "🧙‍♂️": "Wizard",
    "⚔️": "Warrior", 
    "🏹": "Archer",
    "🛡️": "Paladin",
    "🗡️": "Rogue",
    "🔮": "Sorcerer",
    "📚": "Scholar",
    "🎭": "Bard",
    "🐉": "Dragonborn",
    "🦄": "Unicorn",
    "🔥": "Fire Mage",
    "❄️": "Ice Mage",
    "🌟": "Cleric",
    "🦅": "Ranger",
    "👑": "Noble"
}

# Pronoun options
PRONOUN_OPTIONS = [
    "they/them",
    "she/her", 
    "he/him",
    "xe/xem",
    "ze/zir",
    "ask me"
]

# Initialize session state for profile editing
if "show_profile" not in st.session_state:
    st.session_state.show_profile = False
if "show_password_reset" not in st.session_state:
    st.session_state.show_password_reset = False
if "viewing_user_schedule" not in st.session_state:
    st.session_state.viewing_user_schedule = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "Quest Counter"
if "editing_event" not in st.session_state:
    st.session_state.editing_event = None
if "form_submitted" not in st.session_state:
    st.session_state.form_submitted = False

# Funny fantasy cancel messages
CANCEL_MESSAGES = [
    "YOU DIED ☠️",
    "QUEST ABANDONED 💀",
    "RETREAT! 🏃‍♂️",
    "COURAGE FAILED 😰",
    "TELEPORT AWAY 🌀",
    "CHICKEN OUT 🐔",
    "NAH, FAM 🙅‍♂️",
    "NOPE.EXE 🚫",
    "ABORT MISSION 🚁",
    "RAGEQUIT 😤",
    "BAIL OUT 🪂",
    "TACTICAL WITHDRAWAL 🛡️",
    "I'M OUT 👋",
    "FLEE THE SCENE 💨",
    "COWARDLY ESCAPE 🏰"
]

# Functions to sync session state with database
def load_users_from_db():
    """Load users from database into session state"""
    users = {}
    db_users = load_from_database("users")
    for user_row in db_users:
        email, password_hash, display_name, avatar, pronouns, created_at = user_row
        users[email] = {
            "password": password_hash,  # This is now hashed
            "display_name": display_name,
            "avatar": avatar,
            "pronouns": pronouns
        }
    return users

def load_events_from_db():
    """Load events from database into session state"""
    events = []
    db_events = load_from_database("events")
    for event_row in db_events:
        event_id, title, description, date, time, location, host_email, tags, max_attendees, created_at = event_row
        events.append({
            "id": event_id,
            "title": title,
            "description": description,
            "date": date,
            "time": time,
            "location": location,
            "host_email": host_email,
            "tags": json.loads(tags) if tags else [],
            "max_attendees": max_attendees
        })
    return events

def sync_session_with_db():
    """Sync session state with database on app start"""
    # Load data from database
    db_users = load_users_from_db()
    db_events = load_events_from_db()
    
    # If database is empty, create test users
    if not db_users:
        test_users = {
            "Test": {
                "password": hashlib.md5("Test".encode()).hexdigest(),
                "display_name": "Test",
                "avatar": "🧙‍♂️",
                "pronouns": "they/them"
            },
            "Test2": {
                "password": hashlib.md5("Test2".encode()).hexdigest(),
                "display_name": "Test2", 
                "avatar": "⚔️",
                "pronouns": "she/her"
            }
        }
        # Save test users to database
        for email, user_data in test_users.items():
            save_to_database("users", {
                "email": email,
                "password_hash": user_data["password"],
                "display_name": user_data["display_name"],
                "avatar": user_data["avatar"],
                "pronouns": user_data["pronouns"]
            })
        return test_users, []
    
    return db_users, db_events

# Initialize session state with database persistence
if "events" not in st.session_state:
    st.session_state.users, st.session_state.events = sync_session_with_db()
else:
    # Always load fresh data from database to keep in sync
    st.session_state.users, st.session_state.events = sync_session_with_db()

if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "messages" not in st.session_state:
    st.session_state.messages = {}
if "show_messaging" not in st.session_state:
    st.session_state.show_messaging = False
if "message_sent_confirmation" not in st.session_state:
    st.session_state.message_sent_confirmation = None
if "replying_to" not in st.session_state:
    st.session_state.replying_to = None
if "tavern_messages" not in st.session_state:
    st.session_state.tavern_messages = []
if "tavern_form_counter" not in st.session_state:
    st.session_state.tavern_form_counter = 0
if "sent_messages" not in st.session_state:
    st.session_state.sent_messages = {}
if "active_inbox_tab" not in st.session_state:
    st.session_state.active_inbox_tab = "Messages"
if "inline_reply_to" not in st.session_state:
    st.session_state.inline_reply_to = None
if "pending_verification" not in st.session_state:
    st.session_state.pending_verification = {}
if "verification_codes" not in st.session_state:
    st.session_state.verification_codes = {}
if "password_reset_codes" not in st.session_state:
    st.session_state.password_reset_codes = {}

# Email simulation functions
import random
import string

def generate_verification_code():
    """Generate a 6-digit verification code"""
    return ''.join(random.choices(string.digits, k=6))

def send_verification_email(email, code):
    """Simulate sending verification email (in real app, this would use email service)"""
    # For demo purposes, we'll just store and display the code
    st.session_state.verification_codes[email] = code
    return f"📧 Verification email sent to {email}! Code: **{code}** (In a real app, this would be sent via email)"

def send_password_reset_email(email, code):
    """Simulate sending password reset email"""
    st.session_state.password_reset_codes[email] = code
    return f"📧 Password reset email sent to {email}! Code: **{code}** (In a real app, this would be sent via email)"

def verify_email_code(email, input_code):
    """Verify the email verification code"""
    if email in st.session_state.verification_codes:
        if st.session_state.verification_codes[email] == input_code:
            return True
    return False

def verify_reset_code(email, input_code):
    """Verify the password reset code"""
    if email in st.session_state.password_reset_codes:
        if st.session_state.password_reset_codes[email] == input_code:
            return True
    return False

# User management functions
def register_user(email, password, display_name, avatar, pronouns, verification_code=None):
    if email.strip() and password.strip() and display_name.strip() and avatar and pronouns:
        # Check if email already exists
        if email in st.session_state.users:
            return False, "Email already exists!"
        
        # Check if display name (username) already exists
        for existing_email, user_data in st.session_state.users.items():
            if user_data["display_name"].lower() == display_name.strip().lower():
                return False, f"Username '{display_name.strip()}' is already taken! Please choose a different name."
        
        # If verification code is provided, verify it
        if verification_code is not None:
            if verify_email_code(email, verification_code):
                # Create the user account
                # Hash password for security
                password_hash = hashlib.md5(password.encode()).hexdigest()
                
                # Save to session state
                st.session_state.users[email] = {
                    "password": password_hash,
                    "display_name": display_name.strip(),
                    "avatar": avatar,
                    "pronouns": pronouns
                }
                
                # Save to database
                save_to_database("users", {
                    "email": email,
                    "password_hash": password_hash,
                    "display_name": display_name.strip(),
                    "avatar": avatar,
                    "pronouns": pronouns
                })
                
                # Clean up verification data
                if email in st.session_state.verification_codes:
                    del st.session_state.verification_codes[email]
                if email in st.session_state.pending_verification:
                    del st.session_state.pending_verification[email]
                
                # Auto-login after registration
                st.session_state.current_user = {
                    "email": email,
                    "display_name": display_name.strip(),
                    "avatar": avatar,
                    "pronouns": pronouns
                }
                return True, f"Welcome to the party, {display_name}! 🎉"
            else:
                return False, "Invalid verification code! Please check your email."
        else:
            # Store pending registration data and send verification email
            st.session_state.pending_verification[email] = {
                "password": password,
                "display_name": display_name.strip(),
                "avatar": avatar,
                "pronouns": pronouns
            }
            code = generate_verification_code()
            message = send_verification_email(email, code)
            return "verification_needed", message
    return False, "All fields are required!"

def login_user(email, password):
    if email in st.session_state.users:
        # Hash the provided password to compare with stored hash
        password_hash = hashlib.md5(password.encode()).hexdigest()
        if st.session_state.users[email]["password"] == password_hash:
            user_data = st.session_state.users[email]
            st.session_state.current_user = {
                "email": email,
                "display_name": user_data["display_name"],
                "avatar": user_data.get("avatar", "🧙‍♂️"),
                "pronouns": user_data.get("pronouns", "they/them")
            }
            return True, f"Welcome back, {user_data['display_name']}!"
        else:
            return False, "Invalid password!"
    else:
        return False, "Email not found!"

def update_user_profile(email, display_name, avatar, pronouns):
    if email in st.session_state.users:
        st.session_state.users[email]["display_name"] = display_name
        st.session_state.users[email]["avatar"] = avatar
        st.session_state.users[email]["pronouns"] = pronouns
        # Update current user session
        st.session_state.current_user.update({
            "display_name": display_name,
            "avatar": avatar,
            "pronouns": pronouns
        })
        return True
    return False

def reset_password(email, new_password, reset_code=None):
    if reset_code is not None:
        # Verify the reset code
        if verify_reset_code(email, reset_code):
            if email in st.session_state.users:
                st.session_state.users[email]["password"] = new_password
                # Clean up reset data
                if email in st.session_state.password_reset_codes:
                    del st.session_state.password_reset_codes[email]
                return True, "Password reset successfully!"
            else:
                return False, "Email not found!"
        else:
            return False, "Invalid reset code! Please check your email."
    else:
        # Send reset email
        if email in st.session_state.users:
            code = generate_verification_code()
            message = send_password_reset_email(email, code)
            return "reset_email_sent", message
        else:
            return False, "Email not found!"

def logout_user():
    st.session_state.current_user = None
    st.session_state.show_profile = False
    st.session_state.show_password_reset = False

def is_event_past(event_day, event_end_time):
    """Check if an event is in the past"""
    try:
        # Parse the event date and end time
        event_date = datetime.strptime(event_day, "%Y-%m-%d").date()
        event_time = datetime.strptime(event_end_time, "%I:%M %p").time()
        event_datetime = datetime.combine(event_date, event_time)
        
        # Compare with current time
        now = datetime.now()
        return event_datetime < now
    except:
        # If there's any parsing error, assume event is not past
        return False

def send_message(from_email, to_email, message, event_id=None, reply_to_id=None):
    """Send a message to another user"""
    if "messages" not in st.session_state:
        st.session_state.messages = {}
    
    if to_email not in st.session_state.messages:
        st.session_state.messages[to_email] = []
    
    message_data = {
        "id": str(uuid.uuid4()),
        "from_email": from_email,
        "from_name": st.session_state.users[from_email]["display_name"],
        "from_avatar": st.session_state.users[from_email].get("avatar", "🧙‍♂️"),
        "message": message,
        "event_id": event_id,
        "reply_to_id": reply_to_id,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "read": False
    }
    
    st.session_state.messages[to_email].append(message_data)
    
    # Also store in sent messages for the sender
    if "sent_messages" not in st.session_state:
        st.session_state.sent_messages = {}
    if from_email not in st.session_state.sent_messages:
        st.session_state.sent_messages[from_email] = []
    
    sent_message_data = message_data.copy()
    sent_message_data["to_email"] = to_email
    sent_message_data["to_name"] = st.session_state.users[to_email]["display_name"]
    sent_message_data["to_avatar"] = st.session_state.users[to_email].get("avatar", "🧙‍♂️")
    st.session_state.sent_messages[from_email].append(sent_message_data)
    
    return message_data["id"]

def get_user_messages(user_email):
    """Get all messages for a user"""
    if "messages" not in st.session_state:
        st.session_state.messages = {}
    
    return st.session_state.messages.get(user_email, [])

def mark_message_read(user_email, message_id):
    """Mark a message as read"""
    if user_email in st.session_state.messages:
        for message in st.session_state.messages[user_email]:
            if message["id"] == message_id:
                message["read"] = True
                break

def delete_message(user_email, message_id):
    """Delete a message"""
    if user_email in st.session_state.messages:
        st.session_state.messages[user_email] = [
            msg for msg in st.session_state.messages[user_email] 
            if msg["id"] != message_id
        ]

def get_unread_count(user_email):
    """Get count of unread messages"""
    messages = get_user_messages(user_email)
    return len([msg for msg in messages if not msg.get("read", False)])

def get_message_thread(message_id, user_email):
    """Get full conversation thread for a message"""
    # Get all messages (both sent and received) for this user
    received_messages = get_user_messages(user_email)
    sent_messages = st.session_state.sent_messages.get(user_email, [])
    
    # Find the target message first
    target_message = None
    for msg in received_messages:
        if msg["id"] == message_id:
            target_message = msg
            break
    
    if not target_message:
        return []
    
    # Get the other participant's email
    other_user_email = target_message["from_email"]
    
    # Collect all messages between these two users
    thread_messages = []
    
    # Add received messages from the other user
    for msg in received_messages:
        if msg["from_email"] == other_user_email:
            thread_messages.append({
                **msg,
                "direction": "received"
            })
    
    # Add sent messages to the other user
    for msg in sent_messages:
        if msg.get("to_email") == other_user_email:
            thread_messages.append({
                **msg,
                "direction": "sent"
            })
    
    # Sort by timestamp
    thread_messages.sort(key=lambda x: x["timestamp"])
    
    return thread_messages

def get_event_by_id(event_id):
    """Get event details by ID"""
    for event in st.session_state.events:
        if event["id"] == event_id:
            return event
    return None

def send_tavern_message(user_email, message):
    """Send a message to the tavern chatroom"""
    if "tavern_messages" not in st.session_state:
        st.session_state.tavern_messages = []
    
    user_info = st.session_state.users.get(user_email, {})
    user_avatar = user_info.get("avatar", "🧙‍♂️")
    user_class = AVATAR_OPTIONS.get(user_avatar, "Adventurer")
    
    message_data = {
        "id": str(uuid.uuid4()),
        "user_email": user_email,
        "user_name": user_info.get("display_name", "Unknown Adventurer"),
        "user_avatar": user_avatar,
        "user_class": user_class,
        "message": message,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "full_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "beer_count": 0,
        "beer_users": []  # List of user emails who gave beers
    }
    
    st.session_state.tavern_messages.append(message_data)
    
    # Keep only the last 50 messages to prevent memory issues
    if len(st.session_state.tavern_messages) > 50:
        st.session_state.tavern_messages = st.session_state.tavern_messages[-50:]
    
    return message_data["id"]

def get_tavern_messages():
    """Get all tavern messages"""
    if "tavern_messages" not in st.session_state:
        st.session_state.tavern_messages = []
    
    return st.session_state.tavern_messages

def toggle_beer_for_message(message_id, user_email):
    """Toggle beer vote for a tavern message (add if not voted, remove if already voted)"""
    if "tavern_messages" not in st.session_state:
        st.session_state.tavern_messages = []
        return False
        
    for msg in st.session_state.tavern_messages:
        if msg["id"] == message_id:
            # Initialize beer fields if they don't exist (for legacy messages)
            if "beer_count" not in msg:
                msg["beer_count"] = 0
            if "beer_users" not in msg:
                msg["beer_users"] = []
            
            # Toggle beer vote
            if user_email in msg["beer_users"]:
                # Remove vote
                msg["beer_users"].remove(user_email)
                msg["beer_count"] = max(0, msg["beer_count"] - 1)
            else:
                # Add vote
                msg["beer_users"].append(user_email)
                msg["beer_count"] += 1
            
            return True
    
    # Message not found
    return False







def rsvp_to_event(event_id, user_info):
    for event in st.session_state.events:
        if event["id"] == event_id:
            if "rsvps" not in event:
                event["rsvps"] = []
            # Store email, display name, and avatar for RSVP
            user_rsvp = {
                "email": user_info["email"], 
                "display_name": user_info["display_name"],
                "avatar": user_info.get("avatar", "🧙‍♂️")
            }
            if not any(rsvp["email"] == user_info["email"] for rsvp in event["rsvps"]):
                event["rsvps"].append(user_rsvp)
                # Save RSVP to database
                save_to_database("rsvps", {
                    "id": str(uuid.uuid4()),
                    "event_id": event_id,
                    "user_email": user_info["email"],
                    "status": "yes"
                })
            break

def cancel_rsvp(event_id, user_email):
    for event in st.session_state.events:
        if event["id"] == event_id:
            if "rsvps" in event:
                event["rsvps"] = [rsvp for rsvp in event["rsvps"] if rsvp["email"] != user_email]
                # Remove RSVP from database
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM rsvps WHERE event_id = ? AND user_email = ?", (event_id, user_email))
                conn.commit()
                conn.close()
            break

def delete_event(event_id):
    """Delete an event completely"""
    st.session_state.events = [event for event in st.session_state.events if event["id"] != event_id]
    # Delete from database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
    cursor.execute("DELETE FROM rsvps WHERE event_id = ?", (event_id,))
    conn.commit()
    conn.close()

def get_user_hosted_events(user_email):
    """Get all events hosted by a specific user"""
    return [event for event in st.session_state.events if event.get("creator_email") == user_email]

def update_event(event_id, updated_data):
    """Update an existing event"""
    for i, event in enumerate(st.session_state.events):
        if event["id"] == event_id:
            st.session_state.events[i].update(updated_data)
            break

def generate_schedule_html(user_email):
    """Generate HTML for printing user's schedule"""
    user_info = st.session_state.users.get(user_email, {})
    user_name = user_info.get('display_name', 'Unknown')
    
    user_events = []
    for event in st.session_state.events:
        if any(rsvp["email"] == user_email for rsvp in event.get("rsvps", [])):
            user_events.append(event)
    
    html = f"""
    <html>
    <head>
        <title>{user_name}'s Bencon 2026 Schedule</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ text-align: center; color: #8B4513; }}
            .event {{ margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }}
            .day {{ font-weight: bold; color: #654321; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🧙‍♂️ Bencon 2026 Schedule</h1>
            <h2>{user_name}'s Adventure Itinerary</h2>
        </div>
    """
    
    if user_events:
        current_day = None
        for event in sorted(user_events, key=lambda e: (e["day"], e["start"])):
            day_name = next(day[1] for day in DAYS if day[0] == event["day"])
            if day_name != current_day:
                html += f'<div class="day">{day_name}</div>'
                current_day = day_name
            
            tag_icon = TAGS.get(event["tag"], "📝")
            html += f'''
            <div class="event">
                <strong>{tag_icon} {event['name']}</strong><br>
                Time: {event['start']} - {event['end']}<br>
                Host: {event['host']}<br>
                System: {event.get('game_system', 'Not specified')}<br>
                Description: {event['description']}
            </div>
            '''
    else:
        html += '<p><em>No events scheduled yet.</em></p>'
    
    html += '</body></html>'
    return html

def generate_clean_print_html(user_email):
    """Generate clean print-friendly HTML without containers"""
    user_info = st.session_state.users.get(user_email, {})
    user_name = user_info.get('display_name', 'Unknown')
    
    user_events = []
    hosted_events = []
    
    # Get user's RSVPed events
    for event in st.session_state.events:
        if any(rsvp["email"] == user_email for rsvp in event.get("rsvps", [])):
            user_events.append(event)
        if event.get("creator_email") == user_email:
            hosted_events.append(event)
    
    # Combine and remove duplicates
    all_events = user_events.copy()
    for hosted_event in hosted_events:
        if not any(rsvp["email"] == user_email for rsvp in hosted_event.get("rsvps", [])):
            all_events.append(hosted_event)
    
    html = f"""
    <html>
    <head>
        <title>{user_name}'s Bencon 2026 Schedule</title>
        <style>
            @media print {{
                body {{ -webkit-print-color-adjust: exact; }}
            }}
            body {{ 
                font-family: 'Arial', sans-serif; 
                margin: 0.5in; 
                line-height: 1.4;
                font-size: 11pt;
            }}
            .header {{ 
                text-align: center; 
                margin-bottom: 20px;
                border-bottom: 2px solid #8B4513;
                padding-bottom: 10px;
            }}
            .header h1 {{
                font-size: 18pt;
                margin: 0;
                color: #8B4513;
            }}
            .header h2 {{
                font-size: 14pt;
                margin: 5px 0 0 0;
                color: #654321;
            }}
            .day-header {{ 
                font-weight: bold; 
                font-size: 12pt;
                color: #654321; 
                margin: 15px 0 8px 0;
                border-bottom: 1px solid #ccc;
                padding-bottom: 3px;
            }}
            .event-item {{ 
                margin: 8px 0 8px 15px; 
                page-break-inside: avoid;
            }}
            .event-title {{
                font-weight: bold;
                font-size: 11pt;
            }}
            .event-details {{
                margin: 2px 0 2px 10px;
                font-size: 10pt;
                color: #333;
            }}
            .hosting-indicator {{
                color: #B8860B;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>⚔️ BENCON 2026 ⚔️</h1>
            <h2>{user_name}'s Quest Log</h2>
        </div>
    """
    
    if all_events:
        current_day = None
        for event in sorted(all_events, key=lambda e: (e["day"], e["start"])):
            day_name = next(day[1] for day in DAYS if day[0] == event["day"])
            if day_name != current_day:
                html += f'<div class="day-header">{day_name}</div>'
                current_day = day_name
            
            is_hosting = event.get("creator_email") == user_email
            hosting_text = ' <span class="hosting-indicator">(Hosting)</span>' if is_hosting else ''
            
            html += f'''
            <div class="event-item">
                <div class="event-title">{event['name']}{hosting_text}</div>
                <div class="event-details">Time: {event['start']} - {event['end']}</div>
                <div class="event-details">Host: {event['host']}</div>
                <div class="event-details">System: {event.get('game_system', 'Not specified')}</div>
                <div class="event-details">Description: {event['description']}</div>
            </div>
            '''
    else:
        html += '<div style="text-align: center; margin-top: 50px; font-style: italic;">No events scheduled yet.</div>'
    
    html += '''
        <script>
            window.onload = function() {
                setTimeout(function() {
                    window.print();
                }, 500);
            }
        </script>
    </body></html>
    '''
    return html

def generate_pdf_content(user_email):
    """Generate content for PDF generation"""
    user_info = st.session_state.users.get(user_email, {})
    user_name = user_info.get('display_name', 'Unknown')
    
    user_events = []
    hosted_events = []
    
    # Get user's RSVPed events
    for event in st.session_state.events:
        if any(rsvp["email"] == user_email for rsvp in event.get("rsvps", [])):
            user_events.append(event)
        if event.get("creator_email") == user_email:
            hosted_events.append(event)
    
    # Combine and remove duplicates
    all_events = user_events.copy()
    for hosted_event in hosted_events:
        if not any(rsvp["email"] == user_email for rsvp in hosted_event.get("rsvps", [])):
            all_events.append(hosted_event)
    
    content = f"BENCON 2026 - {user_name}'s Adventure Schedule\n"
    content += "=" * 50 + "\n\n"
    
    if all_events:
        current_day = None
        for event in sorted(all_events, key=lambda e: (e["day"], e["start"])):
            day_name = next(day[1] for day in DAYS if day[0] == event["day"])
            if day_name != current_day:
                content += f"\n{day_name}\n"
                content += "-" * len(day_name) + "\n"
                current_day = day_name
            
            is_hosting = event.get("creator_email") == user_email
            hosting_text = " (Hosting)" if is_hosting else ""
            
            content += f"\n• {event['name']}{hosting_text}\n"
            content += f"  Time: {event['start']} - {event['end']}\n"
            content += f"  Host: {event['host']}\n"
            content += f"  System: {event.get('game_system', 'Not specified')}\n"
            content += f"  Description: {event['description']}\n"
    else:
        content += "\nNo events scheduled yet.\n"
    
    return content

# Import medieval fonts and custom CSS
st.html("""
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Uncial+Antiqua&family=MedievalSharp&display=swap" rel="stylesheet">
<style>
/* Medieval font styling for entire app */
.stApp {
    font-family: 'Cinzel', 'Times New Roman', serif !important;
}

/* Headers use more decorative medieval fonts */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Uncial Antiqua', 'Cinzel', 'Old English Text MT', serif !important;
    color: #9D4EDD !important;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3) !important;
}

/* Main title styling */
h1 {
    font-family: 'MedievalSharp', 'Uncial Antiqua', cursive !important;
    font-size: 2.5rem !important;
    color: #7B2CBF !important;
    text-align: center !important;
    text-shadow: 3px 3px 6px rgba(157, 78, 221, 0.5) !important;
}

/* Sidebar styling */
.css-1d391kg, .css-1lcbmhc {
    font-family: 'Cinzel', serif !important;
}

/* Hide sidebar toggle tooltip */
[data-testid="collapsedControl"] [title],
[data-testid="collapsedControl"] [aria-label],
button[title*="keyboard"]::after,
button[aria-label*="keyboard"]::after,
[title="keyboard shortcuts"]::after {
    display: none !important;
    visibility: hidden !important;
}

/* Button text */
.stButton button {
    font-family: 'Cinzel', serif !important;
    font-weight: 600 !important;
}

/* Form elements */
.stTextInput input, .stTextArea textarea, .stSelectbox select {
    font-family: 'Cinzel', serif !important;
}

/* Sidebar text elements with fantasy fonts */
.css-1d391kg .markdown-text-container, 
.css-1lcbmhc .markdown-text-container,
.css-1d391kg div[data-testid="stMarkdownContainer"],
.css-1lcbmhc div[data-testid="stMarkdownContainer"],
.css-1d391kg .stMarkdown,
.css-1lcbmhc .stMarkdown,
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"],
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] strong,
section[data-testid="stSidebar"] .markdown-text-container {
    font-family: 'Cinzel', serif !important;
}

/* User names and registered adventurers */
.css-1d391kg .stMarkdown p,
.css-1lcbmhc .stMarkdown p,
.css-1d391kg .stMarkdown strong,
.css-1lcbmhc .stMarkdown strong,
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown strong,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] strong {
    font-family: 'Cinzel', serif !important;
    font-weight: 600 !important;
}

/* All sidebar text */
section[data-testid="stSidebar"] * {
    font-family: 'Cinzel', serif !important;
}

/* Sidebar headers */
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] h4,
section[data-testid="stSidebar"] h5,
section[data-testid="stSidebar"] h6 {
    font-family: 'Uncial Antiqua', 'Cinzel', serif !important;
}

/* Navigation buttons */
div[data-testid="column"] .stButton button {
    font-family: 'Cinzel', serif !important;
    font-weight: 600 !important;
}

/* Sidebar buttons for users */
section[data-testid="stSidebar"] .stButton button {
    font-family: 'Cinzel', serif !important;
    font-weight: 500 !important;
}
</style>
""")

# Apply the fantasy title styling directly with better font loading
st.html("""
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Uncial+Antiqua&family=MedievalSharp&display=swap" rel="stylesheet">
<div style="
    background: linear-gradient(135deg, #FFD700 0%, #FFA500 25%, #FFDF00 50%, #FFA500 75%, #FFD700 100%);
    background-size: 400% 400%;
    animation: gradientShift 4s ease infinite;
    border: 4px solid #8B4513;
    border-radius: 20px;
    padding: 25px 40px;
    margin: 20px 0;
    text-align: center;
    box-shadow: 
        0 0 30px rgba(255, 215, 0, 0.8),
        inset 0 2px 10px rgba(139, 69, 19, 0.3),
        0 8px 20px rgba(0, 0, 0, 0.4);
    position: relative;
    overflow: hidden;
">
    <div style="
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-image: 
            radial-gradient(circle at 20% 30%, rgba(255, 215, 0, 0.1) 2px, transparent 2px),
            radial-gradient(circle at 80% 70%, rgba(255, 215, 0, 0.1) 1px, transparent 1px),
            radial-gradient(circle at 40% 80%, rgba(255, 255, 255, 0.05) 3px, transparent 3px);
        background-size: 50px 50px, 30px 30px, 70px 70px;
        pointer-events: none;
    "></div>
    <h1 style="
        font-family: 'MedievalSharp', 'Uncial Antiqua', 'Cinzel', 'Old English Text MT', cursive !important;
        font-size: 2.5rem !important;
        color: #7B2CBF !important;
        text-align: center !important;
        text-shadow: 
            2px 2px 0px #5A189A,
            4px 4px 8px rgba(0, 0, 0, 0.8),
            0 0 15px rgba(123, 44, 191, 0.5) !important;
        margin: 0 !important;
        font-weight: bold !important;
        letter-spacing: 3px !important;
        position: relative;
        z-index: 2;
    ">⚔️ 🧙‍♂️ BENCON 2026 🧙‍♀️ ⚔️</h1>
    <div class="fantasy-subtitle">✨ BE YER BEST LIL' FREAK ✨</div>
</div>
<style>
@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.fantasy-subtitle {
    font-family: 'MedievalSharp', 'Uncial Antiqua', 'Cinzel', serif !important;
    font-size: 0.875rem !important;
    color: #9D4EDD !important;
    text-shadow: 
        1px 1px 0px #2D1B69,
        2px 2px 4px rgba(0, 0, 0, 0.6),
        0 0 10px rgba(157, 78, 221, 0.8) !important;
    letter-spacing: 0.0625rem !important;
    font-weight: bold !important;
    text-align: center !important;
    margin-top: 0.3125rem !important;
    position: relative !important;
    z-index: 2 !important;
}

/* Responsive scaling for banner */
@media screen and (max-width: 768px) {
    .stApp h1 {
        font-size: 2.5rem !important;
    }
    .fantasy-subtitle {
        font-size: 0.75rem !important;
    }
}

@media screen and (max-width: 480px) {
    .stApp h1 {
        font-size: 2rem !important;
    }
    .fantasy-subtitle {
        font-size: 0.625rem !important;
        letter-spacing: 0.03125rem !important;
    }
}

/* Zoom scaling support */
@media screen and (min-resolution: 1.5dppx) {
    .stApp h1 {
        font-size: 3.25rem !important;
    }
    .fantasy-subtitle {
        font-size: 0.8125rem !important;
    }
}

/* Container responsive scaling */
.stApp [data-testid="stMarkdownContainer"] > div {
    max-width: 100% !important;
    overflow-x: auto !important;
}

/* Slightly wider sidebar */
.css-1d391kg {
    width: 20rem !important;
}
.css-1lcbmhc {
    width: 20rem !important;
}
section[data-testid="stSidebar"] > div {
    width: 20rem !important;
}
section[data-testid="stSidebar"] {
    width: 20rem !important;
}
.css-1cypcdb {
    width: 20rem !important;
}
/* Sidebar background container */
.css-1oe5cao {
    width: 20rem !important;
}
</style>
""")

# Add tavern-specific sidebar styling if on tavern page
if st.session_state.current_page == "Tavern":
    st.markdown("""
    <style>
    /* Much narrower sidebar for tavern page only */
    .css-1d391kg {
        width: 12rem !important;
    }
    .css-1lcbmhc {
        width: 12rem !important;
    }
    section[data-testid="stSidebar"] > div {
        width: 12rem !important;
    }
    section[data-testid="stSidebar"] {
        width: 12rem !important;
    }
    .css-1cypcdb {
        width: 12rem !important;
    }
    .css-1oe5cao {
        width: 12rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Custom CSS for button styling with neon purple theme
st.markdown("""
<style>
/* Fantasy day container styling */
.fantasy-day-header {
    background: white;
    border: 3px solid #7B2CBF;
    border-radius: 15px;
    padding: 15px 20px;
    margin: 15px 0;
    color: #7B2CBF !important;
    font-family: 'Uncial Antiqua', 'Cinzel', serif !important;
    font-weight: bold;
    text-align: center;
    text-shadow: none;
    box-shadow: 
        inset 0 2px 4px rgba(255,255,255,0.3),
        inset 0 -2px 4px rgba(101, 67, 33, 0.5),
        0 4px 8px rgba(0,0,0,0.3),
        0 0 20px rgba(139, 69, 19, 0.4);
    position: relative;
    overflow: hidden;
}

/* Wider container for All Available Quests section */
.quest-section-wide {
    max-width: 1200px !important;
    width: 95% !important;
}
/* Crackly texture for joined quest buttons */
.joined-quest-button {
    background-image: 
        radial-gradient(circle at 20% 50%, transparent 20%, rgba(139, 69, 19, 0.3) 21%, rgba(139, 69, 19, 0.3) 34%, transparent 35%, transparent),
        linear-gradient(0deg, rgba(160, 82, 45, 0.8) 50%, rgba(139, 69, 19, 0.8) 50%),
        radial-gradient(circle at 80% 20%, transparent 20%, rgba(101, 67, 33, 0.3) 21%, rgba(101, 67, 33, 0.3) 34%, transparent 35%, transparent);
    background-size: 15px 15px, 20px 20px, 25px 25px;
    background-color: #8B4513 !important;
    color: white !important;
    border: 2px solid #654321 !important;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.8) !important;
    font-weight: bold !important;
}

/* Hover effect for cancel button with red texture */
.cancel-quest-button:hover {
    background-image: 
        radial-gradient(circle at 30% 60%, transparent 20%, rgba(220, 53, 69, 0.4) 21%, rgba(220, 53, 69, 0.4) 34%, transparent 35%),
        linear-gradient(45deg, rgba(139, 0, 0, 0.8) 50%, rgba(178, 34, 34, 0.8) 50%),
        radial-gradient(circle at 70% 30%, transparent 20%, rgba(139, 0, 0, 0.3) 21%, rgba(139, 0, 0, 0.3) 34%, transparent 35%);
    background-size: 12px 12px, 18px 18px, 22px 22px;
    background-color: #dc3545 !important;
    color: white !important;
    border-color: #bd2130 !important;
    transform: scale(1.05);
    box-shadow: 0 0 15px rgba(220, 53, 69, 0.5) !important;
    transition: all 0.3s ease !important;
}

.cancel-quest-button {
    background-image: 
        radial-gradient(circle at 30% 60%, transparent 20%, rgba(220, 53, 69, 0.2) 21%, rgba(220, 53, 69, 0.2) 34%, transparent 35%),
        linear-gradient(45deg, rgba(139, 0, 0, 0.4) 50%, rgba(178, 34, 34, 0.4) 50%);
    background-size: 12px 12px, 18px 18px;
    transition: all 0.3s ease !important;
}

/* Join button hover effect */
.join-quest-button:hover {
    background-color: #28a745 !important;
    transform: scale(1.05);
    box-shadow: 0 0 15px rgba(40, 167, 69, 0.5) !important;
    transition: all 0.3s ease !important;
}

.join-quest-button {
    transition: all 0.3s ease !important;
}
</style>
""", unsafe_allow_html=True)

# User Login Section
st.sidebar.header("🎭 Knave Check")

# Show password reset dialog if requested
if st.session_state.show_password_reset:
    st.sidebar.subheader("🔒 Password Reset")
    
    # Check if we have a reset code waiting for any email
    reset_email = None
    for email in st.session_state.password_reset_codes:
        reset_email = email
        break
    
    if reset_email:
        # Show reset code verification form
        st.sidebar.info(f"Reset code sent to {reset_email}")
        with st.sidebar.form("verify_reset_form"):
            reset_code = st.text_input("Enter 6-digit reset code:")
            new_password = st.text_input("New password:", type="password")
            confirm_password = st.text_input("Confirm password:", type="password")
            
            col1, col2 = st.columns(2)
            with col1:
                confirm_reset_btn = st.form_submit_button("Reset Password")
            with col2:
                cancel_reset_btn = st.form_submit_button("Cancel")
            
            if confirm_reset_btn:
                if new_password != confirm_password:
                    st.sidebar.error("Passwords don't match!")
                elif len(new_password) < 6:
                    st.sidebar.error("Password must be at least 6 characters!")
                elif not reset_code:
                    st.sidebar.error("Please enter the reset code!")
                else:
                    result, message = reset_password(reset_email, new_password, reset_code)
                    if result == True:
                        st.sidebar.success(message)
                        st.session_state.show_password_reset = False
                        st.rerun()
                    else:
                        st.sidebar.error(message)
            
            if cancel_reset_btn:
                if reset_email in st.session_state.password_reset_codes:
                    del st.session_state.password_reset_codes[reset_email]
                st.session_state.show_password_reset = False
                st.rerun()
    else:
        # Show email request form
        with st.sidebar.form("request_reset_form"):
            reset_email = st.text_input("Enter your email:")
            request_reset_btn = st.form_submit_button("Send Reset Email")
            cancel_reset_btn = st.form_submit_button("Cancel")
            
            if request_reset_btn:
                if reset_email:
                    result, message = reset_password(reset_email, None)
                    if result == "reset_email_sent":
                        st.sidebar.info(message)
                        st.rerun()
                    else:
                        st.sidebar.error(message)
                else:
                    st.sidebar.error("Please enter your email address!")
            
            if cancel_reset_btn:
                st.session_state.show_password_reset = False
                st.rerun()

elif st.session_state.current_user is None:
    login_tab, register_tab = st.sidebar.tabs(["Login", "Register"])
    
    with login_tab:
        with st.form("login_form"):
            email = st.text_input("Email:")
            password = st.text_input("Password:", type="password")
            col1, col2 = st.columns(2)
            with col1:
                login_btn = st.form_submit_button("Login")
            with col2:
                forgot_btn = st.form_submit_button("Forgot?")
            
            if login_btn:
                success, message = login_user(email, password)
                if success:
                    st.sidebar.success(message)
                    st.rerun()
                else:
                    st.sidebar.error(message)
            
            if forgot_btn:
                st.session_state.show_password_reset = True
                st.rerun()
    
    with register_tab:
        # Check if we're in verification stage for any email
        verification_email = None
        for email in st.session_state.pending_verification:
            verification_email = email
            break
        
        if verification_email:
            # Show verification form
            st.markdown("**📧 Email Verification**")
            st.info(f"Please check your email ({verification_email}) for a verification code.")
            
            with st.form("verify_email_form"):
                verification_code = st.text_input("Enter 6-digit verification code:")
                col1, col2 = st.columns(2)
                
                with col1:
                    verify_btn = st.form_submit_button("Verify & Create Account")
                with col2:
                    cancel_verify_btn = st.form_submit_button("Cancel")
                
                if verify_btn:
                    if verification_code:
                        pending_data = st.session_state.pending_verification[verification_email]
                        result, message = register_user(
                            verification_email,
                            pending_data["password"],
                            pending_data["display_name"],
                            pending_data["avatar"],
                            pending_data["pronouns"],
                            verification_code
                        )
                        if result == True:
                            st.sidebar.success(message)
                            st.rerun()
                        else:
                            st.sidebar.error(message)
                    else:
                        st.sidebar.error("Please enter the verification code.")
                
                if cancel_verify_btn:
                    del st.session_state.pending_verification[verification_email]
                    if verification_email in st.session_state.verification_codes:
                        del st.session_state.verification_codes[verification_email]
                    st.rerun()
        else:
            # Show regular registration form
            with st.form("register_form"):
                reg_email = st.text_input("Email:")
                reg_password = st.text_input("Password:", type="password")
                display_name = st.text_input("Adventurer Name:")
                
                # Avatar selection with better formatting
                st.write("**Choose your avatar:**")
                selected_avatar = st.selectbox("Avatar:", 
                                             options=list(AVATAR_OPTIONS.keys()),
                                             format_func=lambda x: f"{x} {AVATAR_OPTIONS[x]}",
                                             label_visibility="collapsed")
                st.write(f"Preview: {selected_avatar} {AVATAR_OPTIONS[selected_avatar]}")
                
                # Pronouns selection
                pronouns = st.selectbox("Your pronouns:", PRONOUN_OPTIONS)
                
                register_btn = st.form_submit_button("Send Verification Email")
                
                if register_btn:
                    result, message = register_user(reg_email, reg_password, display_name, selected_avatar, pronouns)
                    if result == "verification_needed":
                        st.sidebar.info(message)
                        st.rerun()
                    elif result == True:
                        st.sidebar.success(message)
                        st.rerun()
                    else:
                        st.sidebar.error(message)

else:
    # User profile section
    user = st.session_state.current_user
    
    # Profile button with avatar
    profile_col1, profile_col2 = st.sidebar.columns([1, 3])
    with profile_col1:
        if st.sidebar.button(f"{user['avatar']}", help=f"Click to edit profile - Current: {AVATAR_OPTIONS[user['avatar']]}"):
            st.session_state.show_profile = not st.session_state.show_profile
    with profile_col2:
        # Use HTML for avatar with tooltip
        avatar_html = f"""
        <span title="{AVATAR_OPTIONS[user['avatar']]}">{user['avatar']}</span>
        """
        st.sidebar.markdown(f"**{user['display_name']}** | _{user['pronouns']}_ | {avatar_html}", unsafe_allow_html=True)
    
    # Show profile editor if requested
    if st.session_state.show_profile:
        st.sidebar.subheader("✏️ Edit Profile")
        with st.sidebar.form("profile_form"):
            new_name = st.text_input("Adventurer Name:", value=user['display_name'])
            
            # Avatar selection with better formatting for profile edit
            st.write("**Avatar:**")
            new_avatar = st.selectbox("Choose avatar:", 
                                    options=list(AVATAR_OPTIONS.keys()),
                                    index=list(AVATAR_OPTIONS.keys()).index(user['avatar']),
                                    format_func=lambda x: f"{x} {AVATAR_OPTIONS[x]}",
                                    label_visibility="collapsed")
            
            new_pronouns = st.selectbox("Pronouns:", 
                                      options=PRONOUN_OPTIONS,
                                      index=PRONOUN_OPTIONS.index(user['pronouns']))
            
            col1, col2 = st.columns(2)
            with col1:
                save_btn = st.form_submit_button("Save")
            with col2:
                cancel_btn = st.form_submit_button("Cancel")
            
            if save_btn:
                update_user_profile(user['email'], new_name, new_avatar, new_pronouns)
                st.sidebar.success("Profile updated!")
                st.session_state.show_profile = False
                st.rerun()
            
            if cancel_btn:
                st.session_state.show_profile = False
                st.rerun()
    
    if st.sidebar.button("Logout"):
        logout_user()
        st.rerun()

# Show registered users with avatars (clickable)
if st.session_state.users:
    st.sidebar.write("**Registered Adventurers:**")
    for email, user_info in st.session_state.users.items():
        avatar = user_info.get('avatar', '🧙‍♂️')
        pronouns = user_info.get('pronouns', 'they/them')
        avatar_name = AVATAR_OPTIONS.get(avatar, 'Unknown')
        
        # Create clickable user entry
        if st.sidebar.button(f"{avatar} {user_info['display_name']} _{pronouns}_", 
                           key=f"user_{email}",
                           help=f"Click to view {user_info['display_name']}'s schedule"):
            st.session_state.viewing_user_schedule = email
            st.rerun()

# Tavern Chat (only show on Quest Counter page)
if st.session_state.current_user and st.session_state.current_page == "Quest Counter":
    st.sidebar.markdown("---")
    
    # Tavern header
    st.sidebar.markdown("""
    <div style="background: linear-gradient(135deg, #8B4513 0%, #A0522D 25%, #CD853F 50%, #D2691E 75%, #8B4513 100%);
               border: 3px solid #654321; border-radius: 15px; padding: 10px; margin: 10px 0;
               box-shadow: inset 0 2px 4px rgba(255,255,255,0.3), 0 4px 8px rgba(0,0,0,0.3);">
        <h4 style="color: #FFFACD; text-align: center; margin: 0; 
                 text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
                 font-family: 'Uncial Antiqua', 'Cinzel', serif;">
            🍺 The Tavern 🍺
        </h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Real-time chat with database sync
    import time
    if 'last_chat_refresh' not in st.session_state:
        st.session_state.last_chat_refresh = time.time()
    
    # Refresh every 3 seconds and reload from database
    current_time = time.time()
    if current_time - st.session_state.last_chat_refresh > 3:
        st.session_state.last_chat_refresh = current_time
        # Reload tavern messages from database for real-time updates
        sync_session_with_db()
        st.rerun()
    
    # Chat messages display in sidebar
    tavern_messages = get_tavern_messages()
    
    # Create a container for messages
    st.sidebar.markdown("**Recent Bar Goss:** 🔄")
    
    if tavern_messages:
        # Show last 5 messages in sidebar (newest first)
        recent_messages = tavern_messages[-5:] if len(tavern_messages) > 5 else tavern_messages
        
        for msg in reversed(recent_messages):
            # Compact message display for sidebar
            is_current_user = msg["user_email"] == st.session_state.current_user["email"]
            bg_color = "#E8F4FD" if is_current_user else "#F8F4FF"
            
            # Get class name for message (with fallback for legacy messages)
            user_class = msg.get('user_class')
            if not user_class:
                # Fallback: get class from current user data
                user_info = st.session_state.users.get(msg['user_email'], {})
                user_avatar = user_info.get('avatar', msg.get('user_avatar', '🧙‍♂️'))
                user_class = AVATAR_OPTIONS.get(user_avatar, 'Adventurer')
            
            st.sidebar.markdown(f"""
            <div style="border: 1px solid #7B2CBF; border-radius: 5px; 
                       padding: 4px; margin: 3px 8px 3px 3px; background: {bg_color};
                       font-size: 11px; max-width: 85%;">
                <div style="font-weight: bold; color: #7B2CBF;">
                    {msg['user_avatar']} {msg['user_name'][:8]}{'...' if len(msg['user_name']) > 8 else ''} | <i>"{user_class[:8]}{'...' if len(user_class) > 8 else ''}"</i>
                </div>
                <div style="color: #333; font-size: 10px;">
                    {msg['message'][:35]}{'...' if len(msg['message']) > 35 else ''}
                </div>
                <div style="font-size: 8px; color: #666; text-align: right;">
                    {msg['timestamp']}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.sidebar.markdown("_The tavern is quiet..._")
    
    # Quick chat input
    st.sidebar.markdown("""
    <style>
    /* Yap form container styling */
    .stForm {
        max-width: 85% !important;
        margin: 3px 8px 3px 3px !important;
    }
    .stTextArea > div > div > textarea {
        width: 100% !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Stylized Yap label
    st.sidebar.markdown("""
    <div style="font-weight: bold; color: #7B2CBF; font-size: 14px; 
               margin-bottom: 5px; font-family: 'Cinzel', serif; 
               text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">
        💬 Yap:
    </div>
    """, unsafe_allow_html=True)
    
    with st.sidebar.form("tavern_quick_chat"):
        quick_message = st.text_area("Message", 
                                   placeholder="Say something...", 
                                   max_chars=100, 
                                   height=60,
                                   label_visibility="collapsed")
        
        send_quick = st.form_submit_button("🦅 Send", use_container_width=True)
        
        if send_quick:
            if quick_message.strip():
                send_tavern_message(st.session_state.current_user["email"], quick_message.strip())
                st.sidebar.success("Sent! 🍺")
                st.rerun()
            else:
                st.sidebar.error("Enter a message!")
    
    # Refresh button for chat
    if st.sidebar.button("🔄 Refresh Tavern", use_container_width=True):
        st.rerun()

# Only show content if user is logged in
if st.session_state.current_user is None:
    st.warning("🚪 Please scream into the void to join the festivities!")
    st.stop()

# Navigation Bar
st.markdown("---")
nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)
with nav_col1:
    if st.button("🗓️ Quest Counter", use_container_width=True, 
                type="primary" if st.session_state.current_page == "Quest Counter" else "secondary"):
        st.session_state.current_page = "Quest Counter"
        st.session_state.viewing_user_schedule = None
        st.rerun()

with nav_col2:
    # Inbox with unread count
    unread_count = get_unread_count(st.session_state.current_user["email"])
    inbox_label = f"📨 Inbox ({unread_count})" if unread_count > 0 else "📨 Inbox"
    if st.button(inbox_label, use_container_width=True,
                type="primary" if st.session_state.current_page == "Inbox" else "secondary"):
        st.session_state.current_page = "Inbox"
        st.session_state.viewing_user_schedule = None
        st.session_state.editing_event = None
        st.rerun()

with nav_col3:
    if st.button("🍺 Tavern", use_container_width=True,
                type="primary" if st.session_state.current_page == "Tavern" else "secondary"):
        st.session_state.current_page = "Tavern"
        st.session_state.viewing_user_schedule = None
        st.session_state.editing_event = None
        st.rerun()
        
with nav_col4:
    user_avatar = st.session_state.current_user.get('avatar', '🧙‍♂️')
    if st.button(f"{user_avatar} Profile", use_container_width=True,
                type="primary" if st.session_state.current_page == "Profile" else "secondary"):
        st.session_state.current_page = "Profile"
        st.session_state.viewing_user_schedule = None
        st.session_state.editing_event = None
        st.rerun()

st.markdown("---")

st.markdown("---")

# Show user schedule if viewing someone's profile
if st.session_state.viewing_user_schedule:
    viewed_email = st.session_state.viewing_user_schedule
    if viewed_email in st.session_state.users:
        viewed_user = st.session_state.users[viewed_email]
        
        st.header(f"📅 {viewed_user['display_name']}'s Schedule")
        
        # Close button
        if st.button("← Back to Calendar"):
            st.session_state.viewing_user_schedule = None
            st.rerun()
        
        # Find user's events
        user_events = []
        for event in st.session_state.events:
            if any(rsvp["email"] == viewed_email for rsvp in event.get("rsvps", [])):
                user_events.append(event)
        
        if user_events:
            for event in sorted(user_events, key=lambda e: (e["day"], e["start"])):
                day_name = next(day[1] for day in DAYS if day[0] == event["day"])
                tag_icon = TAGS.get(event["tag"], "📝")
                
                # Check if event is past
                is_past = is_event_past(event["day"], event["end"])
                strikethrough_style = "text-decoration: line-through; opacity: 0.7;" if is_past else ""
                past_indicator = " [COMPLETED]" if is_past else ""
                
                with st.container():
                    st.markdown(f"""
                    <div style="border: 2px solid #7B2CBF; border-radius: 10px; 
                               padding: 12px; margin: 8px 0; background: #F8F4FF; {strikethrough_style}">
                        <div style="font-weight: bold; color: #7B2CBF; margin-bottom: 5px; {strikethrough_style}">
                            {tag_icon} {event['name']}{past_indicator}
                        </div>
                        <div style="color: #333; margin-bottom: 8px; font-size: 14px; {strikethrough_style}">
                            📅 {day_name} at {event['start']}-{event['end']} | Host: {event['host']}
                        </div>
                        <div style="color: #666; font-size: 12px; {strikethrough_style}">
                            💻 System: {event.get('game_system', 'Not specified')}
                        </div>
                        <div style="color: #666; font-size: 12px; font-style: italic; margin-top: 8px; {strikethrough_style}">
                            📖 {event['description']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.write(f"_{viewed_user['display_name']} hasn't joined any quests yet._")
        
        st.stop()

# Inbox Page
if st.session_state.current_page == "Inbox":
    st.header("📨 Adventurer's Inbox")
    
    # Messaging tabs
    tab_names = ["📥 Received", "📤 Sent", "✉️ Send Message"]
    selected_tab_index = 0
    if st.session_state.active_inbox_tab == "Sent":
        selected_tab_index = 1
    elif st.session_state.active_inbox_tab == "Send Message":
        selected_tab_index = 2
    
    tabs = st.tabs(tab_names)
    
    with tabs[0]:  # Received Messages
        messages = get_user_messages(st.session_state.current_user["email"])
        
        if not messages:
            st.info("Your inbox is empty. No messages from fellow adventurers yet!")
        else:
            st.write(f"You have {len(messages)} message(s)")
            
            # Sort messages by timestamp (newest first)
            messages.sort(key=lambda x: x["timestamp"], reverse=True)
            
            for message in messages:
                # Mark as read when viewing
                if not message.get("read", False):
                    mark_message_read(st.session_state.current_user["email"], message["id"])
                
                # Message container styling
                read_style = "opacity: 0.7;" if message.get("read", False) else ""
                
                with st.container():
                    st.markdown(f"""
                    <div style="border: 2px solid #7B2CBF; border-radius: 10px; padding: 15px; 
                               margin: 10px 0; background: linear-gradient(135deg, #F8F4FF 0%, #EDE4FF 100%); 
                               {read_style}">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                            <div style="font-weight: bold; color: #7B2CBF;">
                                {message['from_avatar']} From: {message['from_name']}
                            </div>
                            <div style="font-size: 12px; color: #666;">
                                {message['timestamp']}
                            </div>
                        </div>
                        <div style="color: #333; margin-bottom: 10px;">
                            {message['message']}
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # If message has an event link
                    if message.get("event_id"):
                        event = get_event_by_id(message["event_id"])
                        if event:
                            day_name = next(day[1] for day in DAYS if day[0] == event["day"])
                            tag_icon = TAGS.get(event["tag"], "📝")
                            
                            st.markdown(f"""
                            <div style="background: #FFFACD; border: 1px solid #FFD700; border-radius: 5px; 
                                       padding: 10px; margin-top: 10px;">
                                <div style="font-weight: bold; color: #8B4513;">
                                    🎯 Shared Event: {tag_icon} {event['name']}
                                </div>
                                <div style="font-size: 14px; color: #654321;">
                                    📅 {day_name} at {event['start']}-{event['end']} | Host: {event['host']}
                                </div>
                                <div style="font-size: 12px; color: #5D4E75; margin-top: 5px;">
                                    {event['description']}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Quick RSVP button
                            user_rsvped = any(rsvp["email"] == st.session_state.current_user["email"] 
                                            for rsvp in event.get("rsvps", []))
                            is_full = len(event.get("rsvps", [])) >= event["seat_max"]
                            
                            col_rsvp, col_reply, col_delete = st.columns([2, 2, 1])
                            with col_rsvp:
                                if not user_rsvped and not is_full:
                                    if st.button(f"⚔️ Join Quest", key=f"join_inbox_{message['id']}", 
                                               use_container_width=True):
                                        rsvp_to_event(event['id'], st.session_state.current_user)
                                        st.success(f"Joined quest: {event['name']}!")
                                        st.rerun()
                                elif user_rsvped:
                                    st.success("✅ You're already in this party!")
                                else:
                                    st.warning("🚫 Quest is full")
                            
                            with col_reply:
                                if st.button("↩️ Reply", key=f"reply_event_msg_{message['id']}", 
                                           help="Reply to this message", use_container_width=True):
                                    if st.session_state.inline_reply_to == message["id"]:
                                        st.session_state.inline_reply_to = None
                                    else:
                                        st.session_state.inline_reply_to = message["id"]
                                    st.rerun()
                            
                            with col_delete:
                                if st.button("🗑️", key=f"delete_msg_{message['id']}", 
                                           help="Delete message"):
                                    delete_message(st.session_state.current_user["email"], message["id"])
                                    st.rerun()
                        else:
                            st.warning("⚠️ Referenced event no longer exists")
                    else:
                        # Reply and Delete buttons for regular messages
                        col_reply, col_delete = st.columns([3, 1])
                        with col_reply:
                            if st.button("↩️ Reply", key=f"reply_msg_{message['id']}", 
                                       help="Reply to this message", use_container_width=True):
                                if st.session_state.inline_reply_to == message["id"]:
                                    st.session_state.inline_reply_to = None
                                else:
                                    st.session_state.inline_reply_to = message["id"]
                                st.rerun()
                        with col_delete:
                            if st.button("🗑️", key=f"delete_msg_{message['id']}", 
                                       help="Delete message"):
                                delete_message(st.session_state.current_user["email"], message["id"])
                                st.rerun()
                    
                    # Show original message if this is a reply
                    if message.get("reply_to_id"):
                        st.markdown("""
                        <div style="background: #F0F0F0; border-left: 3px solid #7B2CBF; padding: 8px; 
                                   margin-top: 8px; font-size: 12px; font-style: italic;">
                            📝 Replying to an earlier message
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Show inline reply form if this message is selected for reply
                    if st.session_state.inline_reply_to == message["id"]:
                        st.markdown("---")
                        st.markdown("**💬 Conversation Thread:**")
                        
                        # Show the full conversation thread
                        thread_messages = get_message_thread(message["id"], st.session_state.current_user["email"])
                        
                        # Display thread in a scrollable container
                        if thread_messages:
                            with st.container():
                                st.markdown('<div style="max-height: 300px; overflow-y: auto; border: 1px solid #ddd; padding: 10px; border-radius: 5px; background: #f9f9f9;">', unsafe_allow_html=True)
                                
                                for thread_msg in thread_messages:
                                    if thread_msg["direction"] == "sent":
                                        # Sent message (green, right-aligned)
                                        st.markdown(f"""
                                        <div style="text-align: right; margin: 5px 0;">
                                            <div style="display: inline-block; background: #d4edda; border: 1px solid #c3e6cb; 
                                                       border-radius: 10px; padding: 8px 12px; max-width: 80%; text-align: left;">
                                                <div style="font-size: 11px; color: #155724; font-weight: bold;">
                                                    You → {thread_msg.get('to_name', 'Unknown')}
                                                </div>
                                                <div style="color: #333; margin: 3px 0;">
                                                    {html.escape(thread_msg['message'])}
                                                </div>
                                                <div style="font-size: 10px; color: #666;">
                                                    {thread_msg['timestamp']}
                                                </div>
                                            </div>
                                        </div>
                                        """, unsafe_allow_html=True)
                                    else:
                                        # Received message (blue, left-aligned)
                                        st.markdown(f"""
                                        <div style="text-align: left; margin: 5px 0;">
                                            <div style="display: inline-block; background: #d1ecf1; border: 1px solid #bee5eb; 
                                                       border-radius: 10px; padding: 8px 12px; max-width: 80%; text-align: left;">
                                                <div style="font-size: 11px; color: #0c5460; font-weight: bold;">
                                                    {thread_msg['from_avatar']} {thread_msg['from_name']}
                                                </div>
                                                <div style="color: #333; margin: 3px 0;">
                                                    {html.escape(thread_msg['message'])}
                                                </div>
                                                <div style="font-size: 10px; color: #666;">
                                                    {thread_msg['timestamp']}
                                                </div>
                                            </div>
                                        </div>
                                        """, unsafe_allow_html=True)
                                
                                st.markdown('</div>', unsafe_allow_html=True)
                        
                        st.markdown("**✏️ Your Reply:**")
                        
                        with st.form(f"inline_reply_{message['id']}"):
                            reply_text = st.text_area("Your reply:", 
                                                    placeholder="Type your reply here...", 
                                                    max_chars=500, 
                                                    key=f"reply_text_{message['id']}")
                            
                            col_send, col_cancel = st.columns([3, 1])
                            with col_send:
                                send_reply = st.form_submit_button("📤 Send Reply", type="primary", use_container_width=True)
                            with col_cancel:
                                cancel_reply = st.form_submit_button("❌ Cancel", use_container_width=True)
                            
                            if send_reply:
                                if reply_text.strip():
                                    message_id = send_message(
                                        st.session_state.current_user["email"],
                                        message["from_email"],
                                        reply_text.strip(),
                                        None,  # No event_id
                                        message["id"]  # reply_to_id
                                    )
                                    st.session_state.inline_reply_to = None
                                    st.success(f"Reply sent to {message['from_name']}! 📨")
                                    st.rerun()
                                else:
                                    st.error("Please enter a reply message!")
                            
                            if cancel_reply:
                                st.session_state.inline_reply_to = None
                                st.rerun()
    
    with tabs[1]:  # Sent Messages
        sent_messages = st.session_state.sent_messages.get(st.session_state.current_user["email"], [])
        
        if not sent_messages:
            st.info("You haven't sent any messages yet!")
        else:
            st.write(f"You have sent {len(sent_messages)} message(s)")
            
            # Sort messages by timestamp (newest first)
            sent_messages.sort(key=lambda x: x["timestamp"], reverse=True)
            
            for message in sent_messages:
                with st.container():
                    st.markdown(f"""
                    <div style="border: 2px solid #28a745; border-radius: 10px; padding: 15px; 
                               margin: 10px 0; background: linear-gradient(135deg, #F0FFF0 0%, #E8F5E8 100%);">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                            <div style="font-weight: bold; color: #28a745;">
                                {message['to_avatar']} To: {message['to_name']}
                            </div>
                            <div style="font-size: 12px; color: #666;">
                                {message['timestamp']}
                            </div>
                        </div>
                        <div style="color: #333; margin-bottom: 10px;">
                            {message['message']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
    with tabs[2]:  # Send Message
        st.subheader("✉️ Send Message to Fellow Adventurer")
        
        # Show confirmation popup if message was sent
        if st.session_state.message_sent_confirmation:
            st.success(f"🦅 {st.session_state.message_sent_confirmation}")
            # Clear the confirmation after showing it
            st.session_state.message_sent_confirmation = None
        
        # Show reply context if replying
        if st.session_state.replying_to:
            reply_info = st.session_state.replying_to
            st.markdown(f"""
            <div style="background: #E8F4FD; border: 2px solid #7B2CBF; border-radius: 8px; 
                       padding: 10px; margin-bottom: 15px;">
                <div style="font-weight: bold; color: #7B2CBF;">
                    ↩️ Replying to: {reply_info['sender_name']}
                </div>
                <div style="font-size: 12px; color: #666; font-style: italic; margin-top: 5px;">
                    "{reply_info['original_message'][:100]}{'...' if len(reply_info['original_message']) > 100 else ''}"
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("❌ Cancel Reply"):
                st.session_state.replying_to = None
                st.rerun()
        
        # Get list of other users
        other_users = {email: user for email, user in st.session_state.users.items() 
                      if email != st.session_state.current_user["email"]}
        
        if not other_users:
            st.info("No other adventurers registered yet!")
        else:
            # Use a unique form key to reset the form after sending
            form_key = f"send_message_form_{st.session_state.get('form_reset_counter', 0)}"
            
            with st.form(form_key):
                # Pre-select recipient if replying
                if st.session_state.replying_to:
                    recipient_options = [st.session_state.replying_to['sender_email']]
                    selected_recipient = st.session_state.replying_to['sender_email']
                    st.write(f"**Replying to:** {other_users[selected_recipient]['avatar']} {other_users[selected_recipient]['display_name']}")
                else:
                    # Recipient selection
                    recipient_options = list(other_users.keys())
                    selected_recipient = st.selectbox(
                        "Send to:",
                        recipient_options,
                        format_func=lambda x: f"{other_users[x]['avatar']} {other_users[x]['display_name']} ({x})"
                    )
                
                # Optional event sharing (not available for replies)
                selected_event_id = None
                if not st.session_state.replying_to:
                    st.write("**Optional: Share an Event**")
                    event_options = ["None"] + [f"{event['name']} - {next(day[1] for day in DAYS if day[0] == event['day'])}" 
                                              for event in st.session_state.events]
                    event_choice = st.selectbox("Share event:", event_options)
                    
                    if event_choice != "None":
                        # Find the event ID
                        for event in st.session_state.events:
                            event_label = f"{event['name']} - {next(day[1] for day in DAYS if day[0] == event['day'])}"
                            if event_label == event_choice:
                                selected_event_id = event['id']
                                break
                
                # Message content
                placeholder_text = "Your reply message..." if st.session_state.replying_to else "Greetings, fellow adventurer! Want to join my quest?"
                message_text = st.text_area("Message:", placeholder=placeholder_text, max_chars=500)
                
                # Send button
                button_text = "↩️ Send Reply" if st.session_state.replying_to else "🦅 Send Message"
                send_button = st.form_submit_button(button_text, type="primary")
                
                if send_button:
                    if not message_text.strip():
                        st.error("Please enter a message!")
                    else:
                        reply_to_id = st.session_state.replying_to['message_id'] if st.session_state.replying_to else None
                        
                        message_id = send_message(
                            st.session_state.current_user["email"], 
                            selected_recipient, 
                            message_text.strip(),
                            selected_event_id,
                            reply_to_id
                        )
                        
                        recipient_name = other_users[selected_recipient]['display_name']
                        if st.session_state.replying_to:
                            confirmation_text = f"Reply sent to {recipient_name}! 📨"
                        else:
                            confirmation_text = f"Message sent to {recipient_name}! 🦅"
                        
                        # Store confirmation and clear form
                        st.session_state.message_sent_confirmation = confirmation_text
                        st.session_state.replying_to = None
                        
                        # Reset form by incrementing counter
                        if "form_reset_counter" not in st.session_state:
                            st.session_state.form_reset_counter = 0
                        st.session_state.form_reset_counter += 1
                        
                        st.rerun()
    
    st.stop()

# Tavern Page
if st.session_state.current_page == "Tavern":
    st.header("🍺 The Tavern - Adventurer's Lounge")
    
    # Two column layout: chat history and send message (wider conversation area)
    chat_col, send_col = st.columns([7, 3])
    
    with chat_col:
        st.markdown("<h3 style='text-align: center;'>💬 Bar Chatter</h3>", unsafe_allow_html=True)
        
        tavern_messages = get_tavern_messages()
        
        if not tavern_messages:
            st.info("The tavern is empty! Be the first to start a conversation! 🍺")
        else:
            # Display all messages (newest first)
            for msg in reversed(tavern_messages):
                is_current_user = msg["user_email"] == st.session_state.current_user["email"]
                
                # Get class name with fallback for legacy messages
                user_class = msg.get('user_class')
                if not user_class:
                    # Fallback: get class from current user data
                    user_info = st.session_state.users.get(msg['user_email'], {})
                    user_avatar = user_info.get('avatar', msg.get('user_avatar', '🧙‍♂️'))
                    user_class = AVATAR_OPTIONS.get(user_avatar, 'Adventurer')
                
                # Create message container with styling
                message_bg = "#E8F4FD" if is_current_user else "#F8F4FF"
                
                # Create columns for cheers button and message content
                cheers_col, content_col = st.columns([1, 9])
                
                with cheers_col:
                    # Add vertical spacing to lower the button
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Check if current user has already voted
                    current_user_email = st.session_state.current_user["email"]
                    user_has_voted = current_user_email in msg.get("beer_users", [])
                    
                    button_text = "🍻" 
                    help_text = "Remove your beer vote" if user_has_voted else "Give this message a beer!"
                    
                    # Use standard Streamlit button styling like delete button
                    button_type = "primary" if user_has_voted else "secondary"
                    
                    if st.button(button_text, key=f"cheers_{msg['id']}", help=help_text, type=button_type):
                        # Toggle beer vote for the message
                        success = toggle_beer_for_message(msg["id"], current_user_email)
                        if success:
                            st.rerun()
                
                with content_col:
                    # Escape HTML in user content to prevent issues
                    escaped_message = html.escape(msg['message'])
                    escaped_user_name = html.escape(msg['user_name'])
                    escaped_user_class = html.escape(user_class)
                    
                    # Get beer count for this message
                    beer_count = msg.get("beer_count", 0)
                    
                    # Message content in styled container
                    st.markdown(f"""
                    <div style="background: {message_bg}; border: 2px solid #7B2CBF; 
                               border-radius: 10px; padding: 12px; margin: 5px 0;">
                        <div style="font-weight: bold; color: #7B2CBF; margin-bottom: 5px;">
                            {msg['user_avatar']} {escaped_user_name} | <em>"{escaped_user_class}"</em>
                        </div>
                        <div style="color: #333; margin-bottom: 8px;">
                            {escaped_message}
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="font-size: 12px; color: #666;">
                                {msg['timestamp']}
                            </div>
                            <div style="font-size: 12px; color: #7B2CBF; font-weight: bold;">
                                🍺 {beer_count}
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Add some spacing between messages
                st.markdown("<br>", unsafe_allow_html=True)
    
    with send_col:
        st.markdown("##### 📝 Yap Away")
        
        # Message input form
        with st.form("tavern_full_chat_form"):
            new_message = st.text_area("Your message:", 
                                     placeholder="Rase yer flagon ya cretin!", 
                                     max_chars=300, 
                                     height=120)
            
            send_message_btn = st.form_submit_button("🦅 Send Message", use_container_width=True)
            
            if send_message_btn:
                if new_message.strip():
                    send_tavern_message(st.session_state.current_user["email"], new_message.strip())
                    st.success("Message sent to the tavern! 🍺")
                    st.rerun()
                else:
                    st.error("Please enter a message!")
        
        # Refresh button
        if st.button("🔄 Refresh Tavern", use_container_width=True):
            st.rerun()
        
        # Hottest Bar Goss - messages with most beers
        st.markdown("---")
        
        # Flame-themed header
        st.markdown("""
        <div style="background: linear-gradient(135deg, #FF6B35 0%, #F7931E 25%, #FFD23F 50%, #F7931E 75%, #FF6B35 100%);
                   border: 3px solid #E85D04; border-radius: 15px; padding: 8px; margin: 10px 0;
                   box-shadow: inset 0 2px 4px rgba(255,255,255,0.3), 0 4px 8px rgba(0,0,0,0.3);
                   position: relative;">
            <div style="position: absolute; top: -5px; left: 5px; font-size: 20px;">🔥</div>
            <div style="position: absolute; top: -5px; right: 5px; font-size: 20px;">🔥</div>
            <div style="position: absolute; bottom: -5px; left: 15px; font-size: 16px;">🔥</div>
            <div style="position: absolute; bottom: -5px; right: 15px; font-size: 16px;">🔥</div>
            <h5 style="color: #8B1538; text-align: center; margin: 0; 
                     text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
                     font-family: 'Uncial Antiqua', 'Cinzel', serif;">
                Hot Bar Goss
            </h5>
        </div>
        """, unsafe_allow_html=True)
        
        tavern_messages = get_tavern_messages()
        if tavern_messages:
            # Sort messages by beer count (highest first) and take top 5
            sorted_messages = sorted(tavern_messages, key=lambda x: x.get('beer_count', 0), reverse=True)
            hottest_messages = sorted_messages[:5]
            
            for msg in hottest_messages:
                beer_count = msg.get('beer_count', 0)
                user_class = msg.get('user_class', 'Adventurer')
                if not user_class or user_class == 'Unknown':
                    # Fallback: get class from current user data
                    user_info = st.session_state.users.get(msg['user_email'], {})
                    user_avatar = user_info.get('avatar', msg.get('user_avatar', '🧙‍♂️'))
                    user_class = AVATAR_OPTIONS.get(user_avatar, 'Adventurer')
                
                # Flame-themed message container
                st.markdown(f"""
                <div style="border: 2px solid #FF6B35; border-radius: 8px; 
                           padding: 8px; margin: 4px 0; 
                           background: linear-gradient(135deg, #FFF8E7 0%, #FFE5B4 100%);
                           box-shadow: 0 2px 4px rgba(255, 107, 53, 0.3);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="font-weight: bold; color: #8B1538; font-size: 11px;">
                            {msg['user_avatar']} {msg['user_name']} | <i>"{user_class}"</i>
                        </div>
                        <div style="font-weight: bold; color: #E85D04; font-size: 12px;">
                            🍺 {beer_count}
                        </div>
                    </div>
                    <div style="color: #333; font-size: 12px; margin-top: 2px;">
                        "{msg['message'][:50]}{'...' if len(msg['message']) > 50 else ''}"
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.write("_No messages yet..._")
    
    st.stop()

# Profile Page
if st.session_state.current_page == "Profile":
    user = st.session_state.current_user
    
    # Show edit event form if editing
    if st.session_state.editing_event:
        event_to_edit = None
        for event in st.session_state.events:
            if event["id"] == st.session_state.editing_event:
                event_to_edit = event
                break
        
        if event_to_edit:
            st.header("✏️ Edit Quest")
            
            with st.form("edit_event_form"):
                edit_name = st.text_input("Quest Name:", value=event_to_edit["name"])
                edit_host = st.text_input("Quest Host/GM:", value=event_to_edit["host"])
                edit_day = st.selectbox("Select Day", DAYS, 
                                      index=[i for i, day in enumerate(DAYS) if day[0] == event_to_edit["day"]][0],
                                      format_func=lambda x: x[1])
                edit_start = st.selectbox("Start Time", TIME_SLOTS,
                                        index=TIME_SLOTS.index(event_to_edit["start"]))
                edit_end = st.selectbox("End Time", TIME_SLOTS,
                                      index=TIME_SLOTS.index(event_to_edit["end"]))
                edit_tag = st.selectbox("Event Tag", list(TAGS.keys()),
                                      index=list(TAGS.keys()).index(event_to_edit["tag"]))
                edit_system = st.text_input("Game System:", value=event_to_edit.get("game_system", ""))
                edit_min = st.number_input("Minimum Seats", min_value=1, max_value=100, 
                                         value=event_to_edit["seat_min"])
                edit_max = st.number_input("Maximum Seats", min_value=edit_min, max_value=100,
                                         value=event_to_edit["seat_max"])
                edit_desc = st.text_area("Quest Description", value=event_to_edit["description"], max_chars=300)
                
                col1, col2 = st.columns(2)
                with col1:
                    save_edit = st.form_submit_button("� Save Changes", type="primary")
                with col2:
                    cancel_edit = st.form_submit_button("❌ Cancel Edit")
                
                if save_edit:
                    start_dt = datetime.strptime(edit_start, "%I:%M %p")
                    end_dt = datetime.strptime(edit_end, "%I:%M %p")
                    if end_dt <= start_dt:
                        st.error("End time must be after start time.")
                    elif not edit_name.strip() or not edit_host.strip() or not edit_system.strip() or not edit_desc.strip():
                        st.error("All fields are required.")
                    else:
                        updated_data = {
                            "name": edit_name.strip(),
                            "host": edit_host.strip(),
                            "day": edit_day[0],
                            "start": edit_start,
                            "end": edit_end,
                            "tag": edit_tag,
                            "game_system": edit_system.strip(),
                            "seat_min": edit_min,
                            "seat_max": edit_max,
                            "description": edit_desc.strip()
                        }
                        update_event(st.session_state.editing_event, updated_data)
                        st.session_state.editing_event = None
                        st.success("Quest updated successfully! 🎯")
                        st.rerun()
                
                if cancel_edit:
                    st.session_state.editing_event = None
                    st.rerun()
            
            st.stop()
    
    st.header(f"{user['avatar']} {user['display_name']}'s Profile")
    
    col1, col2 = st.columns([5, 1])
    
    with col1:
        st.subheader("📅 Your Schedule")
        
        # Print and Download Buttons
        col_print, col_download = st.columns(2)
        
        with col_print:
            if st.button("🖨️ Print Schedule", use_container_width=True, help="Open clean print view"):
                print_html = generate_clean_print_html(user["email"])
                st.components.v1.html(print_html, height=0, scrolling=False)
        
        with col_download:
            pdf_content = generate_pdf_content(user["email"])
            st.download_button(
                label="📄 Download PDF",
                data=pdf_content.encode('utf-8'),
                file_name=f"{user['display_name']}_Bencon2026_Schedule.txt",
                mime="text/plain",
                use_container_width=True,
                help="Download clean text version"
            )
        
        user_rsvps = []
        hosted_events = get_user_hosted_events(user["email"])
        
        for event in st.session_state.events:
            if any(rsvp["email"] == user["email"] for rsvp in event.get("rsvps", [])):
                user_rsvps.append(event)
        
        all_user_events = user_rsvps.copy()
        # Add hosted events that user isn't participating in
        for hosted_event in hosted_events:
            if not any(rsvp["email"] == user["email"] for rsvp in hosted_event.get("rsvps", [])):
                all_user_events.append(hosted_event)
        
        if all_user_events:
            current_day = None
            for event in sorted(all_user_events, key=lambda e: (e["day"], e["start"])):
                day_name = next(day[1] for day in DAYS if day[0] == event["day"])
                tag_icon = TAGS.get(event["tag"], "📝")
                is_hosting = event.get("creator_email") == user["email"]
                
                # Add day separator and header if this is a new day
                if day_name != current_day:
                    if current_day is not None:  # Add divider between days (not before first day)
                        st.markdown("---")
                    
                    # Day header with medieval styling
                    st.markdown(f"""
                    <div style="text-align: center; margin: 20px 0; padding: 15px; 
                               background: linear-gradient(135deg, #7B2CBF 0%, #5A189A 100%); 
                               border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.3);
                               font-family: 'Cinzel', 'Old English Text MT', 'Blackletter', serif;
                               font-size: 24px; font-weight: bold; color: #C77DFF;
                               text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
                               border: 3px solid #C77DFF;">
                        ⚔️ {day_name} ⚔️
                    </div>
                    """, unsafe_allow_html=True)
                    current_day = day_name
                
                # Check if event is past
                is_past = is_event_past(event["day"], event["end"])
                strikethrough_style = "text-decoration: line-through; opacity: 0.7;" if is_past else ""
                
                # Create styled container for hosted events
                if is_hosting:
                    # Create a layered approach: gold container below, functional buttons on top
                    hosting_indicator = " 👑 (You're hosting)"
                    past_indicator = " [COMPLETED]" if is_past else ""
                    
                    # Create a unique ID for this container
                    container_id = f"gold_container_{event['id']}"
                    
                    # Position the gold container and buttons side by side
                    col_container, col_buttons = st.columns([4.5, 1.5])
                    
                    with col_container:
                        # Create the gold background container
                        st.markdown(f"""
                        <div id="{container_id}" style="border: 3px solid #FFD700; border-radius: 10px; padding: 15px; 
                                    background: linear-gradient(135deg, #FFF8DC 0%, #FFFACD 100%); 
                                    margin: 10px 0; box-shadow: 0 4px 8px rgba(255, 215, 0, 0.3);
                                    font-family: 'Cinzel', 'Times New Roman', serif; {strikethrough_style}">
                            <div style="font-size: 18px; font-weight: bold; margin-bottom: 8px; color: #8B4513; {strikethrough_style}">
                                {tag_icon} {event['name']}{hosting_indicator}{past_indicator}
                            </div>
                            <div style="font-size: 16px; font-weight: bold; margin-bottom: 4px; color: #2C3E50; {strikethrough_style}">
                                📅 {day_name} at {event['start']}-{event['end']}
                            </div>
                            <div style="font-size: 14px; margin-bottom: 8px; color: #34495E; {strikethrough_style}">
                                💻 System: {event.get('game_system', 'Not specified')}
                            </div>
                            <div style="font-size: 13px; margin-bottom: 8px; color: #5D6D7E; font-style: italic; {strikethrough_style}">
                                📖 {event['description']}
                            </div>
                            <div style="font-size: 12px; color: #7B68EE; {strikethrough_style}">
                                👥 Party: {len(event.get('rsvps', []))}/{event['seat_min']}-{event['seat_max']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_buttons:
                        # Center align the buttons container and add vertical spacing
                        st.markdown("""
                        <div style="display: flex; flex-direction: column; justify-content: center; height: 100%; gap: 10px;">
                        """, unsafe_allow_html=True)
                        
                        # Add some vertical spacing to center the buttons
                        st.write("")  
                        st.write("")  # Additional spacing for better centering
                        
                        # Edit button with blue fill
                        if st.button("✏️ Edit", key=f"edit_profile_{event['id']}", 
                                   help="Edit Event", use_container_width=True):
                            st.session_state.editing_event = event['id']
                            st.rerun()
                        # Delete button with red fill  
                        if st.button("🗑️ Delete", key=f"delete_profile_{event['id']}", 
                                   help="Delete Event", use_container_width=True):
                            delete_event(event['id'])
                            st.success(f"Event '{event['name']}' has been canceled.")
                            st.rerun()
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    # CSS to style the buttons with specified colors and proper targeting
                    st.markdown(f"""
                    <style>
                    /* Target the button container for better alignment */
                    div[data-testid="column"]:nth-child(2) {{
                        display: flex !important;
                        flex-direction: column !important;
                        justify-content: center !important;
                        align-items: center !important;
                        padding: 15px 10px !important;
                    }}
                    
                    /* Blue fill for edit button (first button) */
                    div[data-testid="column"]:nth-child(2) button:first-of-type {{
                        background-color: #3498DB !important;
                        color: white !important;
                        border: 2px solid #2980B9 !important;
                        font-weight: bold !important;
                        margin-bottom: 8px !important;
                    }}
                    div[data-testid="column"]:nth-child(2) button:first-of-type:hover {{
                        background-color: #2980B9 !important;
                        transform: scale(1.05) !important;
                        box-shadow: 0 4px 12px rgba(52, 152, 219, 0.4) !important;
                    }}
                    
                    /* Red fill for delete button (second button) */  
                    div[data-testid="column"]:nth-child(2) button:last-of-type {{
                        background-color: #E74C3C !important;
                        color: white !important;
                        border: 2px solid #C0392B !important;
                        font-weight: bold !important;
                    }}
                    div[data-testid="column"]:nth-child(2) button:last-of-type:hover {{
                        background-color: #C0392B !important;
                        transform: scale(1.05) !important;
                        box-shadow: 0 4px 12px rgba(231, 76, 60, 0.4) !important;
                    }}
                    </style>
                    """, unsafe_allow_html=True)
                else:
                    # White container styling for attending events (same format as gold container)
                    past_indicator = " [COMPLETED]" if is_past else ""
                    
                    # Create a unique ID for this container
                    container_id = f"white_container_{event['id']}"
                    
                    # Position the white container and abandon button side by side
                    col_container, col_buttons = st.columns([4.5, 1.5])
                    
                    with col_container:
                        # Create the white background container
                        st.markdown(f"""
                        <div id="{container_id}" style="border: 3px solid #CCCCCC; border-radius: 10px; padding: 15px; 
                                    background: linear-gradient(135deg, #FFFFFF 0%, #F8F9FA 100%); 
                                    margin: 10px 0; box-shadow: 0 4px 8px rgba(204, 204, 204, 0.3);
                                    font-family: 'Cinzel', 'Times New Roman', serif; {strikethrough_style}">
                            <div style="font-size: 18px; font-weight: bold; margin-bottom: 8px; color: #495057; {strikethrough_style}">
                                {tag_icon} {event['name']}{past_indicator}
                            </div>
                            <div style="font-size: 16px; font-weight: bold; margin-bottom: 4px; color: #2C3E50; {strikethrough_style}">
                                📅 {day_name} at {event['start']}-{event['end']}
                            </div>
                            <div style="font-size: 14px; margin-bottom: 8px; color: #495057; {strikethrough_style}">
                                🎭 Host: {event['host']}
                            </div>
                            <div style="font-size: 14px; margin-bottom: 8px; color: #34495E; {strikethrough_style}">
                                💻 System: {event.get('game_system', 'Not specified')}
                            </div>
                            <div style="font-size: 13px; margin-bottom: 8px; color: #5D6D7E; font-style: italic; {strikethrough_style}">
                                📖 {event['description']}
                            </div>
                            <div style="font-size: 12px; color: #6F42C1; {strikethrough_style}">
                                👥 Party: {len(event.get('rsvps', []))}/{event['seat_min']}-{event['seat_max']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_buttons:
                        # Add CSS to properly center the abandon button container
                        st.markdown("""
                        <style>
                        /* Target the white container button column for proper centering */
                        .white-container-buttons {
                            display: flex !important;
                            flex-direction: column !important;
                            justify-content: center !important;
                            align-items: center !important;
                            height: 150px !important; /* Match approximate height of white container */
                            padding: 15px 10px !important;
                        }
                        </style>
                        """, unsafe_allow_html=True)
                        
                        # Create a container with the centering class
                        st.markdown('<div class="white-container-buttons">', unsafe_allow_html=True)
                        
                        # Store cancel message in session state for consistency
                        message_key = f"cancel_msg_profile_{event['id']}"
                        if message_key not in st.session_state:
                            st.session_state[message_key] = random.choice(CANCEL_MESSAGES)
                    
                        cancel_message = st.session_state[message_key]
                        
                        # Abandon quest button with red styling
                        if st.button(f"{cancel_message}", key=f"abandon_profile_{event['id']}", 
                                   help="Click to abandon quest!", use_container_width=True):
                            cancel_rsvp(event['id'], user["email"])
                            # Clear the stored message so a new one appears next time they join
                            if message_key in st.session_state:
                                del st.session_state[message_key]
                            st.success(f"You have abandoned the quest '{event['name']}'.")
                            st.rerun()
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    # CSS to style the abandon button with red color
                    st.markdown(f"""
                    <style>
                    /* Red fill for abandon button */  
                    button[key*="abandon_profile_{event['id']}"] {{
                        background-color: #DC3545 !important;
                        color: white !important;
                        border: 2px solid #C82333 !important;
                        font-weight: bold !important;
                    }}
                    button[key*="abandon_profile_{event['id']}"]:hover {{
                        background-color: #C82333 !important;
                        transform: scale(1.05) !important;
                        box-shadow: 0 4px 12px rgba(220, 53, 69, 0.4) !important;
                    }}
                    </style>
                    """, unsafe_allow_html=True)
        else:
            st.write("_You haven't joined any quests yet. Time for an adventure!_ 🗺️")
    
    st.stop()

# Quest Counter Page  
if st.session_state.current_page == "Quest Counter":
    # Event Creation Form
    st.header("📝 Create a New Quest")
        
    # Use form_submitted flag to generate a unique key to clear the form
    form_key = f"event_form_{st.session_state.form_submitted}"
    
    # Reset form submitted flag after using it for the key
    if st.session_state.form_submitted:
        st.session_state.form_submitted = False

    with st.form(form_key):
            event_name = st.text_input("Quest Name:", placeholder="e.g., Dragons & Dungeons Adventure")
            event_host = st.text_input("Quest Host/GM:", value=st.session_state.current_user['display_name'])
            day = st.selectbox("Select Day", DAYS, format_func=lambda x: x[1])
            start_time = st.selectbox("Start Time", TIME_SLOTS)
            end_time = st.selectbox("End Time", TIME_SLOTS, index=min(len(TIME_SLOTS)-1, 2))
            tag = st.selectbox("Event Tag", list(TAGS.keys()))
            game_system = st.text_input("Game System:", placeholder="e.g., D&D 5e, Pathfinder, etc.")
            
            # Participation option
            participation = st.radio(
                "Are You Just Hosting This Event or Are You In the Headcount?",
                ["I'm just hosting", "I'm participating and part of the headcount"],
                help="Choose whether you count toward the minimum/maximum seats"
            )
            
            seat_min = st.number_input("Minimum Seats", min_value=1, max_value=100, value=2)
            seat_max = st.number_input("Maximum Seats", min_value=seat_min, max_value=100, value=6)
            description = st.text_area("Quest Description (include what is happening and any materials needed)", max_chars=300)
            submit = st.form_submit_button("Create Quest")

    # Validation
    if submit:
        start_dt = datetime.strptime(start_time, "%I:%M %p")
        end_dt = datetime.strptime(end_time, "%I:%M %p")
        if end_dt <= start_dt:
            st.error("End time must be after start time.")
        elif not event_name.strip():
            st.error("Quest name is required.")
        elif not event_host.strip():
            st.error("Quest host is required.")
        elif not game_system.strip():
            st.error("Game system is required.")
        elif not description.strip():
            st.error("Description is required.")
        else:
            event_id = str(uuid.uuid4())
            new_event = {
                "id": event_id,
                "name": event_name.strip(),
                "host": event_host.strip(),
                "day": day[0],
                "start": start_time,
                "end": end_time,
                "tag": tag,
                "game_system": game_system.strip(),
                "seat_min": seat_min,
                "seat_max": seat_max,
                "description": description.strip(),
                "creator_email": st.session_state.current_user['email'],
                "creator_name": st.session_state.current_user['display_name'],
                "rsvps": []
            }
            
            # Auto-join if participating
            if participation == "I'm participating and part of the headcount":
                user_rsvp = {
                    "email": st.session_state.current_user["email"], 
                    "display_name": st.session_state.current_user["display_name"],
                    "avatar": st.session_state.current_user.get("avatar", "🧙‍♂️")
                }
                new_event["rsvps"].append(user_rsvp)
            
            st.session_state.events.append(new_event)
            
            # Save event to database
            save_to_database("events", {
                "id": new_event["id"],
                "title": new_event["title"],
                "description": new_event["description"],
                "date": new_event["date"],
                "time": new_event["time"],
                "location": new_event["location"],
                "host_email": new_event["creator_email"],
                "tags": new_event["tags"],
                "max_attendees": new_event.get("max_attendees", 50)
            })
            
            # Save RSVP if auto-joining
            if new_event.get("rsvps"):
                for rsvp in new_event["rsvps"]:
                    save_to_database("rsvps", {
                        "id": str(uuid.uuid4()),
                        "event_id": new_event["id"],
                        "user_email": rsvp["email"],
                        "status": "yes"
                    })
            
            # Show balloons first
            st.balloons()
            
            # Add dragon and sword confetti effect
            st.components.v1.html("""
                <div id="confetti-container"></div>
                <script>
                function createDragonSwordConfetti() {
                    const symbols = ['🐉', '⚔️', '🗡️', '🛡️', '🏹', '🔥'];
                    
                    for (let i = 0; i < 50; i++) {
                        setTimeout(() => {
                            const confetti = document.createElement('div');
                            confetti.innerHTML = symbols[Math.floor(Math.random() * symbols.length)];
                            confetti.style.position = 'fixed';
                            confetti.style.left = Math.random() * 100 + 'vw';
                            confetti.style.top = '-50px';
                            confetti.style.fontSize = (Math.random() * 30 + 25) + 'px';
                            confetti.style.zIndex = '999999';
                            confetti.style.pointerEvents = 'none';
                            confetti.style.transform = 'rotate(' + (Math.random() * 360) + 'deg)';
                            
                            // Add to body
                            document.body.appendChild(confetti);
                            
                            // Animate the fall
                            let pos = -50;
                            let rotation = Math.random() * 360;
                            const fall = setInterval(() => {
                                pos += 8;
                                rotation += 10;
                                confetti.style.top = pos + 'px';
                                confetti.style.transform = 'rotate(' + rotation + 'deg)';
                                
                                if (pos > window.innerHeight + 100) {
                                    clearInterval(fall);
                                    if (confetti.parentNode) {
                                        confetti.parentNode.removeChild(confetti);
                                    }
                                }
                            }, 50);
                            
                        }, i * 150);
                    }
                }
                
                // Start the confetti immediately
                createDragonSwordConfetti();
                </script>
                """, height=0)
            
            # Create a popup-style message
            st.markdown("""
            <div style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); 
                       background: linear-gradient(135deg, #2ECC71, #27AE60); color: white; 
                       padding: 20px 30px; border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.3);
                       text-align: center; font-size: 18px; font-weight: bold; z-index: 9999;
                       border: 3px solid #FFD700;">
                🎉 Quest Created Successfully! 🎯<br/>
                <span style="font-size: 14px; font-weight: normal;">Your epic adventure awaits!</span>
            </div>
            """, unsafe_allow_html=True)
            
            # Set flag to clear form on next render
            st.session_state.form_submitted = True
            
            # Auto-clear the popup and refresh
            import time
            time.sleep(2)
            st.rerun()

    # Available Events Display - with wider container
    st.markdown('<div class="quest-section-wide">', unsafe_allow_html=True)
    st.subheader("🗓️ All Available Quests (Thursday - Saturday)")
    st.markdown("*Browse all quests and join adventures!*")

    for day_key, day_label in DAYS:
        # Fantasy styled day header
        st.markdown(f'<div class="fantasy-day-header">⚔️ {day_label} ⚔️</div>', unsafe_allow_html=True)
        
        # Show ALL events (including user's own)
        day_events = [e for e in st.session_state.events if e["day"] == day_key]
        if not day_events:
            st.write("_No quests yet for this day._")
        else:
            for event in sorted(day_events, key=lambda e: e["start"]):
                    # Get RSVP info
                    rsvps = event.get("rsvps", [])
                    current_count = len(rsvps)
                    is_user_rsvped = any(rsvp["email"] == st.session_state.current_user["email"] for rsvp in rsvps)
                    is_full = current_count >= event["seat_max"]
                    can_rsvp = not is_user_rsvped and not is_full and current_count < event["seat_max"]
                    
                    # Status indicators
                    if current_count < event["seat_min"]:
                        status = "🔴 Needs more adventurers"
                    elif current_count >= event["seat_min"] and current_count < event["seat_max"]:
                        status = "🟡 Ready to go (spots available)"
                    else:
                        status = "🟢 Party is full"
                    
                    # Display event
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        tag_icon = TAGS.get(event["tag"], "📝")
                        is_host = event.get("creator_email") == st.session_state.current_user["email"]
                        host_display = f"**🎭 Host/GM:** {event['host']}" if not is_host else f"**🎭 Host/GM:** <mark style='background-color: #FFD700; padding: 2px 4px; border-radius: 3px;'>{event['host']} (You)</mark>"
                        
                        st.markdown(f"""
**{tag_icon} {event['name']}**  
{host_display}  
**🕐 {event['start']} - {event['end']}** | **Tag:** `{event['tag']}`  
**💻 System:** {event.get('game_system', 'Not specified')}  
**Party Size:** {current_count}/{event['seat_min']}-{event['seat_max']} | {status}  
**Description:** {event['description']}
""", unsafe_allow_html=True)
                        
                        # Show RSVPs with avatars
                        if rsvps:
                            rsvp_display = []
                            for rsvp in rsvps:
                                avatar = rsvp.get("avatar", "🧙‍♂️")
                                avatar_name = AVATAR_OPTIONS.get(avatar, "Unknown")
                                avatar_html = f'<span title="{avatar_name}">{avatar}</span>'
                                rsvp_display.append(f"{avatar_html} {rsvp['display_name']}")
                            
                            st.markdown(f"**Adventurers signed up:** {', '.join(rsvp_display)}", unsafe_allow_html=True)
                    
                    with col2:
                        # RSVP and Share buttons
                        if can_rsvp:
                            # Regular join button
                            join_button = st.button(f"Join Quest ⚔️", key=f"join_{event['id']}", 
                                                  help="Click to join this epic adventure!")
                            if join_button:
                                rsvp_to_event(event['id'], st.session_state.current_user)
                                st.rerun()
                        elif is_user_rsvped:
                            # Show only "IN PARTY" status without cancel button (moved to Profile page)
                            st.markdown(f"""
                            <div style="text-align: center;">
                                <p style="margin: 0; padding: 10px; background: linear-gradient(45deg, #8B4513, #654321); 
                                   color: white; border-radius: 5px; font-size: 14px; font-weight: bold;
                                   background-image: 
                                       radial-gradient(circle at 20% 50%, transparent 20%, rgba(139, 69, 19, 0.3) 21%, rgba(139, 69, 19, 0.3) 34%, transparent 35%),
                                       linear-gradient(0deg, rgba(160, 82, 45, 0.8) 50%, rgba(139, 69, 19, 0.8) 50%);
                                   background-size: 15px 15px, 20px 20px;
                                   text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
                                   border: 2px solid #654321;">
                                    🗡️ IN PARTY 🛡️
                                </p>
                                <p style="margin: 5px 0 0 0; font-size: 11px; color: #666; font-style: italic;">
                                    Visit your Profile to abandon quest
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                        elif is_full:
                            st.markdown("""
                            <div style="text-align: center; padding: 10px; background-color: #6c757d; 
                               color: white; border-radius: 5px; font-weight: bold;">
                                🚫 PARTY FULL 🚫
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Share Event button (always available)
                        if st.button("📤 Share Quest", key=f"share_{event['id']}", 
                                   help="Send this quest to another adventurer", use_container_width=True):
                            # Show quick share dialog
                            st.session_state[f"show_share_{event['id']}"] = True
                            st.rerun()
                        
                        # Quick share dialog
                        if st.session_state.get(f"show_share_{event['id']}", False):
                            with st.expander("📤 Quick Share", expanded=True):
                                other_users = {email: user for email, user in st.session_state.users.items() 
                                             if email != st.session_state.current_user["email"]}
                                
                                if other_users:
                                    share_recipient = st.selectbox(
                                        "Send to:",
                                        list(other_users.keys()),
                                        format_func=lambda x: f"{other_users[x]['avatar']} {other_users[x]['display_name']}",
                                        key=f"share_recipient_{event['id']}"
                                    )
                                    
                                    share_message = st.text_input(
                                        "Message (optional):",
                                        value=f"Hey! Check out this quest: {event['name']}",
                                        key=f"share_message_{event['id']}"
                                    )
                                    
                                    col_send, col_cancel = st.columns(2)
                                    with col_send:
                                        if st.button("🦅 Send", key=f"send_share_{event['id']}", use_container_width=True):
                                            send_message(
                                                st.session_state.current_user["email"],
                                                share_recipient,
                                                share_message,
                                                event['id']
                                            )
                                            st.success(f"Quest shared with {other_users[share_recipient]['display_name']}!")
                                            st.session_state[f"show_share_{event['id']}"] = False
                                            st.rerun()
                                    
                                    with col_cancel:
                                        if st.button("❌ Cancel", key=f"cancel_share_{event['id']}", use_container_width=True):
                                            st.session_state[f"show_share_{event['id']}"] = False
                                            st.rerun()
                                else:
                                    st.info("No other adventurers to share with!")
                                    if st.button("Close", key=f"close_share_{event['id']}", use_container_width=True):
                                        st.session_state[f"show_share_{event['id']}"] = False
                                        st.rerun()
                    
                    st.divider()
    
        # Close the wide container
        st.markdown('</div>', unsafe_allow_html=True)
    


