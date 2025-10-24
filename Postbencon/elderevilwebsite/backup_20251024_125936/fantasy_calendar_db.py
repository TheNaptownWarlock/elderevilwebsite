# Fantasy Calendar Database Setup with SQLite
import sqlite3
import json
from datetime import datetime
from pathlib import Path

class FantasyCalendarDB:
    def __init__(self, db_path="fantasy_calendar.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with all necessary tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users/Profiles table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            display_name TEXT,
            character_class TEXT,
            avatar_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Events table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            event_date DATE NOT NULL,
            event_time TIME,
            creator_id INTEGER,
            location TEXT,
            max_attendees INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (creator_id) REFERENCES users (id)
        )
        ''')
        
        # RSVPs table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS rsvps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER,
            user_id INTEGER,
            status TEXT CHECK(status IN ('yes', 'no', 'maybe')),
            rsvp_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT,
            FOREIGN KEY (event_id) REFERENCES events (id),
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(event_id, user_id)
        )
        ''')
        
        # Tavern Chat table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tavern_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            message TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # Activity Log table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            activity_type TEXT,
            activity_description TEXT,
            related_event_id INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (related_event_id) REFERENCES events (id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, username, display_name=None, character_class=None):
        """Add a new user profile"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO users (username, display_name, character_class)
            VALUES (?, ?, ?)
            ''', (username, display_name or username, character_class))
            
            user_id = cursor.lastrowid
            conn.commit()
            return user_id
        except sqlite3.IntegrityError:
            return None  # User already exists
        finally:
            conn.close()
    
    def create_event(self, title, event_date, creator_username, description=None, event_time=None):
        """Create a new event"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get creator ID
        cursor.execute('SELECT id FROM users WHERE username = ?', (creator_username,))
        creator = cursor.fetchone()
        if not creator:
            conn.close()
            return None
        
        creator_id = creator[0]
        
        cursor.execute('''
        INSERT INTO events (title, description, event_date, event_time, creator_id)
        VALUES (?, ?, ?, ?, ?)
        ''', (title, description, event_date, event_time, creator_id))
        
        event_id = cursor.lastrowid
        
        # Log activity
        cursor.execute('''
        INSERT INTO activity_log (user_id, activity_type, activity_description, related_event_id)
        VALUES (?, ?, ?, ?)
        ''', (creator_id, 'event_created', f'Created event: {title}', event_id))
        
        conn.commit()
        conn.close()
        return event_id
    
    def rsvp_to_event(self, event_id, username, status, notes=None):
        """RSVP to an event"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get user ID
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        if not user:
            conn.close()
            return False
        
        user_id = user[0]
        
        # Insert or update RSVP
        cursor.execute('''
        INSERT OR REPLACE INTO rsvps (event_id, user_id, status, notes, rsvp_date)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (event_id, user_id, status, notes))
        
        # Log activity
        cursor.execute('''
        INSERT INTO activity_log (user_id, activity_type, activity_description, related_event_id)
        VALUES (?, ?, ?, ?)
        ''', (user_id, 'rsvp_updated', f'RSVPed {status} to event', event_id))
        
        conn.commit()
        conn.close()
        return True
    
    def get_events(self, date=None):
        """Get events, optionally filtered by date"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if date:
            cursor.execute('''
            SELECT e.*, u.display_name as creator_name
            FROM events e
            JOIN users u ON e.creator_id = u.id
            WHERE e.event_date = ?
            ORDER BY e.event_time
            ''', (date,))
        else:
            cursor.execute('''
            SELECT e.*, u.display_name as creator_name
            FROM events e
            JOIN users u ON e.creator_id = u.id
            ORDER BY e.event_date, e.event_time
            ''')
        
        events = cursor.fetchall()
        conn.close()
        return events
    
    def get_rsvps_for_event(self, event_id):
        """Get all RSVPs for an event"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT r.*, u.display_name, u.character_class
        FROM rsvps r
        JOIN users u ON r.user_id = u.id
        WHERE r.event_id = ?
        ORDER BY r.rsvp_date
        ''', (event_id,))
        
        rsvps = cursor.fetchall()
        conn.close()
        return rsvps
    
    def add_tavern_message(self, username, message):
        """Add a message to the tavern chat"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get user ID
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        if not user:
            conn.close()
            return False
        
        user_id = user[0]
        
        cursor.execute('''
        INSERT INTO tavern_messages (user_id, message)
        VALUES (?, ?)
        ''', (user_id, message))
        
        conn.commit()
        conn.close()
        return True
    
    def get_recent_activity(self, limit=10):
        """Get recent activity for the 'Hottest Bar Goss'"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT a.*, u.display_name, e.title as event_title
        FROM activity_log a
        JOIN users u ON a.user_id = u.id
        LEFT JOIN events e ON a.related_event_id = e.id
        ORDER BY a.timestamp DESC
        LIMIT ?
        ''', (limit,))
        
        activities = cursor.fetchall()
        conn.close()
        return activities

# Example usage for your Streamlit app
if __name__ == "__main__":
    # Initialize database
    db = FantasyCalendarDB()
    
    # Add sample data
    user_id = db.add_user("TheNaptownWarlock", "The Naptown Warlock", "Warlock")
    if user_id:
        event_id = db.create_event(
            "Epic D&D Session", 
            "2025-10-28", 
            "TheNaptownWarlock",
            "Join us for an epic adventure!",
            "19:00"
        )
        
        print(f"Created user ID: {user_id}")
        print(f"Created event ID: {event_id}")