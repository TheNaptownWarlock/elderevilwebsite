#!/usr/bin/env python3
"""
Add some sample messages to the tavern to test the chat functionality
"""

import requests
import json
from datetime import datetime
import uuid

# Supabase configuration
SUPABASE_URL = "https://uvsdbuonyfzajhtrgnxq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV2c2RidW9ueWZ6YWpodHJnbnhxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEwNjUxNjgsImV4cCI6MjA3NjY0MTE2OH0.tq_dQfCIl68bSt2BUPP0lWW2DjjwPpxcKV6LIt2LRFg"

headers = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json'
}

sample_messages = [
    {
        "id": str(uuid.uuid4()),
        "user_email": "test1@example.com",
        "message": "Welcome back to the tavern! 🍺",
    },
    {
        "id": str(uuid.uuid4()),
        "user_email": "test2@example.com", 
        "message": "Anyone up for a quest tonight? ⚔️",
    },
    {
        "id": str(uuid.uuid4()),
        "user_email": "test3@example.com",
        "message": "The dragon has been slain! Drinks are on me! 🐉🍻",
    }
]

def add_sample_messages():
    """Add sample messages to tavern_messages table"""
    print("🍺 Adding sample tavern messages...")
    
    for i, message in enumerate(sample_messages):
        try:
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/tavern_messages",
                headers=headers,
                json=message,
                verify=False
            )
            
            if response.status_code in [200, 201]:
                print(f"✅ Added message {i+1}: '{message['message']}'")
            else:
                print(f"❌ Failed to add message {i+1}: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Exception adding message {i+1}: {e}")

def view_all_messages():
    """View all messages in tavern_messages table"""
    print("\n📋 Current tavern messages:")
    
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/tavern_messages?select=*&order=created_at.asc",
            headers=headers,
            verify=False
        )
        
        if response.status_code == 200:
            messages = response.json()
            print(f"Found {len(messages)} messages:")
            
            for i, msg in enumerate(messages):
                timestamp = msg.get('created_at', 'Unknown time')
                user = msg.get('user_email', 'Unknown user')
                message_text = msg.get('message', '')
                print(f"  {i+1}. [{timestamp}] {user}: {message_text}")
        else:
            print(f"❌ Failed to load messages: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception loading messages: {e}")

if __name__ == "__main__":
    print("🍺 Tavern Chat Sample Messages Tool")
    print("=" * 50)
    
    # Show current messages
    view_all_messages()
    
    # Add sample messages
    add_sample_messages()
    
    # Show updated messages
    view_all_messages()
    
    print("\n✅ Done! Your tavern should now have some sample messages to test with.")