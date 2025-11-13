#!/usr/bin/env python3
"""
Test script to verify tavern messages are using display_name column correctly
"""

import requests
import json

# Supabase configuration
SUPABASE_URL = "https://uvsdbuonyfzajhtrgnxq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV2c2RidW9ueWZ6YWpodHJnbnhxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEwNjUxNjgsImV4cCI6MjA3NjY0MTE2OH0.tq_dQfCIl68bSt2BUPP0lWW2DjjwPpxcKV6LIt2LRFg"

def test_tavern_messages():
    """Test that tavern messages show display names correctly"""
    
    print("🍺 Testing Tavern Messages Display Names")
    print("=" * 50)
    
    # Disable SSL warnings
    requests.packages.urllib3.disable_warnings()
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Get tavern messages
    url = f"{SUPABASE_URL}/rest/v1/tavern_messages?select=*&order=created_at.desc"
    response = requests.get(url, headers=headers, verify=False)
    
    if response.status_code == 200:
        messages = response.json()
        print(f"📊 Found {len(messages)} tavern messages")
        print()
        
        for i, msg in enumerate(messages[:5], 1):  # Show top 5 messages
            user_email = msg.get('user_email')
            display_name = msg.get('display_name')
            message_text = msg.get('message', '')
            created_at = msg.get('created_at', '')
            
            print(f"{i}. Message from: {display_name} ({user_email})")
            print(f"   Text: {message_text[:50]}{'...' if len(message_text) > 50 else ''}")
            print(f"   Time: {created_at}")
            
            # Check if display_name is populated
            if display_name:
                print(f"   ✅ Display name: '{display_name}'")
            else:
                print(f"   ❌ Missing display name!")
            print()
        
        # Summary
        messages_with_names = [m for m in messages if m.get('display_name')]
        messages_without_names = [m for m in messages if not m.get('display_name')]
        
        print("📈 Summary:")
        print(f"   Messages with display names: {len(messages_with_names)}")
        print(f"   Messages without display names: {len(messages_without_names)}")
        
        if len(messages_without_names) == 0:
            print("   🎉 All messages have display names!")
        else:
            print("   ⚠️  Some messages are missing display names")
            
    else:
        print(f"❌ Error fetching messages: {response.status_code}")
        print(f"Response: {response.text}")

def test_users_lookup():
    """Test that we can still get user info for avatars/classes"""
    
    print("\n👥 Testing User Lookup for Avatars")
    print("=" * 50)
    
    # Disable SSL warnings
    requests.packages.urllib3.disable_warnings()
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Get users
    url = f"{SUPABASE_URL}/rest/v1/users?select=email,display_name,avatar"
    response = requests.get(url, headers=headers, verify=False)
    
    if response.status_code == 200:
        users = response.json()
        print(f"👥 Found {len(users)} users")
        
        for user in users[:5]:  # Show top 5 users
            email = user.get('email')
            display_name = user.get('display_name')
            avatar = user.get('avatar')
            
            print(f"• {display_name} ({email}) - {avatar}")
            
    else:
        print(f"❌ Error fetching users: {response.status_code}")

if __name__ == "__main__":
    test_tavern_messages()
    test_users_lookup()