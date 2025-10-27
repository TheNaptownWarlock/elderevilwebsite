import streamlit as st
from datetime import datetime, timedelta
import uuid
import random
import json
import hashlib
import html
import os

# Configure Streamlit for subdirectory deployment
st.set_page_config(
    page_title="Bencon Fantasy Calendar",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# SSL configuration for Windows
import ssl
import urllib3
import os

# Disable SSL warnings for development
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Set environment variables to bypass SSL
os.environ['PYTHONHTTPSVERIFY'] = '0'
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''

# Set SSL context to be more permissive
ssl._create_default_https_context = ssl._create_unverified_context

# Supabase credentials will be loaded when needed

def get_supabase_credentials():
    """Get Supabase credentials safely"""
    try:
        return st.secrets.get("SUPABASE_URL", ""), st.secrets.get("SUPABASE_KEY", "")
    except:
        return "", ""

# Comprehensive requests SSL bypass
try:
    import requests
    requests.packages.urllib3.disable_warnings()
    
    # Monkey patch requests to disable SSL verification globally
    original_request = requests.Session.request
    def patched_request(self, method, url, **kwargs):
        kwargs['verify'] = False
        kwargs.pop('cert', None)  # Remove cert verification
        return original_request(self, method, url, **kwargs)
    requests.Session.request = patched_request
    
    # Also patch the get, post, put, delete methods
    original_get = requests.get
    original_post = requests.post
    original_put = requests.put
    original_delete = requests.delete
    
    def patched_get(url, **kwargs):
        kwargs['verify'] = False
        return original_get(url, **kwargs)
    
    def patched_post(url, **kwargs):
        kwargs['verify'] = False
        return original_post(url, **kwargs)
        
    def patched_put(url, **kwargs):
        kwargs['verify'] = False
        return original_put(url, **kwargs)
        
    def patched_delete(url, **kwargs):
        kwargs['verify'] = False
        return original_delete(url, **kwargs)
    
    requests.get = patched_get
    requests.post = patched_post  
    requests.put = patched_put
    requests.delete = patched_delete
    
except ImportError:
    pass

# Supabase imports
from supabase import create_client, Client
import threading
import time

# Initialize Supabase client (no caching to avoid SSL issues)
def init_supabase():
    """Initialize Supabase client using credentials from secrets"""
    try:
        # Debug: Check if secrets are available
        st.info("🔗 Attempting to load Supabase credentials...")
        
        # Check secrets object
        if not hasattr(st, 'secrets'):
            st.error("Streamlit secrets object not available")
            return None
        
        # Debug: Show all available secrets
        try:
            available_keys = list(st.secrets.keys()) if st.secrets else []
            st.info(f"Available secret keys: {available_keys}")
        except Exception as debug_e:
            st.warning(f"Could not list secret keys: {debug_e}")
        
        # Try multiple ways to get the credentials
        supabase_url = ""
        supabase_key = ""
        
        # Method 1: Direct access
        try:
            raw_url = st.secrets["SUPABASE_URL"]
            raw_key = st.secrets["SUPABASE_KEY"]
            
            st.info(f"Raw URL from secrets: '{raw_url}' (type: {type(raw_url)}, len: {len(str(raw_url))})")
            st.info(f"Raw Key from secrets: '{str(raw_key)[:20]}...' (type: {type(raw_key)}, len: {len(str(raw_key))})")
            
            supabase_url = str(raw_url)
            supabase_key = str(raw_key)
            st.info("✅ Method 1: Direct access worked")
        except Exception as e1:
            st.warning(f"Method 1 failed: {e1}")
        
        # Clean and validate credentials
        supabase_url = str(supabase_url).strip().strip('"').strip("'")
        supabase_key = str(supabase_key).strip().strip('"').strip("'")
        
        # Debug output after cleaning
        st.info(f"After cleaning - URL: '{supabase_url[:50]}...'" if supabase_url else "After cleaning - URL: Empty")
        st.info(f"After cleaning - Key: '{supabase_key[:20]}...'" if supabase_key else "After cleaning - Key: Empty")
        
        # If still empty, use the hardcoded values you provided
        if not supabase_url or not supabase_key or len(supabase_url) == 0 or len(supabase_key) == 0:
            st.warning("⚠️ Secrets are empty, using provided credentials...")
            supabase_url = "https://uvsdbuonyfzajhtrgnxq.supabase.co"
            supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV2c2RidW9ueWZ6YWpodHJnbnhxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEwNjUxNjgsImV4cCI6MjA3NjY0MTE2OH0.tq_dQfCIl68bSt2BUPP0lWW2DjjwPpxcKV6LIt2LRFg"
            st.info(f"✅ Using hardcoded URL: {supabase_url}")
            st.info(f"✅ Using hardcoded Key: {supabase_key[:20]}...")
        
        if not supabase_url or not supabase_key:
            st.error("❌ Supabase credentials are empty")
            return None
            
        # Create custom options for Supabase client that bypasses SSL
        import os
        
        # Set additional environment variables for SSL bypass
        os.environ['PYTHONHTTPSVERIFY'] = '0'
        os.environ['CURL_CA_BUNDLE'] = ''
        os.environ['REQUESTS_CA_BUNDLE'] = ''
        os.environ['SSL_CERT_FILE'] = ''
        os.environ['SSL_CERT_DIR'] = ''
        
        # Try to create client with custom httpx client that doesn't verify SSL
        try:
            import httpx
            
            # Create httpx client with SSL verification disabled
            custom_http_client = httpx.Client(
                verify=False,
                timeout=30.0
            )
            
            # Create Supabase client with custom options
            from supabase.lib.client_options import ClientOptions
            
            options = ClientOptions(
                schema="public",
                headers={},
                auto_refresh_token=True,
                persist_session=True
            )
            
            client = create_client(supabase_url, supabase_key, options)
            
            # Force override the HTTP client
            if hasattr(client, '_rest_client'):
                client._rest_client._client = custom_http_client
                st.success("🔧 Custom httpx client applied!")
            
        except ImportError:
            # Fallback: Create standard client and modify sessions
            client = create_client(supabase_url, supabase_key)
            
            # Apply requests session modifications
            import requests
            
            # Find and modify all requests sessions
            def modify_session(obj, path=""):
                if hasattr(obj, 'session') and isinstance(obj.session, requests.Session):
                    obj.session.verify = False
                    obj.session.trust_env = False
                    st.info(f"🔧 Modified session at {path}")
                
                for attr_name in dir(obj):
                    if not attr_name.startswith('_'):
                        try:
                            attr = getattr(obj, attr_name)
                            if hasattr(attr, '__dict__'):
                                modify_session(attr, f"{path}.{attr_name}")
                        except:
                            pass
            
            modify_session(client, "client")
        
        st.success("✅ Supabase client created with SSL bypass!")
        return client
        
    except Exception as e:
        st.error(f"❌ Failed to initialize Supabase: {e}")
        return None

# Skip Supabase client initialization - using direct API calls to avoid SSL issues
supabase = None  # We'll use direct API calls instead

# Database initialization and persistence functions (now using Supabase)

def init_database():
    """Initialize the database - Using direct API calls to avoid SSL issues"""
    try:
        # Test Supabase connection using direct API (bypasses SSL issues)
        import requests
        requests.packages.urllib3.disable_warnings()
        
        base_url = "https://uvsdbuonyfzajhtrgnxq.supabase.co"
        api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV2c2RidW9ueWZ6YWpodHJnbnhxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEwNjUxNjgsImV4cCI6MjA3NjY0MTE2OH0.tq_dQfCIl68bSt2BUPP0lWW2DjjwPpxcKV6LIt2LRFg"
        
        headers = {
            'apikey': api_key,
            'Authorization': f'Bearer {api_key}'
        }
        
        # Test connection by trying to access users table
        url = f"{base_url}/rest/v1/users?limit=1"
        response = requests.get(url, headers=headers, verify=False)
        
        if response.status_code == 200:
            print("✅ Supabase connected via direct API!")
            return True
        else:
            print(f"❌ Supabase API test failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    else:
        # Fallback to SQLite for local development
        print("🔄 Using local SQLite database (Supabase not available)")
        import sqlite3
        conn = sqlite3.connect("bencon_calendar.db")
        cursor = conn.cursor()
        
        # Create SQLite tables as fallback
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            password_hash TEXT,
            display_name TEXT,
            avatar TEXT,
            pronouns TEXT,
            bio TEXT,
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
            seat_min INTEGER DEFAULT 1,
            seat_max INTEGER DEFAULT 1,
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
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
        st.info("✅ SQLite database initialized")
        return True

def save_to_database(table, data):
    """Save data to Supabase using direct API calls"""
    print(f"🔍 DEBUG: save_to_database called for table: {table}")
    print(f"🔍 DEBUG: Data received: {data}")
    # Always use direct API calls to avoid SSL issues with the client
    return save_to_supabase(table, data)

def save_to_supabase(table, data):
    """Save data to Supabase using direct API calls (bypassing the Python client)"""
    
    try:
        print(f"🔄 Attempting to save to Supabase table: {table} using direct API")
        
        # Use direct requests API calls instead of Supabase client
        import requests
        import json
        
        # Disable SSL warnings and verification completely
        requests.packages.urllib3.disable_warnings()
        
        # Supabase API endpoints
        base_url = "https://uvsdbuonyfzajhtrgnxq.supabase.co"
        api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV2c2RidW9ueWZ6YWpodHJnbnhxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEwNjUxNjgsImV4cCI6MjA3NjY0MTE2OH0.tq_dQfCIl68bSt2BUPP0lWW2DjjwPpxcKV6LIt2LRFg"
        
        headers = {
            'apikey': api_key,
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal'
        }
        
        if table == "users":
            # Prepare user data for Supabase
            user_data = {
                "email": data["email"],
                "password_hash": data["password_hash"], 
                "display_name": data["display_name"],
                "avatar": data["avatar"],
                "pronouns": data["pronouns"],
                "bio": data.get("bio", "")  # Include bio field
            }
            print(f"DEBUG: User data being sent: {user_data}")
            # Direct API call to Supabase
            url = f"{base_url}/rest/v1/{table}"
            print(f"DEBUG: Making POST request to: {url}")
            response = requests.post(url, headers=headers, json=user_data, verify=False)
            print(f"DEBUG: Response status: {response.status_code}")
            print(f"DEBUG: Response text: {response.text}")
            
            if response.status_code in [200, 201]:
                print("DEBUG: User saved successfully!")
                return True
            else:
                print(f"❌ API Error {response.status_code}: {response.text}")
                return False
        
        elif table == "events":
            # Prepare event data for Supabase
            event_data = {
                "id": data["id"],
                "title": data["title"],
                "description": data["description"],
                "date": data["date"],
                "time": data["time"],
                "end_time": data.get("end_time", ""),  # Add end_time field
                "location": data["location"],
                "host_email": data["host_email"],
                "tags": json.dumps(data["tags"]) if isinstance(data["tags"], list) else data["tags"],
                "game_system": data.get("game_system", "Not specified"),
                # Include seat_min/seat_max if provided; set max_attendees from seat_max for compatibility
                "seat_min": data.get("seat_min", 1),
                "seat_max": data.get("seat_max", data.get("max_attendees", 1)),
                "max_attendees": data.get("max_attendees", data.get("seat_max", 1))
            }
            print(f"DEBUG: Event data being sent: {event_data}")
            # Direct API call to Supabase
            url = f"{base_url}/rest/v1/{table}"
            print(f"DEBUG: Making POST request to: {url}")
            response = requests.post(url, headers=headers, json=event_data, verify=False)
            print(f"DEBUG: Response status: {response.status_code}")
            print(f"DEBUG: Response text: {response.text}")
            
            if response.status_code in [200, 201]:
                print("DEBUG: Event saved successfully!")
                return True
            else:
                print(f"❌ API Error {response.status_code}: {response.text}")
                return False
        
        elif table == "rsvps":
            # Prepare RSVP data for Supabase
            rsvp_data = {
                "id": data["id"],
                "event_id": data["event_id"],
                "user_email": data["user_email"],
                "status": data["status"]
            }
            # Direct API call to Supabase
            url = f"{base_url}/rest/v1/{table}"
            response = requests.post(url, headers=headers, json=rsvp_data, verify=False)
            
            if response.status_code in [200, 201]:
                return True
            else:
                print(f"❌ API Error {response.status_code}: {response.text}")
                return False
        
        elif table == "tavern_messages":
            # Prepare tavern message for Supabase
            message_data = {
                "id": data["id"],
                "user_email": data["user_email"],
                "message": data["message"]
            }
            print(f"DEBUG: Tavern message data being sent: {message_data}")
            # Direct API call to Supabase
            url = f"{base_url}/rest/v1/{table}"
            print(f"DEBUG: Making POST request to: {url}")
            response = requests.post(url, headers=headers, json=message_data, verify=False)
            print(f"DEBUG: Response status: {response.status_code}")
            print(f"DEBUG: Response text: {response.text}")
            
            if response.status_code in [200, 201]:
                print("DEBUG: Tavern message saved successfully!")
                return True
            else:
                print(f"❌ API Error {response.status_code}: {response.text}")
                return False
            
        elif table == "private_messages":
            # Prepare private message for Supabase
            pm_data = {
                "id": data["id"],
                "sender_email": data["sender_email"],
                "recipient_email": data["recipient_email"],
                "subject": data["subject"],
                "message": data["message"],
                "created_at": datetime.now().isoformat()
            }
            print(f"DEBUG: Private message data being sent: {pm_data}")
            # Direct API call to Supabase
            url = f"{base_url}/rest/v1/{table}"
            print(f"DEBUG: Making POST request to: {url}")
            response = requests.post(url, headers=headers, json=pm_data, verify=False)
            print(f"DEBUG: Response status: {response.status_code}")
            print(f"DEBUG: Response text: {response.text}")
            
            if response.status_code in [200, 201]:
                print("DEBUG: Private message saved successfully!")
                return True
            else:
                print(f"❌ API Error {response.status_code}: {response.text}")
                return False
        
        else:
            print(f"⚠️ Unknown table: {table}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Error saving to Supabase {table}: {e}")
        print(f"🔍 Full error details: {type(e).__name__}: {str(e)}")
        
        # Show debug info for SSL errors
        if "SSL" in str(e) or "certificate" in str(e):
            print("🔐 This is an SSL certificate error. The data was NOT saved to Supabase.")
            print("ℹ️ We need to resolve the SSL issue to save to Supabase cloud database.")
        
        return False

def save_to_sqlite(table, data):
    """Save data to SQLite as fallback"""
    import sqlite3
    try:
        conn = sqlite3.connect("bencon_calendar.db")
        cursor = conn.cursor()
        
        if table == "users":
            cursor.execute('''
            INSERT OR REPLACE INTO users (email, password_hash, display_name, avatar, pronouns, bio)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (data["email"], data["password_hash"], data["display_name"], data["avatar"], data["pronouns"], data.get("bio", "")))
        
        elif table == "events":
            cursor.execute('''
            INSERT OR REPLACE INTO events (id, title, description, date, time, location, host_email, tags, seat_min, seat_max, max_attendees)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (data["id"], data["title"], data["description"], data["date"], data["time"], 
                  data["location"], data["host_email"], json.dumps(data["tags"]) if isinstance(data["tags"], list) else data["tags"],
                  data.get("seat_min", 1), data.get("seat_max", data.get("max_attendees", 1)), data.get("max_attendees", data.get("seat_max", 1))))
        
        elif table == "rsvps":
            cursor.execute('''
            INSERT OR REPLACE INTO rsvps (id, event_id, user_email, status)
            VALUES (?, ?, ?, ?)
            ''', (data["id"], data["event_id"], data["user_email"], data["status"]))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error saving to SQLite {table}: {e}")
        return False

def update_to_supabase(table, data, key_field="email"):
    """Update existing record in Supabase using PATCH"""
    try:
        import requests
        requests.packages.urllib3.disable_warnings()
        
        base_url = "https://uvsdbuonyfzajhtrgnxq.supabase.co"
        api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV2c2RidW9ueWZ6YWpodHJnbnhxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEwNjUxNjgsImV4cCI6MjA3NjY0MTE2OH0.tq_dQfCIl68bSt2BUPP0lWW2DjjwPpxcKV6LIt2LRFg"
        
        headers = {
            'apikey': api_key,
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal'
        }
        
        # Build URL with filter for the key field
        key_value = data.get(key_field)
        url = f"{base_url}/rest/v1/{table}?{key_field}=eq.{key_value}"
        
        print(f"DEBUG: Updating {table} where {key_field}={key_value}")
        print(f"DEBUG: Update data: {data}")
        
        # Use PATCH for update
        response = requests.patch(url, headers=headers, json=data, verify=False)
        print(f"DEBUG: Response status: {response.status_code}")
        print(f"DEBUG: Response text: {response.text}")
        
        if response.status_code in [200, 201, 204]:
            print(f"✅ Updated {table} successfully!")
            return True
        else:
            print(f"❌ Update failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating {table}: {e}")
        return False

def load_from_database(table, conditions=None):
    """Load data from Supabase using direct API calls"""
    # Always use direct API calls to avoid SSL issues with the client
    return load_from_supabase(table, conditions)

def load_from_supabase(table, conditions=None):
    """Load data from Supabase using direct API calls"""
    
    try:
        import requests
        
        # Disable SSL warnings
        requests.packages.urllib3.disable_warnings()
        
        # Supabase API configuration
        base_url = "https://uvsdbuonyfzajhtrgnxq.supabase.co"
        api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV2c2RidW9ueWZ6YWpodHJnbnhxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEwNjUxNjgsImV4cCI6MjA3NjY0MTE2OH0.tq_dQfCIl68bSt2BUPP0lWW2DjjwPpxcKV6LIt2LRFg"
        
        headers = {
            'apikey': api_key,
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        # Build URL with query parameters
        url = f"{base_url}/rest/v1/{table}"
        
        if conditions and "=" in conditions:
            column, value = conditions.split("=", 1)
            column = column.strip()
            value = value.strip().strip("'\"")
            url += f"?{column}=eq.{value}"
        
        # Make the API request
        response = requests.get(url, headers=headers, verify=False)
        
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"❌ API Error {response.status_code}: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Error loading from Supabase {table} via API: {e}")
        print(f"🔍 Full error details: {type(e).__name__}: {str(e)}")
        return []

def load_from_sqlite(table, conditions=None):
    """Load data from SQLite as fallback"""
    import sqlite3
    try:
        conn = sqlite3.connect("bencon_calendar.db")
        cursor = conn.cursor()
        
        if conditions:
            query = f"SELECT * FROM {table} WHERE {conditions}"
        else:
            query = f"SELECT * FROM {table}"
        
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        return results
    except Exception as e:
        print(f"Error loading from SQLite {table}: {e}")
        return []

# Initialize database on app start
init_database()

# ============================================================================
# SUPABASE REALTIME / WEBSOCKET FUNCTIONALITY
# ============================================================================

def init_realtime_client():
    """Initialize Supabase Realtime client for WebSocket connections"""
    try:
        base_url = "https://uvsdbuonyfzajhtrgnxq.supabase.co"
        api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV2c2RidW9ueWZ6YWpodHJnbnhxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEwNjUxNjgsImV4cCI6MjA3NjY0MTE2OH0.tq_dQfCIl68bSt2BUPP0lWW2DjjwPpxcKV6LIt2LRFg"
        
        # Create Supabase client with Realtime enabled
        # Use options to configure timeout and reconnection
        from supabase import ClientOptions
        options = ClientOptions(
            auto_refresh_token=True,
            persist_session=True
        )
        supabase_client = create_client(base_url, api_key, options=options)
        
        print("✅ Supabase Realtime client initialized!")
        return supabase_client
    except Exception as e:
        print(f"❌ Error initializing Realtime client: {e}")
        import traceback
        traceback.print_exc()
        return None

def handle_users_change(payload):
    """Handle real-time changes to users table"""
    print(f"🔄 Users table changed: {payload}")
    event_type = payload.get('eventType')
    new_record = payload.get('new')
    old_record = payload.get('old')
    
    if event_type == 'INSERT' and new_record:
        email = new_record.get('email')
        st.session_state.users[email] = {
            "password": new_record.get('password_hash'),
            "display_name": new_record.get('display_name'),
            "avatar": new_record.get('avatar'),
            "pronouns": new_record.get('pronouns'),
            "bio": new_record.get('bio', '')
        }
        print(f"✅ User added: {email}")
    
    elif event_type == 'UPDATE' and new_record:
        email = new_record.get('email')
        if email in st.session_state.users:
            st.session_state.users[email].update({
                "password": new_record.get('password_hash'),
                "display_name": new_record.get('display_name'),
                "avatar": new_record.get('avatar'),
                "pronouns": new_record.get('pronouns'),
                "bio": new_record.get('bio', '')
            })
            print(f"✅ User updated: {email}")
    
    elif event_type == 'DELETE' and old_record:
        email = old_record.get('email')
        if email in st.session_state.users:
            del st.session_state.users[email]
            print(f"✅ User deleted: {email}")

def handle_events_change(payload):
    """Handle real-time changes to events table"""
    print(f"🔄 Events table changed: {payload}")
    event_type = payload.get('eventType')
    new_record = payload.get('new')
    old_record = payload.get('old')
    
    if event_type == 'INSERT' and new_record:
        # Add new event to session state
        event_id = new_record.get('id')
        new_event = {
            "id": event_id,
            "name": new_record.get('title'),
            "host": new_record.get('host_email'),
            "day": new_record.get('date'),
            "start": new_record.get('time'),
            "end": new_record.get('end_time', ''),
            "description": new_record.get('description'),
            "location": new_record.get('location', ''),
            "tags": new_record.get('tags', ''),
            "game_system": new_record.get('game_system', 'Not specified'),
            "seat_min": new_record.get('seat_min', 1),
            "seat_max": new_record.get('seat_max', 1),
            "creator_email": new_record.get('host_email'),
            "rsvps": []
        }
        st.session_state.events.append(new_event)
        print(f"✅ Event added: {new_record.get('title')}")
    
    elif event_type == 'UPDATE' and new_record:
        # Update existing event
        event_id = new_record.get('id')
        for i, event in enumerate(st.session_state.events):
            if event.get('id') == event_id:
                st.session_state.events[i].update({
                    "name": new_record.get('title'),
                    "host": new_record.get('host_email'),
                    "day": new_record.get('date'),
                    "start": new_record.get('time'),
                    "end": new_record.get('end_time', ''),
                    "description": new_record.get('description'),
                    "location": new_record.get('location', ''),
                    "tags": new_record.get('tags', ''),
                    "game_system": new_record.get('game_system', 'Not specified'),
                    "seat_min": new_record.get('seat_min', 1),
                    "seat_max": new_record.get('seat_max', 1)
                })
                print(f"✅ Event updated: {new_record.get('title')}")
                break
    
    elif event_type == 'DELETE' and old_record:
        # Remove deleted event
        event_id = old_record.get('id')
        st.session_state.events = [e for e in st.session_state.events if e.get('id') != event_id]
        print(f"✅ Event deleted: {event_id}")

def handle_rsvps_change(payload):
    """Handle real-time changes to rsvps table"""
    print(f"🔄 RSVPs table changed: {payload}")
    event_type = payload.get('eventType')
    new_record = payload.get('new')
    old_record = payload.get('old')
    
    if event_type in ['INSERT', 'UPDATE'] and new_record:
        event_id = new_record.get('event_id')
        user_email = new_record.get('user_email')
        status = new_record.get('status')
        
        # Update the event's RSVP list
        for event in st.session_state.events:
            if event.get('id') == event_id:
                # Remove existing RSVP from this user
                event['rsvps'] = [r for r in event.get('rsvps', []) if r.get('email') != user_email]
                
                # Add new/updated RSVP
                if status == 'yes':
                    user_info = st.session_state.users.get(user_email, {})
                    event['rsvps'].append({
                        "email": user_email,
                        "status": status,
                        "display_name": user_info.get('display_name', user_email),
                        "avatar": user_info.get('avatar', '🧙‍♂️')
                    })
                print(f"✅ RSVP updated for event {event_id}: {user_email} -> {status}")
                break
    
    elif event_type == 'DELETE' and old_record:
        event_id = old_record.get('event_id')
        user_email = old_record.get('user_email')
        
        # Remove RSVP from event
        for event in st.session_state.events:
            if event.get('id') == event_id:
                event['rsvps'] = [r for r in event.get('rsvps', []) if r.get('email') != user_email]
                print(f"✅ RSVP deleted for event {event_id}: {user_email}")
                break

def handle_private_messages_change(payload):
    """Handle real-time changes to private_messages table"""
    print(f"🔄 Private messages table changed: {payload}")
    # Private messages are loaded on-demand, so we just log the change
    # The inbox will refresh when the user opens it

def handle_tavern_messages_change(payload):
    """Handle real-time changes to tavern_messages table"""
    print(f"🔄 Tavern messages table changed: {payload}")
    event_type = payload.get('eventType')
    new_record = payload.get('new')
    
    if event_type == 'INSERT' and new_record:
        # Add new tavern message
        if 'tavern_messages' not in st.session_state:
            st.session_state.tavern_messages = []
        
        user_email = new_record.get('user_email')
        user_info = st.session_state.users.get(user_email, {})
        
        message = {
            "id": new_record.get('id'),
            "user_email": user_email,
            "message": new_record.get('message'),
            "timestamp": new_record.get('created_at'),
            "user_avatar": user_info.get('avatar', '🧙‍♂️'),
            "user_class": AVATAR_OPTIONS.get(user_info.get('avatar', '🧙‍♂️'), 'Adventurer'),
            "beers": 0
        }
        st.session_state.tavern_messages.append(message)
        print(f"✅ Tavern message added from {user_email}")

def setup_realtime_subscriptions():
    """Set up all Realtime subscriptions with error handling"""
    if 'realtime_client' not in st.session_state:
        st.session_state.realtime_client = init_realtime_client()
    
    if not st.session_state.realtime_client:
        print("⚠️ Realtime client not available, skipping subscriptions")
        return False
    
    if 'realtime_subscribed' in st.session_state and st.session_state.realtime_subscribed:
        print("ℹ️ Realtime subscriptions already active")
        return True
    
    try:
        client = st.session_state.realtime_client
        
        # Subscribe to users table
        try:
            client.table('users').on('*', handle_users_change).subscribe()
            print("✅ Subscribed to users table")
        except Exception as e:
            print(f"⚠️ Failed to subscribe to users table: {e}")
        
        # Subscribe to events table
        try:
            client.table('events').on('*', handle_events_change).subscribe()
            print("✅ Subscribed to events table")
        except Exception as e:
            print(f"⚠️ Failed to subscribe to events table: {e}")
        
        # Subscribe to rsvps table
        try:
            client.table('rsvps').on('*', handle_rsvps_change).subscribe()
            print("✅ Subscribed to rsvps table")
        except Exception as e:
            print(f"⚠️ Failed to subscribe to rsvps table: {e}")
        
        # Subscribe to private_messages table
        try:
            client.table('private_messages').on('*', handle_private_messages_change).subscribe()
            print("✅ Subscribed to private_messages table")
        except Exception as e:
            print(f"⚠️ Failed to subscribe to private_messages table: {e}")
        
        # Subscribe to tavern_messages table
        try:
            client.table('tavern_messages').on('*', handle_tavern_messages_change).subscribe()
            print("✅ Subscribed to tavern_messages table")
        except Exception as e:
            print(f"⚠️ Failed to subscribe to tavern_messages table: {e}")
        
        st.session_state.realtime_subscribed = True
        print("🎉 Realtime subscriptions setup complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up Realtime subscriptions: {e}")
        import traceback
        traceback.print_exc()
        return False

# Initialize Realtime subscriptions on app start
try:
    setup_realtime_subscriptions()
except Exception as e:
    print(f"⚠️ Realtime subscriptions failed to initialize: {e}")
    print("ℹ️ App will continue with polling fallback")

# ============================================================================

# Helper function for parsing tags
def get_first_tag_icon(event):
    tags = event.get("tags", "")
    try:
        parsed_tags = json.loads(tags) if tags and tags.strip() else []
        first_tag = parsed_tags[0] if parsed_tags else ""
        return TAGS.get(first_tag, "📝")
    except (json.JSONDecodeError, TypeError, IndexError):
        return "📝"

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
    "🧙‍♂️": "Trash Wizard",
    "⚔️": "Chaos Goblin", 
    "🏹": "Rotten Archer",
    "🛡️": "Rust Paladin",
    "🗡️": "Stabby Rogue",
    "🔮": "Crystal Meth Sorcerer",
    "📚": "Book Goblin",
    "🎭": "Drama Llama",
    "🐉": "Scaly Bastard",
    "🦄": "Unicorn Corpse",
    "🔥": "Fire Hazard",
    "❄️": "Buzzkill",
    "🌟": "Special Little Guy",
    "🦅": "Sky Rat",
    "👑": "Mole King",
    "🦊": "Foxy Goblin",
    "🐸": "Froggo",
    "🦉": "Pondering Owl",
    "🐺": "Luuupe",
    "🦋": "Cottage Core Wench",
    "🌙": "Astrology Hoe",
    "☀️": "Praiser of da Sun",
    "⚡": "Sparky Lad",
    "🌊": "Catch-a-ride",
    "🌪️": "Disaster Gay",
    "🍄": "Shroom Enjoyer",
    "🌿": "Illya's Fated Foe",
    "💀": "Rag N' Bones"
}

# Pronoun options
PRONOUN_OPTIONS = [
    "they/them",
    "she/her", 
    "he/him",
    "she/they",
    "he/they",
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
    
    try:
        users = {}
        print(f"🔍 DEBUG: Loading users from database...")
        db_users = load_from_database("users")
        print(f"🔍 DEBUG: Raw users data from DB: {db_users}")
        for user_data in db_users:
            # Supabase returns dictionaries, not tuples
            if isinstance(user_data, dict):
                email = user_data.get("email")
                users[email] = {
                    "password": user_data.get("password_hash"),
                    "display_name": user_data.get("display_name"),
                    "avatar": user_data.get("avatar"),
                    "pronouns": user_data.get("pronouns"),
                    "bio": user_data.get("bio", "")
                }
            else:
                # Fallback for SQLite format (tuple)
                email, password_hash, display_name, avatar, pronouns, bio, created_at = user_data
                users[email] = {
                    "password": password_hash,
                    "display_name": display_name,
                    "avatar": avatar,
                    "pronouns": pronouns,
                    "bio": bio or ""
                }
        print(f"🔍 DEBUG: Processed users: {list(users.keys())}")
        return users
    except Exception as e:
        print(f"Error loading users: {e}")
        return {}

def get_events_from_supabase():
    """Fetch events directly from Supabase with all fields including tags and game_system"""
    try:
        SUPABASE_URL, SUPABASE_KEY = get_supabase_credentials()
        if not SUPABASE_URL or not SUPABASE_KEY:
            return []
        
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/events",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json"
            }
        )
        
        if response.status_code == 200:
            events_data = response.json()
            events = []
            
            for event_data in events_data:
                # Parse tags if they're stored as JSON
                tags_data = event_data.get("tags", [])
                if isinstance(tags_data, str):
                    try:
                        tags_data = json.loads(tags_data) if tags_data else []
                    except (json.JSONDecodeError, TypeError):
                        tags_data = [tags_data] if tags_data else []
                elif not isinstance(tags_data, list):
                    tags_data = []
                
                # Get host display name
                host_email = event_data.get("host_email")
                host_display_name = ""
                if host_email:
                    try:
                        user_response = requests.get(
                            f"{SUPABASE_URL}/rest/v1/users?email=eq.{host_email}&select=display_name",
                            headers={
                                "apikey": SUPABASE_KEY,
                                "Authorization": f"Bearer {SUPABASE_KEY}",
                                "Content-Type": "application/json"
                            }
                        )
                        if user_response.status_code == 200:
                            users = user_response.json()
                            if users:
                                host_display_name = users[0].get("display_name", "")
                    except:
                        pass
                
                # Load RSVPs for this event
                rsvps = []
                try:
                    rsvp_response = requests.get(
                        f"{SUPABASE_URL}/rest/v1/rsvps?event_id=eq.{event_data['id']}&status=eq.yes&select=user_email,status",
                        headers={
                            "apikey": SUPABASE_KEY,
                            "Authorization": f"Bearer {SUPABASE_KEY}",
                            "Content-Type": "application/json"
                        }
                    )
                    if rsvp_response.status_code == 200:
                        rsvp_data = rsvp_response.json()
                        for rsvp in rsvp_data:
                            # Get user details for each RSVP
                            try:
                                user_response = requests.get(
                                    f"{SUPABASE_URL}/rest/v1/users?email=eq.{rsvp['user_email']}&select=display_name,avatar",
                                    headers={
                                        "apikey": SUPABASE_KEY,
                                        "Authorization": f"Bearer {SUPABASE_KEY}",
                                        "Content-Type": "application/json"
                                    }
                                )
                                if user_response.status_code == 200:
                                    users = user_response.json()
                                    if users:
                                        user = users[0]
                                        rsvps.append({
                                            "email": rsvp["user_email"],
                                            "display_name": user.get("display_name", ""),
                                            "avatar": user.get("avatar", "🧙‍♂️")
                                        })
                            except:
                                pass
                except:
                    pass
                
                events.append({
                    "id": event_data.get("id"),
                    "title": event_data.get("title"),
                    "name": event_data.get("title"),  # Compatibility
                    "description": event_data.get("description", ""),
                    "date": event_data.get("date"),
                    "day": event_data.get("date"),  # Compatibility
                    "time": event_data.get("time"),
                    "start": event_data.get("time"),  # Compatibility
                    "end": event_data.get("end_time", event_data.get("time")),  # Use end_time if available, fallback to time
                    "location": event_data.get("location", ""),
                    "host_email": host_email,
                    "host": host_display_name,
                    "creator_email": host_email,  # Compatibility
                    "tags": tags_data,
                    "tag": tags_data[0] if tags_data else "",  # Compatibility
                    "game_system": event_data.get("game_system", "Not specified"),
                    "seat_min": event_data.get("seat_min", 1),
                    "seat_max": event_data.get("seat_max", 1),
                    "max_attendees": event_data.get("max_attendees"),
                    "rsvps": rsvps
                })
            
            return events
        else:
            print(f"Error fetching events from Supabase: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching events from Supabase: {e}")
        return []
