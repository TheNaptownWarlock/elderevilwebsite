#!/usr/bin/env python3
"""
Test script to send a tavern message and verify display_name is saved
"""

import sys
import requests
import json
import uuid
from datetime import datetime

# Supabase configuration
SUPABASE_URL = "https://uvsdbuonyfzajhtrgnxq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV2c2RidW9ueWZ6YWpodHJnbnhxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEwNjUxNjgsImV4cCI6MjA3NjY0MTE2OH0.tq_dQfCIl68bSt2BUPP0lWW2DjjwPpxcKV6LIt2LRFg"

def test_send_message_with_display_name():
    """Test sending a new message with display_name"""
    
    print("🧪 Testing new message with display_name")
    print("=" * 50)
    
    # Disable SSL warnings
    requests.packages.urllib3.disable_warnings()
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }
    
    # First, get Ben's user info
    users_url = f"{SUPABASE_URL}/rest/v1/users?email=eq.benbusald@gmail.com"
    users_response = requests.get(users_url, headers=headers, verify=False)
    
    if users_response.status_code == 200:
        users = users_response.json()
        if users:
            user = users[0]
            user_email = user.get('email')
            display_name = user.get('display_name')
            print(f"📋 User found: {display_name} ({user_email})")
            
            # Send a test message with display_name
            message_data = {
                "id": str(uuid.uuid4()),
                "user_email": user_email,
                "message": "Test message from script with display_name!",
                "display_name": display_name
            }
            
            print(f"📤 Sending message: {message_data}")
            
            url = f"{SUPABASE_URL}/rest/v1/tavern_messages"
            response = requests.post(url, headers=headers, json=message_data, verify=False)
            
            if response.status_code in [200, 201]:
                print("✅ Message sent successfully!")
                print(f"Response: {response.text}")
                
                # Verify it was saved correctly
                print("\n🔍 Verifying message was saved...")
                verify_url = f"{SUPABASE_URL}/rest/v1/tavern_messages?id=eq.{message_data['id']}"
                verify_response = requests.get(verify_url, headers=headers, verify=False)
                
                if verify_response.status_code == 200:
                    saved_messages = verify_response.json()
                    if saved_messages:
                        saved_message = saved_messages[0]
                        saved_display_name = saved_message.get('display_name')
                        print(f"✅ Saved display_name: '{saved_display_name}'")
                        
                        if saved_display_name == display_name:
                            print("🎉 Display name saved correctly!")
                        else:
                            print(f"❌ Display name mismatch! Expected: '{display_name}', Got: '{saved_display_name}'")
                    else:
                        print("❌ Message not found after saving")
                else:
                    print(f"❌ Error verifying message: {verify_response.status_code}")
            else:
                print(f"❌ Failed to send message: {response.status_code}")
                print(f"Error: {response.text}")
        else:
            print("❌ User not found")
    else:
        print(f"❌ Error fetching user: {users_response.status_code}")

def check_existing_messages():
    """Check existing messages for missing display_name"""
    
    print("\n🔍 Checking existing messages for missing display_name")
    print("=" * 50)
    
    # Disable SSL warnings
    requests.packages.urllib3.disable_warnings()
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Get all messages
    url = f"{SUPABASE_URL}/rest/v1/tavern_messages?select=*&order=created_at.desc"
    response = requests.get(url, headers=headers, verify=False)
    
    if response.status_code == 200:
        messages = response.json()
        print(f"📊 Found {len(messages)} messages")
        
        missing_display_names = []
        for msg in messages:
            display_name = msg.get('display_name')
            user_email = msg.get('user_email')
            message_text = msg.get('message', '')[:30]
            
            if not display_name or display_name == 'null':
                missing_display_names.append({
                    'id': msg.get('id'),
                    'user_email': user_email,
                    'message': message_text
                })
                print(f"❌ Missing display_name: {user_email} - '{message_text}...'")
            else:
                print(f"✅ Has display_name: '{display_name}' - '{message_text}...'")
        
        if missing_display_names:
            print(f"\n⚠️ Found {len(missing_display_names)} messages without display_name")
            print("These need to be updated manually or via the SQL script.")
        else:
            print("\n🎉 All messages have display_name!")
            
    else:
        print(f"❌ Error fetching messages: {response.status_code}")

if __name__ == "__main__":
    test_send_message_with_display_name()
    check_existing_messages()