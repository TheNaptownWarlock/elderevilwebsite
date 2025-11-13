#!/usr/bin/env python3
"""
Test script to check tavern_messages table and fix the loading issue
"""

import requests
import json
from datetime import datetime

# Supabase configuration
SUPABASE_URL = "https://uvsdbuonyfzajhtrgnxq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV2c2RidW9ueWZ6YWpodHJnbnhxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEwNjUxNjgsImV4cCI6MjA3NjY0MTE2OH0.tq_dQfCIl68bSt2BUPP0lWW2DjjwPpxcKV6LIt2LRFg"

headers = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json'
}

def test_tavern_messages():
    """Test the tavern_messages table"""
    print("🔍 Testing tavern_messages table...")
    
    # Try to fetch existing messages
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/tavern_messages?select=*&order=created_at.asc",
            headers=headers,
            verify=False
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            messages = response.json()
            print(f"✅ Found {len(messages)} messages in tavern_messages table")
            
            if messages:
                for i, msg in enumerate(messages):
                    print(f"  Message {i+1}: {msg}")
            else:
                print("📭 Table is empty - this might be causing the loading issue")
                
            return messages
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response text: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        return None

def add_sample_message():
    """Add a sample message to test the table"""
    print("\n🧪 Adding a sample message...")
    
    sample_message = {
        "id": "test-message-123",
        "user_email": "test@example.com", 
        "message": "Welcome to the tavern! 🍺 This is a test message.",
        "created_at": datetime.now().isoformat()
    }
    
    try:
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/tavern_messages",
            headers=headers,
            json=sample_message,
            verify=False
        )
        
        print(f"Insert response status: {response.status_code}")
        if response.status_code in [200, 201]:
            print("✅ Sample message added successfully!")
        else:
            print(f"❌ Failed to add message: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception adding message: {e}")

def check_table_structure():
    """Check the table structure"""
    print("\n📋 Checking table structure...")
    
    try:
        # Try to get table schema info by making a request with no results
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/tavern_messages?limit=0",
            headers=headers,
            verify=False
        )
        
        print(f"Schema check status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Table exists and is accessible")
        else:
            print(f"❌ Table access issue: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception checking structure: {e}")

if __name__ == "__main__":
    print("🍺 Tavern Messages Diagnostic Tool")
    print("=" * 50)
    
    # Check table structure
    check_table_structure()
    
    # Test existing messages
    messages = test_tavern_messages()
    
    # If no messages, add a sample
    if messages is not None and len(messages) == 0:
        add_sample_message()
        
        # Re-test after adding sample
        print("\n🔄 Re-testing after adding sample...")
        test_tavern_messages()
    
    print("\n✅ Diagnostic complete!")