def load_events_from_db():
    """Load events from database into session state"""
    
    try:
        events = []
        db_events = load_from_database("events")
        for event_data in db_events:
            if isinstance(event_data, dict):
                # Supabase returns dictionaries
                event_id = event_data.get("id")
                title = event_data.get("title")
                description = event_data.get("description")
                date = event_data.get("date") 
                time = event_data.get("time")
                location = event_data.get("location")
                host_email = event_data.get("host_email")
                tags = event_data.get("tags")
                seat_min = event_data.get("seat_min", 1)
                seat_max = event_data.get("seat_max", 1)
                max_attendees = event_data.get("max_attendees")
            else:
                # Fallback for SQLite format (tuple)
                event_id, title, description, date, time, location, host_email, tags, seat_min, seat_max, max_attendees, created_at = event_data
        
            try:
                parsed_tags = json.loads(tags) if tags and tags.strip() else []
            except (json.JSONDecodeError, TypeError):
                parsed_tags = []
        
            # Look up host display name from users
            host_display_name = ""
            if host_email:
                db_users = load_from_database("users", f"email='{host_email}'")
                if db_users and len(db_users) > 0:
                    user_data = db_users[0]
                    if isinstance(user_data, dict):
                        host_display_name = user_data.get("display_name", "")
                    else:
                        host_display_name = user_data[2]  # display_name is 3rd column in SQLite
            
            events.append({
                "id": event_id,
                "title": title,
                "name": title,  # Add name field for compatibility
                "description": description,
                "date": date,
                "day": date,    # Map date to day for Quest Counter compatibility
                "time": time,
                "start": time,  # Map time to start for compatibility
                "end": time,    # Add end time (using same time for now)
                "location": location,
                "host_email": host_email,
                "host": host_display_name,  # Add host display name
                "creator_email": host_email,  # Add creator_email for compatibility
                "tags": parsed_tags,
                "tag": parsed_tags[0] if parsed_tags else "",  # Add single tag for compatibility
                "game_system": event_data.get("game_system", "Not specified"),
                "seat_min": seat_min,
                "seat_max": seat_max,
                "max_attendees": max_attendees,
                "rsvps": []     # Initialize empty rsvps list
            })
        return events
    except Exception as e:
        print(f"Error loading events: {e}")
        return []

