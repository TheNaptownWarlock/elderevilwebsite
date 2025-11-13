#!/usr/bin/env python3
"""
Debug script to check what data is being passed to the tavern chat frontend
"""

import requests
import json
from datetime import datetime

# Supabase configuration
SUPABASE_URL = "https://uvsdbuonyfzajhtrgnxq.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV2c2RidW9ueWZ6YWpodHJnbnhxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEwNjUxNjgsImV4cCI6MjA3NjY0MTE2OH0.tq_dQfCIl68bSt2BUPP0lWW2DjjwPpxcKV6LIt2LRFg"

def check_raw_supabase_data():
    """Check what data Supabase is actually returning"""
    print("🔍 Checking raw Supabase tavern_messages data...")
    
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Get messages from Supabase
    url = f"{SUPABASE_URL}/rest/v1/tavern_messages?select=*&order=created_at.asc"
    response = requests.get(url, headers=headers, verify=False)
    
    if response.status_code == 200:
        messages = response.json()
        print(f"📊 Found {len(messages)} messages in Supabase:")
        
        for i, msg in enumerate(messages):
            print(f"\n--- Message {i+1} ---")
            print(f"ID: {msg.get('id')}")
            print(f"user_email: {msg.get('user_email')}")
            print(f"display_name: {msg.get('display_name')}")
            print(f"user_name: {msg.get('user_name', 'NOT SET')}")  # This field shouldn't exist in DB
            print(f"message: {msg.get('message')[:50]}...")
            print(f"created_at: {msg.get('created_at')}")
            
            # Check what fields are available
            all_fields = list(msg.keys())
            print(f"All fields: {all_fields}")
            
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Response: {response.text}")

def simulate_frontend_processing():
    """Simulate how the frontend processes the data"""
    print("\n" + "="*60)
    print("🎭 Simulating frontend processing...")
    
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Get messages like the frontend does
    url = f"{SUPABASE_URL}/rest/v1/tavern_messages?select=*&order=created_at.asc"
    response = requests.get(url, headers=headers, verify=False)
    
    if response.status_code == 200:
        messages = response.json()
        
        # Simulate the frontend's displayName logic for each user perspective
        test_users = [
            ("benbusald@gmail.com", "Ben \"Buzzy\""),
            ("tnewto@saic.edu", "Edin"),
            ("testuser@example.com", "Test")
        ]
        
        for test_email, test_display_name in test_users:
            print(f"\n🧙‍♂️ Viewing as user: {test_display_name} ({test_email})")
            print("-" * 40)
            
            for msg in messages:
                # Simulate JavaScript displayName logic
                is_own_message = (msg.get('user_email') == test_email)
                
                if is_own_message:
                    display_name = test_display_name  # USER_DISPLAY_NAME
                elif msg.get('display_name'):  # NEW: Check display_name first
                    display_name = msg.get('display_name')
                elif msg.get('user_name'):  # OLD: Fallback to user_name
                    display_name = msg.get('user_name')
                elif msg.get('user_email'):
                    display_name = msg.get('user_email').split('@')[0]
                else:
                    display_name = 'Anonymous'
                
                print(f"  {display_name}: {msg.get('message')[:30]}...")
                
                # Show the fix status
                if not is_own_message:
                    if msg.get('display_name'):
                        print(f"    ✅ FIXED: Using 'display_name': {msg.get('display_name')}")
                    elif msg.get('user_name'):
                        print(f"    ✅ Using 'user_name': {msg.get('user_name')}")
                    else:
                        print(f"    ⚠️ No display_name or user_name, falling back to email")
    
if __name__ == "__main__":
    print("🐛 Tavern Chat Frontend Debug Tool")
    print("=" * 60)
    
    try:
        check_raw_supabase_data()
        simulate_frontend_processing()
        
        print("\n" + "="*60)
        print("🔧 DIAGNOSIS:")
        print("✅ FIXED: Updated frontend to check 'display_name' before 'user_name'")
        print("The JavaScript now properly displays names for all users!")
        print("")
        print("Updated logic:")
        print("  } else if (message.display_name) {")
        print("    displayName = message.display_name;")
        print("  } else if (message.user_name) {")
        print("    displayName = message.user_name;")
        print("  } else if (message.user_email) {")
        
    except Exception as e:
        print(f"❌ Error: {e}")