def load_rsvps_from_db():
    """Load RSVPs from database and attach them to events"""
    try:
        db_rsvps = load_from_database("rsvps")
        rsvps_by_event = {}
        
        # Load all users at once to avoid individual database calls
        all_users = load_from_database("users")
        users_dict = {}
        for user_data in all_users:
            if isinstance(user_data, dict):
                email = user_data.get("email")
                users_dict[email] = {
                    "display_name": user_data.get("display_name", email),
                    "avatar": user_data.get("avatar", "🧙‍♂️")
                }
            else:
                # Fallback for SQLite format (tuple)
                email = user_data[1]  # email is 2nd column
                users_dict[email] = {
                    "display_name": user_data[2],  # display_name is 3rd column
                    "avatar": user_data[3] if len(user_data) > 3 else "🧙‍♂️"  # avatar is 4th column
                }
        
        for rsvp_data in db_rsvps:
            if isinstance(rsvp_data, dict):
                # Supabase returns dictionaries
                event_id = rsvp_data.get("event_id")
                user_email = rsvp_data.get("user_email")
                status = rsvp_data.get("status", "yes")
            else:
                # Fallback for SQLite format (tuple)
                rsvp_id, event_id, user_email, status, created_at = rsvp_data
            
            if event_id not in rsvps_by_event:
                rsvps_by_event[event_id] = []
            
            # Get user info from the pre-loaded users dictionary
            if user_email in users_dict and status == "yes":
                user_info = users_dict[user_email]
                rsvps_by_event[event_id].append({
                    "email": user_email,
                    "display_name": user_info["display_name"],
                    "avatar": user_info["avatar"]
                })
        
        return rsvps_by_event
    except Exception as e:
        print(f"Error loading RSVPs: {e}")
        return {}

def refresh_event_rsvps(event_id):
    """Refresh RSVPs for a specific event from database"""
    try:
        db_rsvps = load_from_database("rsvps", f"event_id='{event_id}'")
        event_rsvps = []
        
        # Load all users at once to avoid individual database calls
        all_users = load_from_database("users")
        users_dict = {}
        for user_data in all_users:
            if isinstance(user_data, dict):
                email = user_data.get("email")
                users_dict[email] = {
                    "display_name": user_data.get("display_name", email),
                    "avatar": user_data.get("avatar", "🧙‍♂️")
                }
            else:
                # Fallback for SQLite format (tuple)
                email = user_data[1]  # email is 2nd column
                users_dict[email] = {
                    "display_name": user_data[2],  # display_name is 3rd column
                    "avatar": user_data[3] if len(user_data) > 3 else "🧙‍♂️"  # avatar is 4th column
                }
        
        for rsvp_data in db_rsvps:
            if isinstance(rsvp_data, dict):
                user_email = rsvp_data.get("user_email")
                status = rsvp_data.get("status", "yes")
            else:
                rsvp_id, event_id_db, user_email, status, created_at = rsvp_data
            
            if status == "yes" and user_email in users_dict:  # Only include confirmed RSVPs
                user_info = users_dict[user_email]
                event_rsvps.append({
                    "email": user_email,
                    "display_name": user_info["display_name"],
                    "avatar": user_info["avatar"]
                })
        
        # Update the event in session state
        if "events" in st.session_state:
            for event in st.session_state.events:
                if event["id"] == event_id:
                    event["rsvps"] = event_rsvps
                    break
        
        return event_rsvps
    except Exception as e:
        st.error(f"Error refreshing RSVPs for event {event_id}: {e}")
        return []

def sync_session_with_db():
    """Sync session state with database on app start"""
    
    try:
        # Load data from database
        db_users = load_users_from_db()
        db_events = load_events_from_db()
        db_rsvps = load_rsvps_from_db()
        
        # Attach RSVPs to events
        for event in db_events:
            event_id = event["id"]
            if event_id in db_rsvps:
                event["rsvps"] = db_rsvps[event_id]
            else:
                event["rsvps"] = []
        
        # Update session state
        st.session_state.users = db_users
        st.session_state.events = db_events
        
        # If database is empty, create test users
        if not db_users:
            test_users = {
                "Test": {
                    "password": hashlib.md5("Test".encode()).hexdigest(),
                    "display_name": "Test",
                    "avatar": "🧙‍♂️",
                    "pronouns": "they/them",
                    "bio": ""
                },
                "Test2": {
                    "password": hashlib.md5("Test2".encode()).hexdigest(),
                    "display_name": "Test2", 
                    "avatar": "⚔️",
                    "pronouns": "she/her",
                    "bio": ""
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
        
    except Exception as e:
        print(f"Error syncing with database: {e}")
        # Initialize with empty data if sync fails
        st.session_state.users = {}
        st.session_state.events = []
        return {}, []

def refresh_data():
    """Refresh data from database only when needed"""
    st.session_state.users, st.session_state.events = sync_session_with_db()

# Initialize session state with database persistence
if "events" not in st.session_state:
    st.session_state.users, st.session_state.events = sync_session_with_db()
if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = True

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
    st.session_state.active_inbox_tab = "📥 Received"
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
def register_user(email, password, display_name, avatar, pronouns, bio=""):
    if email.strip() and password.strip() and display_name.strip() and avatar and pronouns:
        # Check if email already exists
        if email in st.session_state.users:
            return False, "Email already exists!"
        
        # Check if display name (username) already exists
        for existing_email, user_data in st.session_state.users.items():
            if user_data["display_name"].lower() == display_name.strip().lower():
                return False, f"Username '{display_name.strip()}' is already taken! Please choose a different name."
        
        # Generate password hint from email (simple goblin logic)
        password_hint = f"Hint: Your email starts with '{email.split('@')[0][:3]}...'"
        
        # Create the user account directly (no email verification)
        password_hash = hashlib.md5(password.encode()).hexdigest()
        
        # Save to session state
        st.session_state.users[email] = {
            "password": password_hash,
            "display_name": display_name.strip(),
            "avatar": avatar,
            "pronouns": pronouns,
            "bio": bio,
            "password_hint": password_hint,
            "email_verified": True  # Skip verification for goblin simplicity
        }
        
        # Save to database
        print("=" * 80)
        print(f"🔍 DEBUG: About to call save_to_database for users (registration)")
        print(f"🔍 DEBUG: Email: {email}, Display Name: {display_name.strip()}")
        print("=" * 80)
        result = save_to_database("users", {
            "email": email,
            "password_hash": password_hash,
            "display_name": display_name.strip(),
            "avatar": avatar,
            "pronouns": pronouns,
            "bio": bio,
            "password_hint": password_hint,
            "email_verified": True
        })
        
        print("=" * 80)
        print(f"🔍 DEBUG: save_to_database returned: {result}")
        print("=" * 80)
        
        # Auto-login after registration
        st.session_state.current_user = {
            "email": email,
            "display_name": display_name.strip(),
            "avatar": avatar,
            "pronouns": pronouns,
            "bio": bio
        }
        return True, f"Welcome to the party, {display_name}! 🎉"
        
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

def update_user_profile(email, display_name, avatar, pronouns, bio=""):
    if email in st.session_state.users:
        st.session_state.users[email]["display_name"] = display_name
        st.session_state.users[email]["avatar"] = avatar
        st.session_state.users[email]["pronouns"] = pronouns
        st.session_state.users[email]["bio"] = bio
        # Update current user session
        st.session_state.current_user.update({
            "display_name": display_name,
            "avatar": avatar,
            "pronouns": pronouns,
            "bio": bio
        })
        
        # Update in Supabase using PATCH
        password_hash = st.session_state.users[email]["password"]
        update_to_supabase("users", {
            "email": email,
            "password_hash": password_hash,
            "display_name": display_name,
            "avatar": avatar,
            "pronouns": pronouns,
            "bio": bio
        }, key_field="email")
        
        return True
    return False

def reset_password(email, new_password=None, reset_code=None):
    """Simple password reset using password hint"""
    if email in st.session_state.users:
        if new_password is None:
            # Request password reset - show hint
            user_data = st.session_state.users[email]
            password_hint = user_data.get("password_hint", "No hint available")
            return "hint_shown", f"Password hint: {password_hint}"
        else:
            # Reset password
            password_hash = hashlib.md5(new_password.encode()).hexdigest()
            st.session_state.users[email]["password"] = password_hash
            
            # Update in database
            save_to_database("users", {
                "email": email,
                "password_hash": password_hash,
                "display_name": st.session_state.users[email]["display_name"],
                "avatar": st.session_state.users[email]["avatar"],
                "pronouns": st.session_state.users[email]["pronouns"],
                "bio": st.session_state.users[email].get("bio", ""),
                "password_hint": st.session_state.users[email].get("password_hint", "")
            })
            
            return True, "Password updated successfully! You can now login with your new password."
    
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
    message_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    
    # Try to save to Supabase first
    try:
        SUPABASE_URL, SUPABASE_KEY = get_supabase_credentials()
        if SUPABASE_URL and SUPABASE_KEY:
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/private_messages",
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "id": message_id,
                    "sender_email": from_email,
                    "recipient_email": to_email,
                    "subject": f"Message from {st.session_state.users[from_email]['display_name']}",
                    "message": message,
                    "read_status": 0,
                    "created_at": timestamp
                }
            )
            
            if response.status_code in [200, 201]:
                print(f"Message saved to Supabase: {message_id}")
                return message_id
    except Exception as e:
        print(f"Error saving message to Supabase: {e}")
    
    # Fallback to session state
    if "messages" not in st.session_state:
        st.session_state.messages = {}
    
    if to_email not in st.session_state.messages:
        st.session_state.messages[to_email] = []
    
    message_data = {
        "id": message_id,
        "from_email": from_email,
        "from_name": st.session_state.users[from_email]["display_name"],
        "from_avatar": st.session_state.users[from_email].get("avatar", "🧙‍♂️"),
        "message": message,
        "event_id": event_id,
        "reply_to_id": reply_to_id,
        "timestamp": timestamp,
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
    
    return message_id

def get_user_messages(user_email):
    """Get all messages for a user from Supabase"""
    try:
        # Try Supabase first
        SUPABASE_URL, SUPABASE_KEY = get_supabase_credentials()
        if SUPABASE_URL and SUPABASE_KEY:
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/private_messages",
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/json"
                },
                params={
                    "recipient_email": f"eq.{user_email}",
                    "select": "*",
                    "order": "created_at.desc"
                }
            )
            
            if response.status_code == 200:
                messages = response.json()
                # print(f"Debug: Supabase returned {len(messages)} messages")
                # Convert to expected format
                formatted_messages = []
                for msg in messages:
                    # Get sender info from users
                    sender_email = msg["sender_email"]
                    sender_info = st.session_state.users.get(sender_email, {})
                    formatted_messages.append({
                        "id": msg["id"],
                        "from_email": sender_email,
                        "from_name": sender_info.get("display_name", sender_email),
                        "from_avatar": sender_info.get("avatar", "🧙‍♂️"),
                        "subject": msg.get("subject", ""),
                        "message": msg["message"],
                        "timestamp": msg["created_at"],
                        "read": bool(msg.get("read_status", 0))
                    })
                # print(f"Debug: Formatted {len(formatted_messages)} messages")
                return formatted_messages
            else:
                # print(f"Debug: Supabase returned status {response.status_code}")
                pass
    except Exception as e:
        print(f"Error fetching messages from Supabase: {e}")
    
    # Fallback to session state
    if "messages" not in st.session_state:
        st.session_state.messages = {}
    
    fallback_messages = st.session_state.messages.get(user_email, [])
    # print(f"Debug: Fallback returned {len(fallback_messages)} messages")
    return fallback_messages

def mark_message_read(user_email, message_id):
    """Mark a message as read in Supabase"""
    try:
        # Try Supabase first
        SUPABASE_URL, SUPABASE_KEY = get_supabase_credentials()
        if SUPABASE_URL and SUPABASE_KEY:
            response = requests.patch(
                f"{SUPABASE_URL}/rest/v1/private_messages",
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "read_status": 1
                },
                params={
                    "id": f"eq.{message_id}",
                    "recipient_email": f"eq.{user_email}"
                }
            )
            if response.status_code in [200, 204]:
                return
    except Exception as e:
        print(f"Error marking message as read in Supabase: {e}")
    
    # Fallback to session state
    if user_email in st.session_state.messages:
        for message in st.session_state.messages[user_email]:
            if message["id"] == message_id:
                message["read"] = True
                break

def delete_message(user_email, message_id):
    """Delete a message from Supabase and session state"""
    try:
        # Try to delete from Supabase first
        SUPABASE_URL, SUPABASE_KEY = get_supabase_credentials()
        if SUPABASE_URL and SUPABASE_KEY:
            response = requests.delete(
                f"{SUPABASE_URL}/rest/v1/private_messages",
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/json"
                },
                params={
                    "id": f"eq.{message_id}",
                    "recipient_email": f"eq.{user_email}"
                }
            )
            if response.status_code in [200, 204]:
                print(f"Message {message_id} deleted from Supabase")
                return True
    except Exception as e:
        print(f"Error deleting message from Supabase: {e}")
    
    # Fallback to session state
    if user_email in st.session_state.messages:
        st.session_state.messages[user_email] = [
            msg for msg in st.session_state.messages[user_email] 
            if msg["id"] != message_id
        ]
    return True

def get_sent_messages(user_email):
    """Get all sent messages for a user from Supabase"""
    try:
        # Try Supabase first
        SUPABASE_URL, SUPABASE_KEY = get_supabase_credentials()
        if SUPABASE_URL and SUPABASE_KEY:
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/private_messages",
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/json"
                },
                params={
                    "sender_email": f"eq.{user_email}",
                    "select": "*",
                    "order": "created_at.desc"
                }
            )
            
            if response.status_code == 200:
                messages = response.json()
                # Convert to expected format
                formatted_messages = []
                for msg in messages:
                    # Get recipient info from users
                    recipient_email = msg["recipient_email"]
                    recipient_info = st.session_state.users.get(recipient_email, {})
                    formatted_messages.append({
                        "id": msg["id"],
                        "to_email": recipient_email,
                        "to_name": recipient_info.get("display_name", recipient_email),
                        "to_avatar": recipient_info.get("avatar", "🧙‍♂️"),
                        "subject": msg.get("subject", ""),
                        "message": msg["message"],
                        "timestamp": msg["created_at"],
                        "read": bool(msg.get("read_status", 0))
                    })
                return formatted_messages
    except Exception as e:
        print(f"Error fetching sent messages from Supabase: {e}")
    
    # Fallback to session state
    return st.session_state.sent_messages.get(user_email, [])

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

def get_user_rsvps(user_email):
    """Return a list of event dicts that the user has RSVPed to.

    Uses Supabase when available, otherwise falls back to local session_state scanning.
    """
    # Prefer Supabase SDK when configured
    if supabase:
        try:
            print(f"get_user_rsvps: using Supabase SDK for {user_email}")
            r = supabase.table("rsvps").select("event_id").eq("user_email", user_email).execute()
            event_ids = [row["event_id"] for row in (r.data or [])]
            if not event_ids:
                return []
            events_resp = supabase.table("events").select("*").in_("id", event_ids).execute()
            return events_resp.data or []
        except Exception as e:
            st.warning(f"Supabase RSVPs fetch failed: {e}")

    # If no SDK client, try using the REST API directly
    try:
        import requests
        requests.packages.urllib3.disable_warnings()
        base_url = "https://uvsdbuonyfzajhtrgnxq.supabase.co"
        api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV2c2RidW9ueWZ6YWpodHJnbnhxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEwNjUxNjgsImV4cCI6MjA3NjY0MTE2OH0.tq_dQfCIl68bSt2BUPP0lWW2DjjwPpxcKV6LIt2LRFg"
        headers = {
            'apikey': api_key,
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        # Fetch rsvps for the user via REST
        url = f"{base_url}/rest/v1/rsvps?user_email=eq.{user_email}&select=event_id"
        print(f"get_user_rsvps: REST GET {url}")
        resp = requests.get(url, headers=headers, verify=False)
        print(f"get_user_rsvps: REST status {resp.status_code}")
        if resp.status_code != 200:
            return []
        rows = resp.json()
        event_ids = [r.get('event_id') for r in rows]
        if not event_ids:
            return []

        # Fetch events by ids
        # Supabase REST expects csv for in operator: id=in.(id1,id2)
        ids_csv = ",".join(event_ids)
        events_url = f"{base_url}/rest/v1/events?id=in.({ids_csv})"
        print(f"get_user_rsvps: REST GET events {events_url}")
        events_resp = requests.get(events_url, headers=headers, verify=False)
        print(f"get_user_rsvps: events status {events_resp.status_code}")
        if events_resp.status_code == 200:
            return events_resp.json()
        return []
    except Exception as e:
        st.warning(f"Error fetching RSVPs via REST: {e}")

    # Fallback: scan local events stored in session_state
    results = []
    for event in st.session_state.get("events", []):
        for rsvp in event.get("rsvps", []):
            if rsvp.get("user_email") == user_email or rsvp.get("email") == user_email:
                results.append(event)
                break
    return results

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
    
    # Persist to database (Supabase or SQLite) via save_to_database helper
    try:
        save_to_database("tavern_messages", {
            "id": message_data["id"],
            "user_email": message_data["user_email"],
            "message": message_data["message"]
        })
    except Exception as e:
        # Don't break the app if persistence fails — keep in session_state
        st.warning(f"Could not persist tavern message: {e}")

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
                # Refresh RSVPs from database to ensure consistency
                refresh_event_rsvps(event_id)
            break

def cancel_rsvp(event_id, user_email):
    for event in st.session_state.events:
        if event["id"] == event_id:
            if "rsvps" in event:
                event["rsvps"] = [rsvp for rsvp in event["rsvps"] if rsvp["email"] != user_email]
                # Remove RSVP from Supabase
                if supabase:
                    try:
                        supabase.table("rsvps").delete().eq("event_id", event_id).eq("user_email", user_email).execute()
                    except Exception as e:
                        st.error(f"Error canceling RSVP: {e}")
                else:
                    # Fallback to REST API
                    try:
                        base_url = st.secrets.get("SUPABASE_URL")
                        headers = {
                            "apikey": st.secrets.get("SUPABASE_KEY"),
                            "Authorization": f"Bearer {st.secrets.get('SUPABASE_KEY')}",
                            "Content-Type": "application/json"
                        }
                        rsvps_url = f"{base_url}/rest/v1/rsvps?event_id=eq.{event_id}&user_email=eq.{user_email}"
                        resp = requests.delete(rsvps_url, headers=headers, verify=False)
                        if resp.status_code not in [200, 204]:
                            st.error(f"Error canceling RSVP: {resp.status_code}")
                    except Exception as e:
                        st.error(f"Error canceling RSVP: {e}")
                # Refresh RSVPs from database to ensure consistency
                refresh_event_rsvps(event_id)
            break

def delete_event(event_id):
    """Delete an event completely"""
    # Delete from Supabase: prefer SDK, otherwise use REST API
    if supabase:
        try:
            print(f"delete_event: deleting RSVPs for {event_id} via SDK")
            supabase.table("rsvps").delete().eq("event_id", event_id).execute()
            supabase.table("events").delete().eq("id", event_id).execute()
        except Exception as e:
            st.error(f"Error deleting event from Supabase: {e}")
            return
    else:
        # Try REST API deletion
        try:
            import requests
            requests.packages.urllib3.disable_warnings()
            base_url = "https://uvsdbuonyfzajhtrgnxq.supabase.co"
            api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV2c2RidW9ueWZ6YWpodHJnbnhxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEwNjUxNjgsImV4cCI6MjA3NjY0MTE2OH0.tq_dQfCIl68bSt2BUPP0lWW2DjjwPpxcKV6LIt2LRFg"
            headers = {
                'apikey': api_key,
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
                'Prefer': 'return=minimal'
            }

            # Delete RSVPs
            rsvps_url = f"{base_url}/rest/v1/rsvps?event_id=eq.{event_id}"
            resp1 = requests.delete(rsvps_url, headers=headers, verify=False)
            if resp1.status_code not in (200,204):
                st.warning(f"Warning deleting RSVPs via REST: {resp1.status_code} {resp1.text}")

            # Delete event
            event_url = f"{base_url}/rest/v1/events?id=eq.{event_id}"
            resp2 = requests.delete(event_url, headers=headers, verify=False)
            if resp2.status_code not in (200,204):
                st.error(f"Error deleting event via REST: {resp2.status_code} {resp2.text}")
                return
        except Exception as e:
            st.error(f"Error deleting event via REST: {e}")
            return

    # Update local state and refresh UI
    st.session_state.events = [event for event in st.session_state.events if event["id"] != event_id]
    st.success("Event deleted successfully!")
    st.rerun()

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
            
            tag_icon = TAGS.get(event.get("tags", ""), "📝")
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

# CSS is now loaded from .streamlit/style.css file

# CSS injection using st.components.v1.html to inject into parent window
st.components.v1.html("""
<script>
// Inject CSS into parent window
const parentWindow = window.parent;
const parentDocument = parentWindow.document;

// Create style element
const style = parentDocument.createElement('style');
style.textContent = `
/* ULTIMATE CSS OVERRIDE - Loaded in main page */
button,
.stButton > button,
button[data-testid="baseButton-primary"],
button[data-testid="baseButton-secondary"],
.stButton button[type="button"],
button[class*="stButton"],
button[class*="css-"],
button[class*="baseButton"],
button[class*="primary"],
button[class*="secondary"],
button[type="submit"],
button[type="button"],
.main .block-container button,
.main .block-container .stButton button,
.main .block-container .stForm button,
.main .block-container .stForm .stButton button,
.stForm button,
.stForm .stButton button,
.stFormSubmitButton button,
button[data-baseweb="button"],
button[aria-label],
button[title],
div[data-testid="stButton"] button,
div[data-testid="stForm"] button,
div[data-testid="stFormSubmitButton"] button {
    background: linear-gradient(135deg, #8B4513 0%, #A0522D 50%, #CD853F 100%) !important;
    background-color: #8B4513 !important;
    background-image: linear-gradient(135deg, #8B4513 0%, #A0522D 50%, #CD853F 100%) !important;
    color: #FFFACD !important;
    border: 2px solid #654321 !important;
    border-radius: 8px !important;
    font-family: 'Cinzel', serif !important;
    font-weight: bold !important;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.8) !important;
    box-shadow: 
        inset 0 1px 3px rgba(255,255,255,0.2),
        0 2px 4px rgba(0,0,0,0.3) !important;
    transition: all 0.3s ease !important;
}

button:hover,
.stButton > button:hover,
button[data-testid="baseButton-primary"]:hover,
button[data-testid="baseButton-secondary"]:hover,
.stButton button[type="button"]:hover,
button[class*="stButton"]:hover,
button[class*="css-"]:hover,
button[class*="baseButton"]:hover,
button[class*="primary"]:hover,
button[class*="secondary"]:hover,
button[type="submit"]:hover,
button[type="button"]:hover,
.main .block-container button:hover,
.main .block-container .stButton button:hover,
.main .block-container .stForm button:hover,
.main .block-container .stForm .stButton button:hover,
.stForm button:hover,
.stForm .stButton button:hover,
.stFormSubmitButton button:hover,
button[data-baseweb="button"]:hover,
button[aria-label]:hover,
button[title]:hover,
div[data-testid="stButton"] button:hover,
div[data-testid="stForm"] button:hover,
div[data-testid="stFormSubmitButton"] button:hover {
    background: linear-gradient(135deg, #A0522D 0%, #CD853F 50%, #DEB887 100%) !important;
    transform: translateY(-1px) !important;
    box-shadow: 
        inset 0 1px 3px rgba(255,255,255,0.3),
        0 4px 8px rgba(0,0,0,0.4) !important;
}

/* Force header styling */
h3,
div[style*="background: linear-gradient(135deg, #8B4513"] h3,
div[style*="background: linear-gradient(135deg, #8B4513"] h3 *,
.stMarkdown h3,
.stMarkdown h3 *,
.main .block-container .stMarkdown h3,
.main .block-container .stMarkdown h3 *,
div[data-testid="stMarkdownContainer"] h3,
div[data-testid="stMarkdownContainer"] h3 * {
    color: #FFFACD !important;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.8) !important;
}

/* Force form labels */
label,
.main .block-container .stForm label,
.main .block-container .stTextInput label,
.main .block-container .stSelectbox label,
.main .block-container .stNumberInput label,
.main .block-container .stTextArea label,
.main .block-container .stRadio label,
div[data-testid="stForm"] label,
div[data-testid="stTextInput"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stNumberInput"] label,
div[data-testid="stTextArea"] label,
div[data-testid="stRadio"] label {
    color: #8B4513 !important;
    font-family: 'Uncial Antiqua', 'Cinzel', serif !important;
    font-weight: bold !important;
    font-size: 18px !important;
    background: transparent !important;
    text-shadow: 1px 1px 2px rgba(255,255,255,0.5) !important;
}

/* Force radio button text */
.main .block-container .stForm .stRadio label,
.main .block-container .stForm .stRadio label > div,
.main .block-container .stForm .stRadio label span,
.main .block-container .stForm div[data-testid="stRadio"] label,
.main .block-container .stForm div[data-testid="stRadio"] label > div,
.main .block-container .stForm div[data-testid="stRadio"] label span,
div[data-testid="stRadio"] label,
div[data-testid="stRadio"] label > div,
div[data-testid="stRadio"] label span {
    color: #8B4513 !important;
    font-family: 'Uncial Antiqua', 'Cinzel', serif !important;
    font-weight: bold !important;
    background: transparent !important;
    text-shadow: 1px 1px 2px rgba(255,255,255,0.5) !important;
}

/* Force form inputs */
input,
textarea,
select,
.main .block-container .stForm .stTextInput > div > div > input,
.main .block-container .stForm .stTextArea > div > div > textarea,
.main .block-container .stForm .stSelectbox > div > div > div,
.main .block-container .stForm .stNumberInput > div > div > input,
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-testid="stSelectbox"] select,
div[data-testid="stNumberInput"] input {
    background-color: #FFFACD !important;
    border: 2px solid #654321 !important;
    border-radius: 8px !important;
    color: #8B4513 !important;
    font-family: 'Uncial Antiqua', 'Cinzel', serif !important;
    font-weight: bold !important;
}

/* Force dropdown containers */
.main .block-container .stForm .stSelectbox > div,
.main .block-container .stForm .stSelectbox > div > div,
div[data-testid="stSelectbox"] > div,
div[data-testid="stSelectbox"] > div > div {
    background-color: transparent !important;
    background: transparent !important;
    background-image: none !important;
}

/* Remove brown box behind sidebar */
.sidebar .sidebar-content {
    background-color: transparent !important;
    background: transparent !important;
}

/* Fix radio buttons - make them visible - ULTRA AGGRESSIVE */
.main .block-container .stForm .stRadio,
div[data-testid="stRadio"],
div[data-testid="stRadio"] > div,
div[data-testid="stRadio"] > div > div,
div[data-testid="stRadio"] > div > div > div {
    background: transparent !important;
    border: none !important;
    padding: 10px 0 !important;
    margin: 5px 0 !important;
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
}

/* Radio button options - make them visible - ULTRA AGGRESSIVE */
.main .block-container .stForm .stRadio label,
div[data-testid="stRadio"] label,
div[data-testid="stRadio"] label > div,
div[data-testid="stRadio"] label > div > div,
div[data-testid="stRadio"] label span,
div[data-testid="stRadio"] label p {
    color: #8B4513 !important;
    font-family: 'Uncial Antiqua', 'Cinzel', serif !important;
    font-weight: bold !important;
    background: transparent !important;
    text-shadow: 1px 1px 2px rgba(255,255,255,0.5) !important;
    padding: 5px 0 !important;
    margin: 5px 0 !important;
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
    font-size: 16px !important;
}

/* Radio button input circles - ULTRA AGGRESSIVE */
.main .block-container .stForm .stRadio input[type="radio"],
div[data-testid="stRadio"] input[type="radio"],
div[data-testid="stRadio"] input[type="radio"]:checked,
div[data-testid="stRadio"] input[type="radio"]:not(:checked) {
    background-color: #FFFACD !important;
    border: 2px solid #654321 !important;
    border-radius: 50% !important;
    margin-right: 8px !important;
    width: 16px !important;
    height: 16px !important;
    visibility: visible !important;
    opacity: 1 !important;
    display: inline-block !important;
}

/* Force radio button containers to be visible */
div[data-testid="stRadio"] * {
    visibility: visible !important;
    opacity: 1 !important;
}

/* Dropdown styling - make them white background */
.main .block-container .stForm .stSelectbox > div > div > div,
div[data-testid="stSelectbox"] > div > div > div {
    background-color: #FFFACD !important;
    border: 2px solid #654321 !important;
    border-radius: 8px !important;
    color: #8B4513 !important;
    font-family: 'Uncial Antiqua', 'Cinzel', serif !important;
    font-weight: bold !important;
}
`;

// Add the style to the parent document head
parentDocument.head.appendChild(style);

// Also inject fonts
const fontLink = parentDocument.createElement('link');
fontLink.href = 'https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Uncial+Antiqua&family=MedievalSharp&display=swap';
fontLink.rel = 'stylesheet';
parentDocument.head.appendChild(fontLink);

console.log('CSS injected into parent window');
</script>
""", height=0)

# JavaScript injection using st.components.v1.html but targeting parent window
st.components.v1.html("""
<script>
// Access the parent window (main Streamlit page)
function forceMedievalStyling() {
    try {
        // Try to access parent window
        const parentWindow = window.parent;
        const parentDocument = parentWindow.document;
        
        // Force ALL buttons in parent window
        const buttons = parentDocument.querySelectorAll('button');
        buttons.forEach(button => {
            button.style.setProperty('background', 'linear-gradient(135deg, #8B4513 0%, #A0522D 50%, #CD853F 100%)', 'important');
            button.style.setProperty('background-color', '#8B4513', 'important');
            button.style.setProperty('background-image', 'linear-gradient(135deg, #8B4513 0%, #A0522D 50%, #CD853F 100%)', 'important');
            button.style.setProperty('color', '#FFFACD', 'important');
            button.style.setProperty('border', '2px solid #654321', 'important');
            button.style.setProperty('border-radius', '8px', 'important');
            button.style.setProperty('font-family', "'Cinzel', serif", 'important');
            button.style.setProperty('font-weight', 'bold', 'important');
            button.style.setProperty('text-shadow', '1px 1px 2px rgba(0,0,0,0.8)', 'important');
            button.style.setProperty('box-shadow', 'inset 0 1px 3px rgba(255,255,255,0.2), 0 2px 4px rgba(0,0,0,0.3)', 'important');
        });
        
        // Force ALL h3 headers in parent window
        const headers = parentDocument.querySelectorAll('h3');
        headers.forEach(header => {
            if (header.textContent.includes('Create a New Quest')) {
                header.style.setProperty('color', '#FFFACD', 'important');
                header.style.setProperty('text-shadow', '2px 2px 4px rgba(0,0,0,0.8)', 'important');
            }
        });
        
        // Force ALL labels in parent window
        const labels = parentDocument.querySelectorAll('label');
        labels.forEach(label => {
            label.style.setProperty('color', '#8B4513', 'important');
            label.style.setProperty('font-family', "'Uncial Antiqua', 'Cinzel', serif", 'important');
            label.style.setProperty('font-weight', 'bold', 'important');
            label.style.setProperty('font-size', '18px', 'important');
            label.style.setProperty('background', 'transparent', 'important');
            label.style.setProperty('text-shadow', '1px 1px 2px rgba(255,255,255,0.5)', 'important');
            label.style.setProperty('font-style', 'normal', 'important');
        });
        
        // Force ALL label text elements in parent window
        const labelTexts = parentDocument.querySelectorAll('label span, label div, label p');
        labelTexts.forEach(text => {
            text.style.setProperty('color', '#8B4513', 'important');
            text.style.setProperty('font-family', "'Uncial Antiqua', 'Cinzel', serif", 'important');
            text.style.setProperty('font-weight', 'bold', 'important');
            text.style.setProperty('font-size', '18px', 'important');
            text.style.setProperty('background', 'transparent', 'important');
            text.style.setProperty('text-shadow', '1px 1px 2px rgba(255,255,255,0.5)', 'important');
        });
        
        // Force ALL inputs in parent window
        const inputs = parentDocument.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            if (input.type === 'radio') {
                // Radio buttons - special styling
                input.style.setProperty('background-color', '#FFFACD', 'important');
                input.style.setProperty('border', '2px solid #654321', 'important');
                input.style.setProperty('border-radius', '50%', 'important');
                input.style.setProperty('margin-right', '8px', 'important');
            } else {
                // Regular inputs
                input.style.setProperty('background-color', '#FFFACD', 'important');
                input.style.setProperty('border', '2px solid #654321', 'important');
                input.style.setProperty('border-radius', '8px', 'important');
                input.style.setProperty('color', '#8B4513', 'important');
                input.style.setProperty('font-family', "'Uncial Antiqua', 'Cinzel', serif", 'important');
                input.style.setProperty('font-weight', 'bold', 'important');
            }
        });
        
        // Force radio button labels to be visible - ULTRA AGGRESSIVE
        const radioLabels = parentDocument.querySelectorAll('div[data-testid="stRadio"] label, div[data-testid="stRadio"] label > div, div[data-testid="stRadio"] label span, div[data-testid="stRadio"] label p');
        radioLabels.forEach(label => {
            label.style.setProperty('color', '#8B4513', 'important');
            label.style.setProperty('font-family', "'Uncial Antiqua', 'Cinzel', serif", 'important');
            label.style.setProperty('font-weight', 'bold', 'important');
            label.style.setProperty('background', 'transparent', 'important');
            label.style.setProperty('text-shadow', '1px 1px 2px rgba(255,255,255,0.5)', 'important');
            label.style.setProperty('padding', '5px 0', 'important');
            label.style.setProperty('margin', '5px 0', 'important');
            label.style.setProperty('display', 'block', 'important');
            label.style.setProperty('visibility', 'visible', 'important');
            label.style.setProperty('opacity', '1', 'important');
            label.style.setProperty('font-size', '16px', 'important');
        });
        
        // Force radio button containers to be visible
        const radioContainers = parentDocument.querySelectorAll('div[data-testid="stRadio"], div[data-testid="stRadio"] > div, div[data-testid="stRadio"] > div > div');
        radioContainers.forEach(container => {
            container.style.setProperty('background', 'transparent', 'important');
            container.style.setProperty('border', 'none', 'important');
            container.style.setProperty('padding', '10px 0', 'important');
            container.style.setProperty('margin', '5px 0', 'important');
            container.style.setProperty('display', 'block', 'important');
            container.style.setProperty('visibility', 'visible', 'important');
            container.style.setProperty('opacity', '1', 'important');
        });
        
         // Force login form labels to be cream colored - ULTRA AGGRESSIVE
         const loginLabels = parentDocument.querySelectorAll('section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] .stForm label, section[data-testid="stSidebar"] .stTextInput label');
         loginLabels.forEach(label => {
             label.style.setProperty('color', '#FFFACD', 'important');
             label.style.setProperty('background', 'transparent', 'important');
             label.style.setProperty('background-color', 'transparent', 'important');
             label.style.setProperty('background-image', 'none', 'important');
             label.style.setProperty('-webkit-text-fill-color', '#FFFACD', 'important');
             label.style.setProperty('text-fill-color', '#FFFACD', 'important');
             
             // Also target any child elements
             const childElements = label.querySelectorAll('span, div, p');
             childElements.forEach(child => {
                 child.style.setProperty('color', '#FFFACD', 'important');
                 child.style.setProperty('background', 'transparent', 'important');
                 child.style.setProperty('background-color', 'transparent', 'important');
                 child.style.setProperty('background-image', 'none', 'important');
                 child.style.setProperty('-webkit-text-fill-color', '#FFFACD', 'important');
                 child.style.setProperty('text-fill-color', '#FFFACD', 'important');
             });
         });
         
        // Force password field to match email field width
        const passwordInputs = parentDocument.querySelectorAll('section[data-testid="stSidebar"] input[type="password"]');
        passwordInputs.forEach(input => {
            input.style.setProperty('width', '98%', 'important');
            input.style.setProperty('max-width', '280px', 'important');
            
            // Also target the parent containers
            const parentDiv = input.closest('div');
            if (parentDiv) {
                parentDiv.style.setProperty('width', '98%', 'important');
                parentDiv.style.setProperty('max-width', '280px', 'important');
            }
            
            const grandParentDiv = parentDiv?.parentElement;
            if (grandParentDiv) {
                grandParentDiv.style.setProperty('width', '98%', 'important');
                grandParentDiv.style.setProperty('max-width', '280px', 'important');
            }
        });
         
         // Force input field widths to align with buttons
         const loginInputs = parentDocument.querySelectorAll('section[data-testid="stSidebar"] .stTextInput, section[data-testid="stSidebar"] .stTextInput > div, section[data-testid="stSidebar"] .stTextInput > div > div');
         loginInputs.forEach(input => {
             input.style.setProperty('width', '98%', 'important');
             input.style.setProperty('max-width', '280px', 'important');
         });
        
        // Force dropdown styling
        const dropdowns = parentDocument.querySelectorAll('div[data-testid="stSelectbox"] > div > div > div');
        dropdowns.forEach(dropdown => {
            dropdown.style.setProperty('background-color', '#FFFACD', 'important');
            dropdown.style.setProperty('border', '2px solid #654321', 'important');
            dropdown.style.setProperty('border-radius', '8px', 'important');
            dropdown.style.setProperty('color', '#8B4513', 'important');
            dropdown.style.setProperty('font-family', "'Uncial Antiqua', 'Cinzel', serif", 'important');
            dropdown.style.setProperty('font-weight', 'bold', 'important');
        });
        
    } catch (error) {
        console.log('Error accessing parent window:', error);
    }
}

// Run immediately and continuously
forceMedievalStyling();
const medievalInterval = setInterval(forceMedievalStyling, 200); // Run every 200ms for more aggressive override

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (medievalInterval) {
        clearInterval(medievalInterval);
    }
});

// Also run when DOM changes in parent
try {
    const parentWindow = window.parent;
    const parentDocument = parentWindow.document;
    const observer = new MutationObserver(forceMedievalStyling);
    observer.observe(parentDocument.body, { childList: true, subtree: true });
} catch (error) {
    console.log('Error setting up observer:', error);
}
</script>
""", height=0)

# Apply the fantasy title styling directly with better font loading
st.components.v1.html("""
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Uncial+Antiqua&family=MedievalSharp&display=swap" rel="stylesheet">
<div style="
    background: linear-gradient(135deg, #FFD700 0%, #FFA500 25%, #FFDF00 50%, #FFA500 75%, #FFD700 100%);
    background-size: 400% 400%;
    animation: gradientShift 4s ease infinite;
    border: 4px solid #8B4513;
    border-radius: 20px;
    padding: 15px 30px;
    margin: 15px 0;
    text-align: center;
    box-shadow: 
        0 0 20px rgba(255, 215, 0, 0.6),
        inset 0 2px 8px rgba(139, 69, 19, 0.3),
        0 6px 15px rgba(0, 0, 0, 0.3);
    position: relative;
    overflow: visible;
    min-height: 80px;
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
        font-size: 2rem !important;
        color: #7B2CBF !important;
        text-align: center !important;
        text-shadow: 
            2px 2px 0px #5A189A,
            4px 4px 8px rgba(0, 0, 0, 0.8),
            0 0 15px rgba(123, 44, 191, 0.5) !important;
        margin: 0 !important;
        font-weight: bold !important;
        letter-spacing: 2px !important;
        position: relative;
        z-index: 2;
        padding: 5px 0;
    ">⚔️ 🧙‍♂️ BENCON 2026 🧙‍♀️ ⚔️</h1>
    <div class="fantasy-subtitle" style="padding: 2px 0; font-size: 0.8rem;">✨ BE YER BEST LIL' FREAK ✨</div>
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

# Add collapse button under the banner using Streamlit button
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("☰ Toggle Navigation", key="sidebar_toggle", use_container_width=True):
        # Toggle sidebar state
        if 'sidebar_collapsed' not in st.session_state:
            st.session_state.sidebar_collapsed = False
        st.session_state.sidebar_collapsed = not st.session_state.sidebar_collapsed
        st.rerun()

# Add CSS to hide the built-in Streamlit collapse button
st.markdown("""
<style>
/* Hide the built-in << collapse button - comprehensive selectors */
button[kind="header"],
section[data-testid="stSidebar"] button[kind="header"],
section[data-testid="stSidebar"] > div > button:first-child,
section[data-testid="stSidebar"] > div > div > button:first-child,
[data-testid="collapsedControl"],
button[aria-label*="collapse"],
button[aria-label*="Collapse"],
button[title*="collapse"],
button[title*="Collapse"] {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    width: 0 !important;
    height: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
    pointer-events: none !important;
}

/* Also hide it in the sidebar header area */
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] button:first-child,
section[data-testid="stSidebar"] header button,
.css-1cypcdb button:first-child {
    display: none !important;
    visibility: hidden !important;
}
</style>
""", unsafe_allow_html=True)

# Add CSS to hide sidebar when collapsed
if st.session_state.get('sidebar_collapsed', False):
    st.markdown("""
    <style>
    section[data-testid="stSidebar"] {
        transform: translateX(-100%) !important;
        transition: transform 0.3s ease !important;
        pointer-events: none !important;
        z-index: -1 !important;
    }
    
    /* Ensure main content takes full width when sidebar is collapsed */
    .main .block-container {
        max-width: 100% !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    
    /* Mobile-specific fixes */
    @media (max-width: 768px) {
        section[data-testid="stSidebar"] {
            width: 0 !important;
            min-width: 0 !important;
            max-width: 0 !important;
        }
        
        .main .block-container {
            margin-left: 0 !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Also add JavaScript to ensure sidebar is properly hidden/shown
    st.markdown("""
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        const sidebar = document.querySelector('section[data-testid="stSidebar"]');
        if (sidebar) {
            sidebar.style.transform = 'translateX(-100%)';
            sidebar.style.transition = 'transform 0.3s ease';
            sidebar.style.pointerEvents = 'none';
            sidebar.style.zIndex = '-1';
            sidebar.classList.add('sidebar-collapsed');
        }
        
        // Ensure main content takes full width
        const mainContent = document.querySelector('.main .block-container');
        if (mainContent) {
            mainContent.style.maxWidth = '100%';
            mainContent.style.paddingLeft = '1rem';
            mainContent.style.paddingRight = '1rem';
        }
    });
    </script>
    """, unsafe_allow_html=True)
else:
    # Add CSS to ensure sidebar is properly shown when not collapsed
    st.markdown("""
    <style>
    section[data-testid="stSidebar"] {
        transform: translateX(0) !important;
        transition: transform 0.3s ease !important;
        pointer-events: auto !important;
        z-index: 9999 !important;
    }
    
    /* Reset main content when sidebar is shown */
    .main .block-container {
        max-width: none !important;
        padding-left: inherit !important;
        padding-right: inherit !important;
    }
    
    /* Mobile-specific fixes for expanded sidebar */
    @media (max-width: 768px) {
        section[data-testid="stSidebar"] {
            width: inherit !important;
            min-width: inherit !important;
            max-width: inherit !important;
            z-index: 99999 !important;  /* Even higher z-index on mobile */
        }
        
        .main .block-container {
            margin-left: inherit !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Add JavaScript to ensure sidebar is properly shown
    st.markdown("""
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        const sidebar = document.querySelector('section[data-testid="stSidebar"]');
        if (sidebar) {
            sidebar.style.transform = 'translateX(0)';
            sidebar.style.transition = 'transform 0.3s ease';
            sidebar.style.pointerEvents = 'auto';
            sidebar.style.zIndex = '9999';
            sidebar.classList.remove('sidebar-collapsed');
        }
        
        // Reset main content
        const mainContent = document.querySelector('.main .block-container');
        if (mainContent) {
            mainContent.style.maxWidth = '';
            mainContent.style.paddingLeft = '';
            mainContent.style.paddingRight = '';
        }
    });
    </script>
    """, unsafe_allow_html=True)

# Tavern-specific sidebar styling removed (no longer needed)

# Custom CSS for button styling with neon purple theme
st.markdown("""
<style>
/* Form input styling - white backgrounds for better visibility - MORE SPECIFIC */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > select,
.stNumberInput > div > div > input,
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-testid="stSelectbox"] select,
div[data-testid="stNumberInput"] input {
    background-color: white !important;
    color: #8B4513 !important;
    border: 2px solid #8B4513 !important;
    border-radius: 5px !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus,
.stSelectbox > div > div > select:focus,
.stNumberInput > div > div > input:focus,
div[data-testid="stTextInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus,
div[data-testid="stSelectbox"] select:focus,
div[data-testid="stNumberInput"] input:focus {
    background-color: white !important;
    color: #8B4513 !important;
    border-color: #7B2CBF !important;
    box-shadow: 0 0 5px rgba(123, 44, 191, 0.5) !important;
}

/* Additional styling for form labels to match brown theme - FORCE TRANSPARENT */
.stTextInput > div > div > label,
.stTextArea > div > div > label,
.stSelectbox > div > div > label,
.stNumberInput > div > div > label,
div[data-testid="stTextInput"] label,
div[data-testid="stTextArea"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stNumberInput"] label,
div[data-testid="stSelectbox"] > div > div > label,
.stSelectbox > div > div > label,
div[data-testid="stSelectbox"] label[data-testid="stSelectboxLabel"],
.stSelectbox label[data-testid="stSelectboxLabel"],
div[data-testid="stSelectbox"] > div > div > div > label,
.stSelectbox > div > div > div > label {
    color: #8B4513 !important;
    font-weight: bold !important;
    background-color: transparent !important;
    background: transparent !important;
    background-image: none !important;
}

/* Dropdown containers - transparent for Create Quest form only */
.main .block-container .stForm .stSelectbox > div,
.main .block-container .stForm .stSelectbox > div > div {
    background-color: transparent !important;
    background: transparent !important;
    background-image: none !important;
}

/* Radio button options text - Create Quest form only */
.main .block-container .stForm .stRadio label > div,
.main .block-container .stForm .stRadio label span,
.main .block-container .stForm div[data-testid="stRadio"] label > div,
.main .block-container .stForm div[data-testid="stRadio"] label span {
    color: #8B4513 !important;
    font-family: 'Uncial Antiqua', 'Cinzel', serif !important;
    font-weight: bold !important;
}

/* Make dropdown arrows visible (not transparent) */
div[data-testid="stSelectbox"] svg,
.stSelectbox svg,
div[data-testid="stSelectbox"] .stSelectbox svg,
.stSelectbox .stSelectbox svg {
    color: #8B4513 !important;
    fill: #8B4513 !important;
    opacity: 1 !important;
}

/* Force override any conflicting styles */
input[type="text"], input[type="number"], textarea, select {
    background-color: white !important;
    color: #8B4513 !important;
    border: 2px solid #8B4513 !important;
}

/* Make text cursor (caret) black in input fields */
input[type="text"], input[type="number"], textarea {
    caret-color: black !important;
}

/* Make dropdown search box transparent */
div[data-testid="stSelectbox"] input[type="text"],
.stSelectbox input[type="text"] {
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
}

/* Quest Host/GM field styling - brown and bold text */
div[data-testid="stTextInput"] input[disabled],
.stTextInput input[disabled] {
    color: #8B4513 !important;
    font-weight: bold !important;
    background-color: #f5f5f5 !important;
    opacity: 1 !important;
}

/* Make sure disabled text is visible across all browsers */
input[disabled] {
    color: #8B4513 !important;
    opacity: 1 !important;
    -webkit-text-fill-color: #8B4513 !important;
    text-fill-color: #8B4513 !important;
}

/* Additional specificity for Streamlit disabled inputs */
div[data-testid="stTextInput"] input[disabled],
.stTextInput input[disabled],
div[data-testid="stTextInput"] input[readonly],
.stTextInput input[readonly] {
    color: #8B4513 !important;
    opacity: 1 !important;
    -webkit-text-fill-color: #8B4513 !important;
    text-fill-color: #8B4513 !important;
    font-weight: bold !important;
}

/* Make Quest Name field text brown */
div[data-testid="stTextInput"] input:not([disabled]),
.stTextInput input:not([disabled]) {
    color: #8B4513 !important;
}

/* Additional Streamlit-specific overrides */
.stApp input, .stApp textarea, .stApp select {
    background-color: white !important;
    color: #8B4513 !important;
    border: 2px solid #8B4513 !important;
}

/* Target all form elements within Streamlit */
div[data-testid="stForm"] input,
div[data-testid="stForm"] textarea,
div[data-testid="stForm"] select {
    background-color: white !important;
    color: #8B4513 !important;
    border: 2px solid #8B4513 !important;
}

/* Specific styling for Streamlit selectbox/dropdown components */
div[data-testid="stSelectbox"] > div > div > div,
div[data-testid="stSelectbox"] .stSelectbox > div > div > div,
.stSelectbox > div > div > div {
    background-color: white !important;
    color: #8B4513 !important;
    border: 2px solid #8B4513 !important;
}

/* Target the dropdown input field specifically - make white to match other fields */
div[data-testid="stSelectbox"] input,
.stSelectbox input,
div[data-testid="stSelectbox"] .stSelectbox input {
    background-color: white !important;
    color: #8B4513 !important;
    border: 2px solid #8B4513 !important;
}

/* Target dropdown options/items */
div[data-testid="stSelectbox"] [role="option"],
.stSelectbox [role="option"],
div[data-testid="stSelectbox"] .stSelectbox [role="option"] {
    background-color: white !important;
    color: #8B4513 !important;
}

/* Target the dropdown container - make white to match other fields */
div[data-testid="stSelectbox"] > div,
.stSelectbox > div {
    background-color: white !important;
}

/* Force override for selectbox elements but exclude labels - REMOVED TOO BROAD */

/* Ensure labels above dropdowns have transparent backgrounds - more specific targeting */
div[data-testid="stSelectbox"] > div > div > label,
.stSelectbox > div > div > label,
div[data-testid="stSelectbox"] label[data-testid="stSelectboxLabel"],
.stSelectbox label[data-testid="stSelectboxLabel"] {
    background-color: transparent !important;
    background: transparent !important;
    background-image: none !important;
    color: #8B4513 !important;
    font-weight: bold !important;
}

/* Completely disable typing and searching in dropdown input fields - keep white background */
div[data-testid="stSelectbox"] input,
.stSelectbox input {
    background-color: white !important;
    color: #8B4513 !important;
    border: 2px solid #8B4513 !important;
    pointer-events: none !important;
    cursor: pointer !important;
    user-select: none !important;
    -webkit-user-select: none !important;
    -moz-user-select: none !important;
    -ms-user-select: none !important;
    /* Don't hide completely - just make it non-typeable */
}

/* Make dropdown search box completely transparent and remove borders */
div[data-testid="stSelectbox"] input[type="text"],
.stSelectbox input[type="text"] {
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
    color: transparent !important;
}

/* Hide the search input completely when not focused */
div[data-testid="stSelectbox"] input[type="text"]:not(:focus),
.stSelectbox input[type="text"]:not(:focus) {
    display: none !important;
}

/* Make sure the dropdown container is clickable but not typeable - white background to match other fields */
div[data-testid="stSelectbox"] > div > div > div,
.stSelectbox > div > div > div {
    background-color: white !important;
    color: #8B4513 !important;
    border: 2px solid #8B4513 !important;
    border-radius: 8px !important;
    cursor: pointer !important;
    pointer-events: auto !important;
}


/* Fantasy day container styling */
.fantasy-day-header {
    background: linear-gradient(135deg, #8B4513 0%, #A0522D 50%, #CD853F 100%);
    border: 3px solid #654321;
    border-radius: 15px;
    padding: 20px;
    margin: 20px 0;
    color: #FFFACD !important;
    font-family: 'Uncial Antiqua', 'Cinzel', serif !important;
    font-weight: bold;
    font-size: 1.4em;
    text-align: center;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
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

/* Themed backgrounds for all pages */
.stApp {
    background: linear-gradient(135deg, #2C1810 0%, #3D2817 25%, #4A2C17 50%, #3D2817 75%, #2C1810 100%) !important;
    background-size: 400% 400% !important;
    animation: gradientShift 8s ease infinite !important;
}

/* Main content area background - yellowish color */
.main .block-container {
    background: linear-gradient(135deg, #F4E4BC 0%, #E6D3A3 50%, #D4C4A8 100%) !important;
    border: 3px solid #8B4513 !important;
    border-radius: 15px !important;
    margin: 10px !important;
    padding: 20px !important;
    box-shadow: 
        0 4px 8px rgba(0,0,0,0.3),
        inset 0 1px 3px rgba(255,255,255,0.3) !important;
}

/* Sidebar themed background */
section[data-testid="stSidebar"] {
    background: linear-gradient(135deg, #8B4513 0%, #A0522D 50%, #CD853F 100%) !important;
    border-right: 3px solid #654321 !important;
    box-shadow: 
        inset 0 2px 4px rgba(255,255,255,0.2),
        inset 0 -2px 4px rgba(101, 67, 33, 0.3),
        0 4px 8px rgba(0,0,0,0.3) !important;
    min-width: 300px !important;
}

/* Allow sidebar to be collapsed and hide it when collapsed */
section[data-testid="stSidebar"][aria-hidden="true"],
section[data-testid="stSidebar"].sidebar-collapsed {
    display: none !important;
    visibility: hidden !important;
}

/* Sidebar content styling */
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] .stText,
section[data-testid="stSidebar"] .stWrite {
    color: #FFFACD !important;
    font-family: 'Cinzel', serif !important;
}

/* Sidebar headers */
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #FFFACD !important;
    font-family: 'Uncial Antiqua', 'Cinzel', serif !important;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.8) !important;
}

/* Sidebar buttons */
section[data-testid="stSidebar"] .stButton button {
    background: linear-gradient(135deg, #654321 0%, #8B4513 50%, #A0522D 100%) !important;
    color: #FFFACD !important;
    border: 2px solid #654321 !important;
    border-radius: 8px !important;
    font-family: 'Cinzel', serif !important;
    font-weight: bold !important;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.8) !important;
    box-shadow: 
        inset 0 1px 3px rgba(255,255,255,0.2),
        0 2px 4px rgba(0,0,0,0.3) !important;
}

section[data-testid="stSidebar"] .stButton button:hover {
    background: linear-gradient(135deg, #8B4513 0%, #A0522D 50%, #CD853F 100%) !important;
    transform: translateY(-1px) !important;
    box-shadow: 
        inset 0 1px 3px rgba(255,255,255,0.3),
        0 4px 8px rgba(0,0,0,0.4) !important;
}

/* Quest Counter page specific styling */
.quest-section-wide {
    background: transparent !important;
}

/* Profile page specific styling */
.main .block-container h1,
.main .block-container h2,
.main .block-container h3 {
    color: #8B4513 !important;
    font-family: 'Uncial Antiqua', 'Cinzel', serif !important;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3) !important;
}

/* Profile page styling - simplified without print/download buttons */

/* General text styling */
.main .block-container .stMarkdown,
.main .block-container .stText,
.main .block-container .stWrite {
    color: #654321 !important;
    font-family: 'Cinzel', serif !important;
}

/* Create Quest form styling - bold fantasy font for all text */
.main .block-container .stForm label,
.main .block-container .stTextInput label,
.main .block-container .stSelectbox label,
.main .block-container .stNumberInput label,
.main .block-container .stTextArea label,
.main .block-container .stRadio label {
    color: #8B4513 !important;
    font-family: 'Uncial Antiqua', 'Cinzel', serif !important;
    font-weight: bold !important;
    font-size: 18px !important;
    text-shadow: 1px 1px 2px rgba(255,255,255,0.8) !important;
}

/* FRESH CREATE QUEST FORM STYLING - Clean slate */
/* Form container - completely transparent */
.main .block-container .stForm {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    margin: 0 !important;
}

/* Form labels - brown text and BOLD for better readability */
.main .block-container .stForm label,
.main .block-container .stTextInput label,
.main .block-container .stSelectbox label,
.main .block-container .stNumberInput label,
.main .block-container .stTextArea label,
.main .block-container .stRadio label {
    color: #8B4513 !important;
    font-family: 'Uncial Antiqua', 'Cinzel', serif !important;
    font-weight: bold !important;
    font-size: 18px !important;
    background: transparent !important;
    text-shadow: 1px 1px 2px rgba(255,255,255,0.5) !important;
}

/* Radio buttons - transparent background, brown text */
.main .block-container .stForm .stRadio {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    margin: 0 !important;
}

.main .block-container .stForm .stRadio label {
    color: #8B4513 !important;
    font-family: 'Uncial Antiqua', 'Cinzel', serif !important;
    font-weight: bold !important;
    background: transparent !important;
    text-shadow: 1px 1px 2px rgba(255,255,255,0.5) !important;
}

/* Brown container form inputs - cream background for contrast */
.main .block-container .stForm .stTextInput > div > div > input,
.main .block-container .stForm .stTextArea > div > div > textarea,
.main .block-container .stForm .stSelectbox > div > div > div,
.main .block-container .stForm .stNumberInput > div > div > input {
    background-color: #FFFACD !important;
    border: 2px solid #654321 !important;
    border-radius: 8px !important;
    color: #8B4513 !important;
    font-family: 'Uncial Antiqua', 'Cinzel', serif !important;
    font-weight: bold !important;
}

/* Dropdown containers - transparent for Create Quest form only */
.main .block-container .stForm .stSelectbox > div,
.main .block-container .stForm .stSelectbox > div > div {
    background-color: transparent !important;
    background: transparent !important;
    background-image: none !important;
}

/* Create Quest button - matches overall theme */
.main .block-container .stForm .stButton button {
    background: linear-gradient(135deg, #8B4513 0%, #A0522D 50%, #CD853F 100%) !important;
    color: #FFFACD !important;
    border: 2px solid #654321 !important;
    border-radius: 8px !important;
    font-family: 'Cinzel', serif !important;
    font-weight: bold !important;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.8) !important;
    box-shadow: 
        inset 0 1px 3px rgba(255,255,255,0.2),
        0 2px 4px rgba(0,0,0,0.3) !important;
    transition: all 0.3s ease !important;
}

.main .block-container .stForm .stButton button:hover {
    background: linear-gradient(135deg, #A0522D 0%, #CD853F 50%, #DEB887 100%) !important;
    transform: translateY(-1px) !important;
    box-shadow: 
        inset 0 1px 3px rgba(255,255,255,0.3),
        0 4px 8px rgba(0,0,0,0.4) !important;
}

/* Focus states for Create Quest form inputs - brown container */
.main .block-container .stForm .stTextInput input:focus,
.main .block-container .stForm .stSelectbox select:focus,
.main .block-container .stForm .stNumberInput input:focus,
.main .block-container .stForm .stTextArea textarea:focus {
    border-color: #FFFACD !important;
    box-shadow: 0 0 8px rgba(255, 250, 205, 0.5) !important;
}

/* Login form container - styled box */
section[data-testid="stSidebar"] .stForm {
    background: linear-gradient(135deg, #654321 0%, #8B4513 50%, #A0522D 100%) !important;
    border: 3px solid #4A2C17 !important;
    border-radius: 15px !important;
    padding: 20px !important;
    margin: 10px 0 !important;
    box-shadow: 
        0 4px 8px rgba(0,0,0,0.5),
        inset 0 1px 3px rgba(255,255,255,0.2) !important;
}

/* Additional styling for the Adventurer's Gate container */
section[data-testid="stSidebar"] .stMarkdown > div {
    background: transparent !important;
}

/* Ensure tabs are styled properly within the container */
section[data-testid="stSidebar"] .stTabs {
    background: transparent !important;
}

section[data-testid="stSidebar"] .stTabs > div {
    background: transparent !important;
}

/* Login form labels - cream color - ULTRA SPECIFIC */
section[data-testid="stSidebar"] .stForm .stTextInput label,
section[data-testid="stSidebar"] .stTextInput label,
section[data-testid="stSidebar"] .stForm label,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stForm .stTextInput > div > div > label,
section[data-testid="stSidebar"] .stTextInput > div > div > label,
section[data-testid="stSidebar"] .stForm .stTextInput > div > label,
section[data-testid="stSidebar"] .stTextInput > div > label,
section[data-testid="stSidebar"] .stForm .stTextInput label span,
section[data-testid="stSidebar"] .stTextInput label span,
section[data-testid="stSidebar"] .stForm .stTextInput label div,
section[data-testid="stSidebar"] .stTextInput label div,
section[data-testid="stSidebar"] .stForm .stTextInput label p,
section[data-testid="stSidebar"] .stTextInput label p {
    color: #FFFACD !important;
    font-family: 'Cinzel', serif !important;
    font-weight: bold !important;
    font-size: 14px !important;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.8) !important;
    background: transparent !important;
    background-color: transparent !important;
    background-image: none !important;
    -webkit-text-fill-color: #FFFACD !important;
    text-fill-color: #FFFACD !important;
}

/* Login form inputs */
section[data-testid="stSidebar"] .stTextInput input,
section[data-testid="stSidebar"] .stTextInput > div > div > input {
    background: #FFFACD !important;
    border: 2px solid #8B4513 !important;
    border-radius: 8px !important;
    color: #654321 !important;
    font-family: 'Cinzel', serif !important;
    padding: 8px 12px !important;
}

section[data-testid="stSidebar"] .stTextInput input:focus {
    border-color: #A0522D !important;
    box-shadow: 0 0 8px rgba(160, 82, 45, 0.3) !important;
}

/* Password field specific width - match email field width */
section[data-testid="stSidebar"] .stTextInput input[type="password"],
section[data-testid="stSidebar"] .stTextInput input[type="password"] + div,
section[data-testid="stSidebar"] .stTextInput > div:has(input[type="password"]),
section[data-testid="stSidebar"] .stTextInput > div:has(input[type="password"]) > div {
    width: 98% !important;
    max-width: 280px !important;
}

/* Password container width - make it wider to align with buttons */
section[data-testid="stSidebar"] .stTextInput > div > div {
    position: relative;
    width: 98% !important;
    max-width: 280px !important;
}

section[data-testid="stSidebar"] .stTextInput > div {
    width: 98% !important;
    max-width: 280px !important;
}

section[data-testid="stSidebar"] .stTextInput {
    width: 98% !important;
    max-width: 280px !important;
}

/* Hide Streamlit deploy button */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* Mobile-specific sizing fixes */
@media (max-width: 768px) {
    /* Ensure proper mobile viewport */
    .main .block-container {
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
        max-width: 100% !important;
    }
    
    /* Fix form containers on mobile */
    .stForm {
        padding: 0.5rem !important;
    }
    
    /* Fix button sizing on mobile */
    .stButton button {
        width: 100% !important;
        min-height: 44px !important; /* iOS touch target minimum */
        font-size: 16px !important; /* Prevent zoom on iOS */
    }
    
    /* Fix input field sizing on mobile */
    .stTextInput input,
    .stTextArea textarea,
    .stSelectbox select,
    .stNumberInput input {
        font-size: 16px !important; /* Prevent zoom on iOS */
        min-height: 44px !important; /* iOS touch target minimum */
        width: 100% !important;
        max-width: 100% !important;
    }
    
    /* Fix sidebar width on mobile */
    section[data-testid="stSidebar"] {
        width: 280px !important;
        min-width: 280px !important;
        max-width: 280px !important;
    }
    
    /* Fix quest cards on mobile */
    .quest-card {
        margin: 0.5rem 0 !important;
        padding: 1rem !important;
    }
    
    /* Fix table responsiveness */
    .stDataFrame {
        overflow-x: auto !important;
        width: 100% !important;
    }
    
    /* Fix markdown containers */
    .stMarkdownContainer {
        padding: 0.5rem !important;
    }
    
    /* Fix tabs on mobile */
    .stTabs [role="tablist"] {
        flex-wrap: wrap !important;
    }
    
    .stTabs [role="tab"] {
        min-width: auto !important;
        flex: 1 !important;
        font-size: 14px !important;
    }
}

/* Extra small mobile devices */
@media (max-width: 480px) {
    .main .block-container {
        padding-left: 0.25rem !important;
        padding-right: 0.25rem !important;
    }
    
    .stForm {
        padding: 0.25rem !important;
    }
    
    /* Smaller sidebar for very small screens */
    section[data-testid="stSidebar"] {
        width: 260px !important;
        min-width: 260px !important;
        max-width: 260px !important;
    }
    
    /* Adjust banner text for very small screens */
    .stApp h1 {
        font-size: 1.8rem !important;
        line-height: 1.2 !important;
    }
    
    .fantasy-subtitle {
        font-size: 0.6rem !important;
    }
}
header {visibility: hidden;}
.stDeployButton {display:none;}
div[data-testid="stToolbar"] {display:none;}

/* Password visibility icon positioning */
section[data-testid="stSidebar"] .stTextInput button {
    position: absolute !important;
    right: 8px !important;
    top: 50% !important;
    transform: translateY(-50%) !important;
    background: transparent !important;
    border: none !important;
    padding: 4px !important;
    z-index: 10 !important;
}

/* Login form buttons */
section[data-testid="stSidebar"] .stForm .stButton button {
    background: linear-gradient(135deg, #8B4513 0%, #A0522D 50%, #CD853F 100%) !important;
    color: #FFFACD !important;
    border: 2px solid #654321 !important;
    border-radius: 8px !important;
    font-family: 'Cinzel', serif !important;
    font-weight: bold !important;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.8) !important;
    box-shadow: 
        inset 0 1px 3px rgba(255,255,255,0.2),
        0 2px 4px rgba(0,0,0,0.3) !important;
    transition: all 0.3s ease !important;
}

section[data-testid="stSidebar"] .stForm .stButton button:hover {
    background: linear-gradient(135deg, #A0522D 0%, #CD853F 50%, #DEB887 100%) !important;
    transform: translateY(-1px) !important;
    box-shadow: 
        inset 0 1px 3px rgba(255,255,255,0.3),
        0 4px 8px rgba(0,0,0,0.4) !important;
}
</style>

<script>
document.addEventListener('DOMContentLoaded', function() {
    // Disable typing in all selectbox input fields but allow clicking
    const selectboxInputs = document.querySelectorAll('div[data-testid="stSelectbox"] input, .stSelectbox input');
    selectboxInputs.forEach(input => {
        // Prevent all keyboard events but allow mouse events
        input.addEventListener('keydown', function(e) {
            e.preventDefault();
            e.stopPropagation();
            return false;
        });
        input.addEventListener('keypress', function(e) {
            e.preventDefault();
            e.stopPropagation();
            return false;
        });
        input.addEventListener('keyup', function(e) {
            e.preventDefault();
            e.stopPropagation();
            return false;
        });
        input.addEventListener('input', function(e) {
            e.preventDefault();
            e.stopPropagation();
            return false;
        });
        input.addEventListener('paste', function(e) {
            e.preventDefault();
            e.stopPropagation();
            return false;
        });
        
        // Make input readonly and disable text selection
        input.readOnly = true;
        input.style.userSelect = 'none';
        input.style.webkitUserSelect = 'none';
        input.style.mozUserSelect = 'none';
        input.style.msUserSelect = 'none';
        
        // Allow clicking but prevent typing
        input.style.pointerEvents = 'auto';
        input.style.cursor = 'pointer';
    });
    
    // Continuously monitor for new selectbox inputs
    const selectboxInterval = setInterval(function() {
        const newInputs = document.querySelectorAll('div[data-testid="stSelectbox"] input, .stSelectbox input');
        newInputs.forEach(input => {
            if (!input.readOnly) {
                input.readOnly = true;
                input.style.userSelect = 'none';
                input.style.webkitUserSelect = 'none';
                input.style.mozUserSelect = 'none';
                input.style.msUserSelect = 'none';
                input.style.pointerEvents = 'auto';
                input.style.cursor = 'pointer';
            }
        });
    }, 1000); // Reduced frequency from 100ms to 1 second
    
    // Cleanup on page unload
    window.addEventListener('beforeunload', () => {
        if (selectboxInterval) {
            clearInterval(selectboxInterval);
        }
    });
});
</script>
""", unsafe_allow_html=True)

# User Login Section
# Add Toggle Navigation button at the top of sidebar
if st.sidebar.button("☰ Toggle Navigation", key="sidebar_toggle_top", use_container_width=True):
    # Toggle sidebar state
    if 'sidebar_collapsed' not in st.session_state:
        st.session_state.sidebar_collapsed = False
    st.session_state.sidebar_collapsed = not st.session_state.sidebar_collapsed
    st.rerun()

st.sidebar.header("🎭 Knave Check")

# Show password reset dialog if requested
if st.session_state.show_password_reset:
    st.sidebar.subheader("🔒 Password Reset")
    
    # Check if we have a hint waiting for any email
    reset_email = None
    for email in st.session_state.password_reset_codes:
        reset_email = email
        break
    
    if reset_email:
        # Show password reset form with hint
        st.sidebar.info(f"Password hint for {reset_email}")
        with st.sidebar.form("reset_password_form"):
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
                else:
                    result, message = reset_password(reset_email, new_password)
                    if result == True:
                        st.sidebar.success(message)
                        st.session_state.show_password_reset = False
                        # Clear reset data
                        if reset_email in st.session_state.password_reset_codes:
                            del st.session_state.password_reset_codes[reset_email]
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
            request_reset_btn = st.form_submit_button("Show Password Hint")
            cancel_reset_btn = st.form_submit_button("Cancel")
            
            if request_reset_btn:
                if reset_email:
                    result, message = reset_password(reset_email, None)
                    if result == "hint_shown":
                        st.sidebar.info(message)
                        # Store email for password reset
                        if "password_reset_codes" not in st.session_state:
                            st.session_state.password_reset_codes = {}
                        st.session_state.password_reset_codes[reset_email] = "hint_shown"
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
            # Show regular registration form
            with st.form("register_form"):
                reg_email = st.text_input("Email:")
                reg_password = st.text_input("Password (Goblin Security is Shit Use a Random Pass):", type="password")
                display_name = st.text_input("Adventurer Name:")
                
                # Avatar selection with better formatting
                st.write("**Choose your avatar:**")
                selected_avatar = st.selectbox("Avatar:", 
                                             options=list(AVATAR_OPTIONS.keys()),
                                             format_func=lambda x: f"{x} {AVATAR_OPTIONS[x]}",
                                             label_visibility="collapsed")
                st.write(f"Preview: {selected_avatar} {AVATAR_OPTIONS[selected_avatar]}")
                
                # Pronouns selection
                st.write("**Your pronouns:**")
                pronouns = st.selectbox("Pronouns:", PRONOUN_OPTIONS, label_visibility="collapsed")
                
                # Bio field
                st.write("**Bio (optional):**")
                bio = st.text_area("Bio:", 
                                 placeholder="Tell us about yourself...",
                                 height=100,
                                 help="Share a bit about yourself with other adventurers!",
                                 label_visibility="collapsed")
                
                register_btn = st.form_submit_button("Create Account")
                
                if register_btn:
                    print(f"🔍 DEBUG: Registration button clicked for email: {reg_email}")
                    result, message = register_user(reg_email, reg_password, display_name, selected_avatar, pronouns, bio)
                    if result == True:
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
            
            new_bio = st.text_area("Bio (optional):", 
                                 value=user.get('bio', ''),
                                 placeholder="Tell us about yourself...",
                                 height=100)
            
            col1, col2 = st.columns(2)
            with col1:
                save_btn = st.form_submit_button("Save")
            with col2:
                cancel_btn = st.form_submit_button("Cancel")
            
            if save_btn:
                update_user_profile(user['email'], new_name, new_avatar, new_pronouns, new_bio)
                st.sidebar.success("Profile updated!")
                st.session_state.show_profile = False
                st.rerun()
            
            if cancel_btn:
                st.session_state.show_profile = False
                st.rerun()
    
    if st.sidebar.button("Logout"):
        logout_user()
        st.rerun()

# Navigation section - show first when logged in
if st.session_state.current_user:
    st.sidebar.markdown("---")
    
    # Navigation header
    st.sidebar.markdown("""
    <div style="background: linear-gradient(135deg, #8B4513 0%, #A0522D 25%, #CD853F 50%, #D2691E 75%, #8B4513 100%);
               border: 3px solid #654321; border-radius: 15px; padding: 10px; margin: 10px 0;
               box-shadow: inset 0 2px 4px rgba(255,255,255,0.3), 0 4px 8px rgba(0,0,0,0.3);">
        <h4 style="color: #FFFACD; text-align: center; margin: 0 0 15px 0; 
                 text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
                 font-family: 'Uncial Antiqua', 'Cinzel', serif;">
            🚀 Buzzy's Fast Travel Depot 🚀
        </h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation buttons as vertical list with fire emoji for active page
    quest_counter_label = "🗓️ Quest Counter 🔥" if st.session_state.current_page == "Quest Counter" else "🗓️ Quest Counter"
    if st.sidebar.button(quest_counter_label, use_container_width=True, key="nav_quest_counter",
            type="primary" if st.session_state.current_page == "Quest Counter" else "secondary"):
        if st.session_state.current_page != "Quest Counter":
            st.session_state.current_page = "Quest Counter"
            st.session_state.viewing_user_schedule = None
            st.session_state.last_user_click = None
            st.rerun()

    create_quest_label = "⚔️ Create Quest 🔥" if st.session_state.current_page == "Create Quest" else "⚔️ Create Quest"
    if st.sidebar.button(create_quest_label, use_container_width=True, key="nav_create_quest",
            type="primary" if st.session_state.current_page == "Create Quest" else "secondary"):
        if st.session_state.current_page != "Create Quest":
            st.session_state.current_page = "Create Quest"
            st.session_state.viewing_user_schedule = None
            st.session_state.editing_event = None
            st.session_state.last_user_click = None
            st.rerun()

    # Inbox with unread count and fire emoji if active
    unread_count = get_unread_count(st.session_state.current_user["email"])
    if st.session_state.current_page == "Inbox":
        inbox_label = f"📨 Inbox ({unread_count}) 🔥" if unread_count > 0 else "📨 Inbox 🔥"
    else:
        inbox_label = f"📨 Inbox ({unread_count})" if unread_count > 0 else "📨 Inbox"
    
    if st.sidebar.button(inbox_label, use_container_width=True, key="nav_inbox",
            type="primary" if st.session_state.current_page == "Inbox" else "secondary"):
        if st.session_state.current_page != "Inbox":
            st.session_state.current_page = "Inbox"
            st.session_state.viewing_user_schedule = None
            st.session_state.editing_event = None
            st.session_state.last_user_click = None
            st.rerun()

    user_avatar = st.session_state.current_user.get('avatar', '🧙‍♂️')
    profile_label = f"{user_avatar} Profile 🔥" if st.session_state.current_page == "Profile" else f"{user_avatar} Profile"
    if st.sidebar.button(profile_label, use_container_width=True, key="nav_profile",
            type="primary" if st.session_state.current_page == "Profile" else "secondary"):
        st.session_state.current_page = "Profile"
        st.session_state.viewing_user_schedule = None
        st.session_state.editing_event = None
        st.session_state.last_user_click = None
        st.rerun()

    # Print Schedule button
    if st.sidebar.button("🖨️ Print Schedule", use_container_width=True, key="print_schedule_sidebar",
                help="Open clean print view"):
        print_html = generate_clean_print_html(st.session_state.current_user["email"])
        st.components.v1.html(print_html, height=0, scrolling=False)
    
    st.sidebar.markdown("---")

# Show registered users with avatars (clickable) - only when logged in
if st.session_state.users and st.session_state.current_user:
    st.sidebar.write("**Registered Adventurers:**")
    current_user_email = st.session_state.current_user.get('email') if st.session_state.current_user else None
    
    for email, user_info in st.session_state.users.items():
        # Skip the current user - they shouldn't see themselves in the list
        if email == current_user_email:
            continue
            
        avatar = user_info.get('avatar', '🧙‍♂️')
        pronouns = user_info.get('pronouns', 'they/them')
        avatar_name = AVATAR_OPTIONS.get(avatar, 'Unknown')
        
        # Create clickable user entry
        if st.sidebar.button(f"{avatar} {user_info['display_name']} _{pronouns}_", 
                           key=f"user_{email}",
                           help=f"Click to view {user_info['display_name']}'s schedule"):
            # Only set if different from current value to prevent infinite loops
            current_viewing = st.session_state.get('viewing_user_schedule')
            if current_viewing != email:
                print(f"sidebar: viewing_user_schedule set to {email}")
                st.session_state.viewing_user_schedule = email
                # Clear any existing click tracking
                if 'last_user_click' in st.session_state:
                    del st.session_state.last_user_click
                st.rerun()

# Only show content if user is logged in
if st.session_state.current_user is None:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #FFF3CD 0%, #F8D7DA 100%); 
                border: 2px solid #8B4513; border-radius: 10px; padding: 15px; 
                text-align: center; margin: 20px 0;">
        <h3 style="color: #8B4513; font-family: 'Cinzel', serif; font-weight: bold; margin: 0;
                   animation: screamPulse 2s ease-in-out infinite;">
            🚪 Please scream into the void to join the festivities!
        </h3>
    </div>
    
    <style>
    @keyframes screamPulse {
        0% { 
            transform: scale(1);
            text-shadow: 2px 2px 4px rgba(139, 69, 19, 0.3);
        }
        50% { 
            transform: scale(1.05);
            text-shadow: 2px 2px 8px rgba(139, 69, 19, 0.6), 0 0 15px rgba(139, 69, 19, 0.4);
        }
        100% { 
            transform: scale(1);
            text-shadow: 2px 2px 4px rgba(139, 69, 19, 0.3);
        }
    }
    </style>
    """, unsafe_allow_html=True)
    st.stop()

# Navigation moved to sidebar

# Tavern chat helper function
def render_tavern_chat_at_bottom():
    """Render the tavern chat component at the bottom of the page"""
    try:
        from working_chat import render_working_chat
        st.markdown("---")  # Add separator
        user_email = st.session_state.get('current_user', {}).get('email')
        user_display_name = st.session_state.get('current_user', {}).get('display_name')
        user_avatar = st.session_state.get('current_user', {}).get('avatar', '🧙‍♂️')
        user_class = AVATAR_OPTIONS.get(user_avatar, 'Adventurer')
        render_working_chat(user_email, user_display_name, user_avatar, user_class)
    except Exception as e:
        print(f"Error loading chat component: {e}")

# Show user schedule if viewing someone's profile
if st.session_state.viewing_user_schedule:
    viewed_email = st.session_state.viewing_user_schedule
    if viewed_email in st.session_state.users:
        viewed_user = st.session_state.users[viewed_email]
        
        # User Profile section
        pronouns = viewed_user.get('pronouns', 'they/them')
        st.header(f"{viewed_user['avatar']} {viewed_user['display_name']} - {pronouns}")
        
        # Bio section for viewed user
        if viewed_user.get('bio', '').strip():
            st.markdown("---")
            st.markdown("### 📜 About Me")
            st.markdown(f"*{viewed_user['bio']}*")
        
        st.markdown("---")
        st.markdown('<div class="fantasy-day-header">📅 Their Schedule 📅</div>', unsafe_allow_html=True)
        
        # Close button
        if st.button("← Back to Calendar"):
            if st.session_state.viewing_user_schedule is not None:
                st.session_state.viewing_user_schedule = None
                st.rerun()
        
        # Find user's events (prefer Supabase-backed RSVPs)
        user_events = get_user_rsvps(viewed_email)
        
        if user_events and len(user_events) > 0:
            for event in sorted(user_events, key=lambda e: (e.get("date", e.get("day", "")), e.get("time", e.get("start", "")))):
                # Handle both database field names (date, time, title) and local field names (day, start, name)
                event_date = event.get("date", event.get("day", ""))
                event_time = event.get("time", event.get("start", ""))
                event_name = event.get("title", event.get("name", "Untitled Event"))
                event_description = event.get("description", "")
                event_host = event.get("host", event.get("host_email", "Unknown"))
                
                # Get day name from date
                day_name = event_date
                if event_date in [day[0] for day in DAYS]:
                    day_name = next(day[1] for day in DAYS if day[0] == event_date)
                
                tag_icon = get_first_tag_icon(event)
                
                # Check if event is past (simplified check)
                is_past = False  # For now, skip past event checking to avoid errors
                strikethrough_style = "text-decoration: line-through; opacity: 0.7;" if is_past else ""
                past_indicator = " [COMPLETED]" if is_past else ""
                
                with st.container():
                    st.markdown(f"""
                    <div style="border: 2px solid #7B2CBF; border-radius: 10px; 
                               padding: 12px; margin: 8px 0; background: #F8F4FF; {strikethrough_style}">
                        <div style="font-weight: bold; color: #7B2CBF; margin-bottom: 5px; {strikethrough_style}">
                            {tag_icon} {event_name}{past_indicator}
                        </div>
                        <div style="color: #333; margin-bottom: 8px; font-size: 14px; {strikethrough_style}">
                            📅 {day_name} at {event_time} | Host: {event_host}
                        </div>
                        <div style="color: #666; font-size: 12px; {strikethrough_style}">
                            💻 System: {event.get('game_system', 'Not specified')}
                        </div>
                        <div style="color: #666; font-size: 12px; font-style: italic; margin-top: 8px; {strikethrough_style}">
                            📖 {event_description}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="border: 2px solid #8B4513; border-radius: 10px; 
                       padding: 20px; margin: 20px 0; background: linear-gradient(135deg, #F4E4BC, #E6D3A3); 
                       text-align: center;">
                <div style="font-size: 48px; margin-bottom: 15px;">🗓️</div>
                <div style="font-size: 24px; font-weight: bold; color: #8B4513; margin-bottom: 10px; font-family: 'Cinzel', serif;">
                    No Quests Yet
                </div>
                <div style="font-size: 16px; color: #654321; font-family: 'Cinzel', serif;">
                    {viewed_user['display_name']} hasn't joined any quests yet.
                </div>
                <div style="font-size: 14px; color: #8B7355; margin-top: 10px; font-style: italic;">
                    They might be planning their next adventure!
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.stop()

# Inbox Page
if st.session_state.current_page == "Inbox":
    st.markdown("""
    <div style="background: linear-gradient(135deg, #8B4513 0%, #A0522D 25%, #CD853F 50%, #A0522D 75%, #8B4513 100%);
                border: 3px solid #654321;
                border-radius: 15px;
                padding: 20px;
                margin: 20px 0;
                box-shadow: 
                    0 4px 8px rgba(0,0,0,0.3),
                    inset 0 1px 3px rgba(255,255,255,0.2),
                    inset 0 -1px 3px rgba(0,0,0,0.3);
                text-align: center;">
        <h1 style="color: #FFFACD; font-family: 'Uncial Antiqua', 'Cinzel', serif; 
                   font-weight: bold; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.8);">
            📨 Adventurer's Inbox
        </h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Messaging tabs
    tab_names = ["📥 Inbox", "📤 Sent"]
    
    # Create tabs
    tabs = st.tabs(tab_names)
    
    with tabs[0]:  # Received Messages
        messages = get_user_messages(st.session_state.current_user["email"])
        
        # Debug: Show what we got (commented out to reduce spam)
        # st.write(f"Debug: Retrieved {len(messages)} messages")
        # if messages:
        #     st.write(f"First message keys: {list(messages[0].keys())}")
        
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
                                {message.get('from_avatar', '🧙‍♂️')} From: {message.get('from_name', 'Unknown')}
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
                            tag_icon = get_first_tag_icon(event)
                            
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
                                    current_reply = st.session_state.get('inline_reply_to')
                                    new_reply = None if current_reply == message["id"] else message["id"]
                                    
                                    # Only update and rerun if state actually changes
                                    if current_reply != new_reply:
                                        st.session_state.inline_reply_to = new_reply
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
                                # Set the recipient for the reply and go to send message
                                current_replying = st.session_state.get('replying_to')
                                new_replying = {
                                    'email': message['from_email'],
                                    'name': message['from_name'],
                                    'avatar': message['from_avatar'],
                                    'original_message': message['message'],
                                    'original_subject': message.get('subject', '')
                                }
                                
                                # Only update and rerun if state actually changes
                                if current_replying != new_replying:
                                    st.session_state.replying_to = new_replying
                                    st.session_state.current_page = "Inbox"  # Stay on inbox but show send form
                                    st.session_state.active_inbox_tab = "✉️ Send Message"  # Switch to send message tab
                                st.rerun()
                        with col_delete:
                            if st.button("🗑️", key=f"delete_msg_{message['id']}", 
                                       help="Delete message"):
                                delete_message(st.session_state.current_user["email"], message["id"])
                                # Use a flag to prevent multiple rapid clicks
                                if 'last_deleted_message' not in st.session_state or st.session_state.last_deleted_message != message['id']:
                                    st.session_state.last_deleted_message = message['id']
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
                    
                    # Inline reply logic removed - now using simple reply approach
        
        # Add divider and send message form
        st.divider()
        st.subheader("✉️ Send Message")
        
        # Show reply context if replying
        if st.session_state.replying_to:
            reply_info = st.session_state.replying_to
            st.markdown(f"""
            <div style="background: #E8F4FD; border: 2px solid #7B2CBF; border-radius: 8px; 
                       padding: 10px; margin-bottom: 15px;">
                <div style="font-weight: bold; color: #7B2CBF;">
                    ↩️ Replying to: {reply_info['name']}
                </div>
                <div style="font-size: 12px; color: #666; font-style: italic; margin-top: 5px;">
                    "{reply_info['original_message'][:100]}{'...' if len(reply_info['original_message']) > 100 else ''}"
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("❌ Cancel Reply"):
                if st.session_state.get('replying_to') is not None:
                    st.session_state.replying_to = None
                    # Don't call st.rerun() - let the form clear naturally
        
        # Send message form
        with st.form("send_message_form", clear_on_submit=True):
            # Get other users for recipient selection
            other_users = {email: user for email, user in st.session_state.users.items() 
                          if email != st.session_state.current_user["email"]}
        
            if not other_users:
                st.warning("No other adventurers registered yet!")
            else:
                # Recipient selection
                if st.session_state.replying_to:
                    recipient_email = st.session_state.replying_to['email']
                    recipient_options = [recipient_email]
                    selected_recipient = recipient_email
                    st.write(f"**Replying to:** {st.session_state.replying_to['avatar']} {st.session_state.replying_to['name']}")
                else:
                    # Recipient selection
                    recipient_options = list(other_users.keys())
                    selected_recipient = st.selectbox(
                        "Send to:",
                        recipient_options,
                        format_func=lambda x: f"{other_users[x]['avatar']} {other_users[x]['display_name']} ({x})"
                    )
                
                # Message content
                if st.session_state.replying_to:
                    # Show original message at the top when replying
                    st.markdown("**Original Message:**")
                    st.markdown(f"*{st.session_state.replying_to['original_message']}*")
                    st.markdown("**Your Reply:**")
                    message_text = st.text_area("Message:", placeholder="Your reply message...", max_chars=500)
                else:
                    placeholder_text = "Greetings, fellow adventurer! Want to join my quest?"
                    message_text = st.text_area("Message:", placeholder=placeholder_text, max_chars=500)
                
                # Send button
                button_text = "↩️ Send Reply" if st.session_state.replying_to else "🦅 Send Message"
                send_button = st.form_submit_button(button_text, type="primary")
                
                if send_button:
                    if not message_text.strip():
                        st.error("Please enter a message!")
                    else:
                        reply_to_id = None  # We'll handle this differently for now
                        
                        message_data = {
                            "id": str(uuid.uuid4()),
                            "sender_email": st.session_state.current_user["email"],
                            "recipient_email": selected_recipient,
                            "subject": f"Re: {st.session_state.replying_to.get('original_subject', 'Message')}" if st.session_state.replying_to else "",
                            "message": message_text.strip()
                        }
                        
                        # Save to database
                        print(f"🔍 DEBUG: About to call save_to_database for private_messages")
                        result = save_to_database("private_messages", message_data)
                        
                        if result:
                            st.success("Message sent! 🎉")
                            # Clear reply state if replying
                            if st.session_state.replying_to:
                                st.session_state.replying_to = None
                            # Don't call st.rerun() - let the form clear naturally with clear_on_submit=True
                        else:
                            st.error("Failed to send message. Please try again.")
    
    with tabs[1]:  # Sent Messages
        sent_messages = get_sent_messages(st.session_state.current_user["email"])
        
        if not sent_messages:
            st.info("You haven't sent any messages yet!")
        else:
            st.write(f"You have sent {len(sent_messages)} message(s)")
            
            # Sort messages by timestamp (newest first)
            sent_messages.sort(key=lambda x: x["timestamp"], reverse=True)
            
            for message in sent_messages:
                # Message container styling
                with st.container():
                    st.markdown(f"""
                    <div style="border: 2px solid #7B2CBF; border-radius: 10px; padding: 15px; 
                               margin: 10px 0; background: linear-gradient(135deg, #F8F4FF 0%, #EDE4FF 100%);">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                            <div style="font-weight: bold; color: #7B2CBF;">
                                {message.get('to_avatar', '🧙‍♂️')} To: {message.get('to_name', 'Unknown')}
                            </div>
                            <div style="font-size: 12px; color: #666;">
                                {message['timestamp']}
                            </div>
                        </div>
                        <div style="color: #333;">
                            {message['message']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
    st.stop()

# Tavern Page - Removed (chat is now in sidebar)
if False:  # Disabled - chat moved to sidebar
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
        with st.form("tavern_full_chat_form", clear_on_submit=True):
            new_message = st.text_area("Your message:", 
                                     placeholder="Rase yer flagon ya cretin!", 
                                     max_chars=300, 
                                     height=120)
            
            send_message_btn = st.form_submit_button("🦅 Send Message", use_container_width=True)
            
            if send_message_btn:
                if new_message.strip():
                    send_tavern_message(st.session_state.current_user["email"], new_message.strip())
                    st.success("Message sent to the tavern! 🍺")
                    # Avoid forced rerun; form will clear due to clear_on_submit=True
                else:
                    st.error("Please enter a message!")

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
    
    # JavaScript to automatically switch to send message tab when replying
    if st.session_state.get('replying_to'):
        st.markdown("""
        <script>
        // Wait for the page to load, then switch to the send message tab
        setTimeout(function() {
            // Find the send message tab and click it
            const tabs = document.querySelectorAll('[data-testid="stTabs"] button');
            for (let tab of tabs) {
                if (tab.textContent.includes('Send Message')) {
                    tab.click();
                    break;
                }
            }
        }, 100);
        </script>
        """, unsafe_allow_html=True)
    
    # Tavern chat at bottom of Inbox page
    render_tavern_chat_at_bottom()
    
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
            st.markdown("""
            <div style="background: linear-gradient(135deg, #8B4513 0%, #A0522D 25%, #CD853F 50%, #A0522D 75%, #8B4513 100%);
                        border: 3px solid #654321;
                        border-radius: 15px;
                        padding: 20px;
                        margin: 20px 0;
                        box-shadow: 
                            0 4px 8px rgba(0,0,0,0.3),
                            inset 0 1px 3px rgba(255,255,255,0.2),
                            inset 0 -1px 3px rgba(0,0,0,0.3);
                        text-align: center;">
                <h1 style="color: #FFFACD; font-family: 'Uncial Antiqua', 'Cinzel', serif; 
                           font-weight: bold; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.8);">
                    ✏️ Edit Quest
                </h1>
            </div>
            """, unsafe_allow_html=True)
            
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
    
    # Profile header with fantasy styling
    pronouns = user.get('pronouns', 'they/them')
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #8B4513 0%, #A0522D 25%, #CD853F 50%, #A0522D 75%, #8B4513 100%);
                border: 3px solid #654321;
                border-radius: 15px;
                padding: 20px;
                margin: 20px 0;
                box-shadow: 
                    0 4px 8px rgba(0,0,0,0.3),
                    inset 0 1px 3px rgba(255,255,255,0.2),
                    inset 0 -1px 3px rgba(0,0,0,0.3);
                text-align: center;">
        <h1 style="color: #FFFACD; font-family: 'Uncial Antiqua', 'Cinzel', serif; 
                   font-weight: bold; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.8);">
            {user['avatar']} {user['display_name']} - {pronouns}
        </h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Bio section
    if user.get('bio', '').strip():
        st.markdown("---")
        st.markdown("### 📜 About Me")
        st.markdown(f"*{user['bio']}*")
    
    col1, col2 = st.columns([6, 1])
    
    with col1:
        st.markdown('<div class="fantasy-day-header">📅 Your Schedule 📅</div>', unsafe_allow_html=True)
        
        # Check for overlapping events and show warning
        user_events = []
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
        
        # Check for overlapping events
        overlapping_events = []
        if all_user_events:
            for i, event1 in enumerate(all_user_events):
                for j, event2 in enumerate(all_user_events):
                    if i < j and event1.get("day") == event2.get("day"):
                        # Parse times
                        try:
                            start1 = datetime.strptime(event1.get("start", "12:00 AM"), "%I:%M %p")
                            end1_str = event1.get("end", event1.get("end_time", "12:00 AM"))
                            if end1_str == event1.get("start", "12:00 AM"):
                                end1 = start1.replace(hour=(start1.hour + 2) % 24)
                            else:
                                end1 = datetime.strptime(end1_str, "%I:%M %p")
                            
                            start2 = datetime.strptime(event2.get("start", "12:00 AM"), "%I:%M %p")
                            end2_str = event2.get("end", event2.get("end_time", "12:00 AM"))
                            if end2_str == event2.get("start", "12:00 AM"):
                                end2 = start2.replace(hour=(start2.hour + 2) % 24)
                            else:
                                end2 = datetime.strptime(end2_str, "%I:%M %p")
                            
                            # Check for overlap
                            if (start1 < end2 and start2 < end1):
                                overlapping_events.append((event1, event2))
                        except:
                            pass
        
        # Show overlap warning if found
        if overlapping_events:
            st.warning("⚠️ **Warning: You have overlapping events!** Some of your scheduled events conflict with each other.")
        
        if all_user_events:
            current_day = None
            for event in sorted(all_user_events, key=lambda e: (e["day"], e["start"])):
                day_name = next(day[1] for day in DAYS if day[0] == event["day"])
                # Parse tags and get first tag's icon
                tags = event.get("tags", "")
                try:
                    parsed_tags = json.loads(tags) if tags and tags.strip() else []
                    first_tag = parsed_tags[0] if parsed_tags else ""
                    tag_icon = TAGS.get(first_tag, "📝")
                except (json.JSONDecodeError, TypeError, IndexError):
                    tag_icon = "📝"
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
                                👥 Party: {len(event.get('rsvps', []))}/{event.get('seat_min', 1)}-{event.get('seat_max', event.get('seat_min', 1))}
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
                                👥 Party: {len(event.get('rsvps', []))}/{event.get('seat_min', 1)}-{event.get('seat_max', event.get('seat_min', 1))}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_buttons:
                        # Add CSS to properly center the abandon button container
                        st.markdown(f"""
                        <style>
                        /* Target the specific column containing the abandon button for proper centering */
                        div[data-testid="column"]:nth-child(2) {{
                            display: flex !important;
                            flex-direction: column !important;
                            justify-content: center !important;
                            align-items: center !important;
                            height: 150px !important; /* Match approximate height of white container */
                            padding: 15px 10px !important;
                        }}
                        </style>
                        """, unsafe_allow_html=True)
                        
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
    
    # Tavern chat at bottom of Profile page
    render_tavern_chat_at_bottom()
    
    st.stop()

# Create Quest Page
if st.session_state.current_page == "Create Quest":
    # Use form_submitted flag to generate a unique key to clear the form
    form_key = f"event_form_{st.session_state.form_submitted}"
    
    # Reset form submitted flag after using it for the key
    if st.session_state.form_submitted:
        st.session_state.form_submitted = False

    # Add CSS for silver form background on Create Quest page
    st.markdown("""
    <style>
    /* Silver background for event form on Create Quest page */
    .main .block-container .stForm {
        background: linear-gradient(135deg, #C0C0C0 0%, #E8E8E8 25%, #D3D3D3 50%, #E8E8E8 75%, #C0C0C0 100%) !important;
        border: 3px solid #A9A9A9 !important;
        border-radius: 15px !important;
        padding: 25px !important;
        box-shadow: 
            0 4px 8px rgba(0,0,0,0.3),
            inset 0 1px 3px rgba(255,255,255,0.5),
            inset 0 -1px 3px rgba(0,0,0,0.2) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create Quest form in a brown container
    st.markdown("""
    <div style="background: linear-gradient(135deg, #8B4513 0%, #A0522D 25%, #CD853F 50%, #A0522D 75%, #8B4513 100%);
                border: 3px solid #654321;
                border-radius: 15px;
                padding: 25px;
                margin: 20px 0;
                box-shadow: 
                    0 4px 8px rgba(0,0,0,0.3),
                    inset 0 1px 3px rgba(255,255,255,0.2),
                    inset 0 -1px 3px rgba(0,0,0,0.3);">
        <h3 style="color: #FFFACD; font-family: 'Uncial Antiqua', 'Cinzel', serif; 
                   font-weight: bold; margin-bottom: 15px; text-align: center;
                   text-shadow: 2px 2px 4px rgba(0,0,0,0.8);">
            ⚔️ Create a New Quest ⚔️
        </h3>
        <p style="color: #FFFACD; font-family: 'Cinzel', serif; 
                  font-style: italic; text-align: center; margin-bottom: 20px;
                  text-shadow: 2px 2px 4px rgba(0,0,0,0.8);">
            "Forge your adventure and rally fellow adventurers!"
        </p>
    """, unsafe_allow_html=True)

    with st.form(form_key):
            event_name = st.text_input("Quest Name:", placeholder="e.g., Dragons & Dungeons Adventure")
            # Make Quest Host/GM read-only and auto-filled
            event_host = st.text_input("Quest Host/GM:", value=st.session_state.current_user['display_name'], disabled=True)
            day = st.selectbox("Select Day", DAYS, format_func=lambda x: x[1])
            start_time = st.selectbox("Start Time", TIME_SLOTS)
            end_time = st.selectbox("End Time", TIME_SLOTS, index=min(len(TIME_SLOTS)-1, 2))
            tag = st.selectbox("Event Tag", list(TAGS.keys()))
            game_system = st.text_input("Game System:", placeholder="e.g., D&D 5e, Pathfinder, etc.")
            
            # Participation option - changed to dropdown for better styling
            participation = st.selectbox(
                "Are You Just Hosting This Event or Are You In the Headcount?",
                ["I'm just hosting", "I'm participating and part of the headcount"],
                help="Choose whether you count toward the minimum/maximum seats"
            )
            
            seat_min = st.number_input("Minimum Seats", min_value=1, max_value=100, value=2)
            seat_max = st.number_input("Maximum Seats", min_value=seat_min, max_value=100, value=6)
            description = st.text_area("Quest Description (include what is happening and any materials needed)", max_chars=300)
            
            # Center the Create Quest button
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                submit = st.form_submit_button("Create Quest", use_container_width=True)
    
    # Close the brown container div
    st.markdown("</div>", unsafe_allow_html=True)

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
                "tags": tag,
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
            print(f"🔍 DEBUG: About to call save_to_database for events")
            save_to_database("events", {
                "id": new_event["id"],
                "title": new_event["name"],  # Map "name" to "title"
                "description": new_event["description"],
                "date": new_event["day"],    # Map "day" to "date"
                "time": new_event["start"],  # Map "start" to "time"
                "end_time": new_event["end"], # Add end time
                "location": new_event.get("location", ""),
                "host_email": new_event["creator_email"],
                "tags": new_event.get("tags", ""),
                "game_system": new_event.get("game_system", "Not specified"),
                "seat_min": new_event.get("seat_min", 1),
                "seat_max": new_event.get("seat_max", 1),
                # Backwards-compatible max_attendees field (Supabase expects this)
                "max_attendees": new_event.get("seat_max", new_event.get("max_attendees", 50))
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
            
            # Create a popup-style message with close button using session state
            if st.session_state.get('show_success_popup', True):
                st.markdown("""
                    <div style="background: linear-gradient(135deg, #2ECC71, #27AE60); color: white; 
                   padding: 20px 30px; border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.3);
                   text-align: center; font-size: 18px; font-weight: bold; z-index: 9999;
                               border: 3px solid #FFD700; margin: 20px 0;">
            🎉 Quest Created Successfully! 🎯<br/>
            <span style="font-size: 14px; font-weight: normal;">Your epic adventure awaits!</span>
        </div>
        """, unsafe_allow_html=True)
                
                # Center the close button
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    if st.button("✨ Close ✨", key="close_success_popup", use_container_width=True):
                        st.session_state.show_success_popup = False
                        st.rerun()
            
            # Set flag to clear form on next render and show success popup
            st.session_state.form_submitted = True
            st.session_state.show_success_popup = True
            
            # Auto-clear the popup on next render; avoid blocking sleep and forced rerun
            # The UI will update naturally on user interaction or manual refresh

    # Tavern chat at bottom of Create Quest page
    render_tavern_chat_at_bottom()

    st.stop()

# Quest Counter Page  
if st.session_state.current_page == "Quest Counter":
    st.markdown("""
    <div style="background: linear-gradient(135deg, #8B4513 0%, #A0522D 25%, #CD853F 50%, #A0522D 75%, #8B4513 100%);
                border: 3px solid #654321;
                border-radius: 15px;
                padding: 20px;
                margin: 20px 0;
                box-shadow: 
                    0 4px 8px rgba(0,0,0,0.3),
                    inset 0 1px 3px rgba(255,255,255,0.2),
                    inset 0 -1px 3px rgba(0,0,0,0.3);
                text-align: center;">
        <h1 style="color: #FFFACD; font-family: 'Uncial Antiqua', 'Cinzel', serif; 
                   font-weight: bold; margin: 0 0 10px 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.8);">
            🗓️ Quest Counter 🗓️
        </h1>
        <p style="color: #FFFACD; font-family: 'Cinzel', serif; 
                  font-style: italic; margin: 0; text-shadow: 1px 1px 2px rgba(0,0,0,0.8);">
            "Browse all available quests and join adventures!"
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Add live RSVP update script
    st.markdown("""
    <script>
    // Live RSVP updates using Supabase REST API
    let lastRsvpCheck = Date.now();
    let rsvpRefreshInterval;
    
    // Supabase configuration
    const SUPABASE_URL = 'https://uvsdbuonyfzajhtrgnxq.supabase.co';
    const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV2c2RidW9ueWZ6YWpodHJnbnhxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEwNjUxNjgsImV4cCI6MjA3NjY0MTE2OH0.tq_dQfCIl68bSt2BUPP0lWW2DjjwPpxcKV6LIt2LRFg';
    
    function checkForRsvpUpdates() {
        const now = Date.now();
        if (now - lastRsvpCheck > 5000) { // Check every 5 seconds
            lastRsvpCheck = now;
            
            // Get current RSVP data
            const currentRsvps = {};
            document.querySelectorAll('[data-event-id]').forEach(element => {
                const eventId = element.getAttribute('data-event-id');
                const rsvpCount = element.querySelector('.rsvp-count');
                const adventurerList = element.querySelector('.adventurer-list');
                const statusElement = element.querySelector('.quest-status');
                if (rsvpCount && adventurerList) {
                    currentRsvps[eventId] = {
                        count: rsvpCount.textContent,
                        adventurers: adventurerList.textContent,
                        status: statusElement ? statusElement.textContent : ''
                    };
                }
            });
            
            // Fetch latest RSVP data from Supabase
            fetch(`${SUPABASE_URL}/rest/v1/rsvps?select=event_id,user_email,status`, {
                headers: {
                    'apikey': SUPABASE_KEY,
                    'Authorization': `Bearer ${SUPABASE_KEY}`,
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(rsvps => {
                // Group RSVPs by event
                const rsvpsByEvent = {};
                rsvps.forEach(rsvp => {
                    if (rsvp.status === 'yes') {
                        if (!rsvpsByEvent[rsvp.event_id]) {
                            rsvpsByEvent[rsvp.event_id] = [];
                        }
                        rsvpsByEvent[rsvp.event_id].push(rsvp.user_email);
                    }
                });
                
                // Update display for each event
                Object.keys(rsvpsByEvent).forEach(eventId => {
                    const serverCount = rsvpsByEvent[eventId].length;
                    const currentData = currentRsvps[eventId];
                    
                    if (!currentData || currentData.count !== serverCount.toString()) {
                        // Update the display
                        const eventElement = document.querySelector(`[data-event-id="${eventId}"]`);
                        if (eventElement) {
                            const rsvpCount = eventElement.querySelector('.rsvp-count');
                            if (rsvpCount) {
                                rsvpCount.textContent = serverCount;
                                
                                // Add a subtle animation to show update
                                eventElement.style.transition = 'background-color 0.5s ease';
                                eventElement.style.backgroundColor = '#E8F5E8';
                                setTimeout(() => {
                                    eventElement.style.backgroundColor = '';
                                }, 1000);
                            }
                        }
                    }
                });
            })
            .catch(error => console.log('RSVP update check failed:', error));
        }
    }
    
    // Start RSVP refresh interval
    rsvpRefreshInterval = setInterval(checkForRsvpUpdates, 3000);
    
    // Cleanup on page unload
    window.addEventListener('beforeunload', () => {
        if (rsvpRefreshInterval) {
            clearInterval(rsvpRefreshInterval);
        }
    });
    </script>
    """, unsafe_allow_html=True)

    # Available Events Display - with wider container
    st.markdown('<div class="quest-section-wide">', unsafe_allow_html=True)

    for day_key, day_label in DAYS:
        # Fantasy styled day header
        st.markdown(f'<div class="fantasy-day-header">⚔️ {day_label} ⚔️</div>', unsafe_allow_html=True)
        
        # Show ALL events (including user's own) - fetch fresh from Supabase
        fresh_events = get_events_from_supabase()
        day_events = [e for e in fresh_events if e["day"] == day_key]
        if not day_events:
            st.write("_No quests yet for this day._")
        else:
            for event in sorted(day_events, key=lambda e: e["start"]):
                    # Get RSVP info
                    rsvps = event.get("rsvps", [])
                    current_count = len(rsvps)
                    is_user_rsvped = any(rsvp.get("email") == st.session_state.current_user.get("email") for rsvp in rsvps)
                    seat_min_val = event.get("seat_min", 1)
                    seat_max_val = event.get("seat_max", seat_min_val)
                    is_full = current_count >= seat_max_val
                    can_rsvp = not is_user_rsvped and not is_full and current_count < seat_max_val
                    
                    # Status indicators
                    if current_count < seat_min_val:
                        status = "🔴 Needs more adventurers"
                    elif current_count >= seat_min_val and current_count < seat_max_val:
                        status = "🟡 Ready to go (spots available)"
                    else:
                        status = "🟢 Party is full"
                    
                    # Display event
                    # Handle tags - can be a string or array
                    tags_data = event.get("tags", [])
                    if isinstance(tags_data, str):
                        try:
                            tags_data = json.loads(tags_data) if tags_data else []
                        except (json.JSONDecodeError, TypeError):
                            tags_data = [tags_data] if tags_data else []
                    elif not isinstance(tags_data, list):
                        tags_data = []
                    
                    # Get the first tag for display, or use the legacy 'tag' field
                    tag_value = event.get("tag") or (tags_data[0] if tags_data else "")
                    tag_icon = TAGS.get(tag_value, "📝")
                    
                    # Display all tags if there are multiple
                    if len(tags_data) > 1:
                        tag_display = f"Tags: {', '.join(tags_data)}"
                    elif tag_value:
                        tag_display = f"Tag: `{tag_value}`"
                    else:
                        tag_display = "Tag: Not specified"
                    is_host = event.get("creator_email") == st.session_state.current_user.get("email")
                    host_display = f"🎭 Host/GM: {event.get('host', event.get('creator_email','Unknown'))}" \
                                   if not is_host else f"🎭 Host/GM: <mark style='background-color: #FFD700; padding: 2px 4px; border-radius: 3px;'>{event.get('host', event.get('creator_email','Unknown'))} (You)</mark>"

                    # Use .get everywhere to avoid KeyErrors if fields are missing
                    event_name = event.get('name') or event.get('title') or 'Untitled Event'
                    event_start = event.get('start', '')
                    event_end = event.get('end', '')
                    seat_min = event.get('seat_min', 0)
                    seat_max = event.get('seat_max', 0)
                    description = event.get('description', '')

                    # Show RSVPs with avatars for party size
                    if rsvps:
                        rsvp_display = []
                        for rsvp in rsvps:
                            avatar = rsvp.get("avatar", "🧙‍♂️")
                            avatar_name = AVATAR_OPTIONS.get(avatar, "Unknown")
                            avatar_html = f'<span title="{avatar_name}">{avatar}</span>'
                            rsvp_display.append(f"{avatar_html} {rsvp['display_name']}")
                        
                        party_size_display = f"Party Size: <span class='rsvp-count'>{current_count}</span>/{seat_min}-{seat_max} | <span class='quest-status'>{status}</span><br/>Adventurers: <span class='adventurer-list'>{', '.join(rsvp_display)}</span>"
                    else:
                        party_size_display = f"Party Size: <span class='rsvp-count'>{current_count}</span>/{seat_min}-{seat_max} | <span class='quest-status'>{status}</span><br/>Adventurers: <span class='adventurer-list'>None yet</span>"

                    st.markdown(f"""
<div data-event-id="{event['id']}" style="
    background: linear-gradient(135deg, #F4E4BC 0%, #E6D3A3 50%, #D4C4A8 100%);
    border: 3px solid #8B4513;
    border-radius: 15px;
    padding: 20px;
    margin: 15px 0;
    box-shadow: 
        0 4px 8px rgba(0,0,0,0.2),
        inset 0 1px 3px rgba(255,255,255,0.3);
    font-family: 'Cinzel', serif;
">
    <div style="font-size: 1.2em; font-weight: bold; color: #8B4513; margin-bottom: 10px;">
        {tag_icon} {event_name}
    </div>
    <div style="color: #654321; margin-bottom: 8px;">
        {host_display}
    </div>
    <div style="color: #654321; margin-bottom: 8px;">
        🕐 {event_start} - {event_end} | {tag_display}
    </div>
    <div style="color: #654321; margin-bottom: 8px;">
        💻 System: {event.get('game_system', 'Not specified')}
    </div>
    <div style="color: #654321; margin-bottom: 8px;">
        {party_size_display}
    </div>
    <div style="color: #654321; margin-top: 10px; font-style: italic;">
        Description: {description}
    </div>
</div>
""", unsafe_allow_html=True)
                    
                    # Single button below the event container
                    if can_rsvp:
                        # Regular join button
                        join_button = st.button(f"⚔️ Join Quest", key=f"join_{event['id']}", 
                                              help="Click to join this epic adventure!", use_container_width=True)
                        if join_button:
                            rsvp_to_event(event['id'], st.session_state.current_user)
                            st.rerun()
                    elif is_user_rsvped:
                        # Show only "IN PARTY" status without cancel button (moved to Profile page)
                        st.markdown(f"""
                        <div style="text-align: center; padding: 10px; background: linear-gradient(45deg, #28a745, #20c997); 
                                   color: white; border-radius: 5px; font-size: 14px; font-weight: bold;
                                   background-image: 
                                   radial-gradient(circle at 20% 50%, transparent 20%, rgba(40, 167, 69, 0.3) 21%, rgba(40, 167, 69, 0.3) 34%, transparent 35%),
                                   linear-gradient(0deg, rgba(32, 201, 151, 0.8) 50%, rgba(40, 167, 69, 0.8) 50%);
                                   background-size: 15px 15px, 20px 20px;
                                   text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
                               border: 2px solid #1e7e34;">
                                    🗡️ IN PARTY 🛡️
                            </div>
                            """, unsafe_allow_html=True)
                    elif is_full:
                        st.markdown("""
                        <div style="text-align: center; padding: 10px; background-color: #6c757d; 
                           color: white; border-radius: 5px; font-weight: bold;">
                            🚫 PARTY FULL 🚫
                        </div>
                        """, unsafe_allow_html=True)
                
                    st.divider()
    
        # Close the wide container
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Tavern chat at bottom of Quest Counter page
    render_tavern_chat_at_bottom()
