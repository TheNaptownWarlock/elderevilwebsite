#!/usr/bin/env python3
"""
Script to add display_name column to tavern_messages table in Supabase
and populate it with data from the users table.
"""

import requests
import json

# Supabase configuration
SUPABASE_URL = "https://uvsdbuonyfzajhtrgnxq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV2c2RidW9ueWZ6YWpodHJnbnhxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEwNjUxNjgsImV4cCI6MjA3NjY0MTE2OH0.tq_dQfCIl68bSt2BUPP0lWW2DjjwPpxcKV6LIt2LRFg"

def execute_sql(sql_query):
    """Execute SQL query using Supabase RPC"""
    
    # Disable SSL warnings
    requests.packages.urllib3.disable_warnings()
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Use Supabase RPC to execute raw SQL
    url = f"{SUPABASE_URL}/rest/v1/rpc/exec_sql"
    
    payload = {
        "sql": sql_query
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, verify=False)
        print(f"SQL Execution Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            print("✅ SQL executed successfully!")
            if response.text:
                print(f"Response: {response.text}")
            return True
        else:
            print(f"❌ SQL execution failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error executing SQL: {e}")
        return False

def add_display_name_column():
    """Add display_name column to tavern_messages and populate it"""
    
    print("🔧 Adding display_name column to tavern_messages table...")
    
    # Step 1: Add the column
    sql_add_column = """
    ALTER TABLE tavern_messages 
    ADD COLUMN IF NOT EXISTS display_name TEXT;
    """
    
    if not execute_sql(sql_add_column):
        print("❌ Failed to add column")
        return False
    
    print("✅ Column added successfully")
    
    # Step 2: Update existing records
    print("🔄 Updating existing records with display names...")
    
    sql_update_records = """
    UPDATE tavern_messages 
    SET display_name = users.display_name
    FROM users 
    WHERE tavern_messages.user_email = users.email
    AND tavern_messages.display_name IS NULL;
    """
    
    if not execute_sql(sql_update_records):
        print("❌ Failed to update records")
        return False
    
    print("✅ Records updated successfully")
    
    # Step 3: Create index
    print("🔧 Creating index for performance...")
    
    sql_create_index = """
    CREATE INDEX IF NOT EXISTS idx_tavern_messages_user_email 
    ON tavern_messages(user_email);
    """
    
    if not execute_sql(sql_create_index):
        print("⚠️ Failed to create index (this is optional)")
    else:
        print("✅ Index created successfully")
    
    return True

def verify_update():
    """Verify that the update worked by checking some records"""
    
    print("🔍 Verifying the update...")
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Get some tavern messages to verify
    url = f"{SUPABASE_URL}/rest/v1/tavern_messages?select=id,user_email,display_name,message&limit=5"
    
    try:
        response = requests.get(url, headers=headers, verify=False)
        
        if response.status_code == 200:
            messages = response.json()
            print(f"✅ Retrieved {len(messages)} sample records:")
            
            for msg in messages:
                print(f"  - Email: {msg.get('user_email')}")
                print(f"    Display Name: {msg.get('display_name')}")
                print(f"    Message: {msg.get('message', '')[:50]}...")
                print()
            
            return True
        else:
            print(f"❌ Failed to verify: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying: {e}")
        return False

def main():
    """Main function to run the update process"""
    
    print("🚀 Starting Supabase tavern_messages table update...")
    print("=" * 60)
    
    # Note: Supabase doesn't typically allow direct SQL execution via API
    # You'll need to run this SQL manually in the Supabase SQL editor
    
    print("⚠️  IMPORTANT: Supabase doesn't allow direct SQL execution via API.")
    print("📝 Please copy and paste the following SQL into your Supabase SQL editor:")
    print("=" * 60)
    
    sql_script = """
-- Add display_name column to tavern_messages table
ALTER TABLE tavern_messages 
ADD COLUMN IF NOT EXISTS display_name TEXT;

-- Update all existing records to populate display_name from users table
UPDATE tavern_messages 
SET display_name = users.display_name
FROM users 
WHERE tavern_messages.user_email = users.email
AND tavern_messages.display_name IS NULL;

-- Create an index for better performance
CREATE INDEX IF NOT EXISTS idx_tavern_messages_user_email 
ON tavern_messages(user_email);

-- Verify the update (optional)
SELECT 
  tm.id,
  tm.user_email,
  tm.display_name,
  tm.message,
  tm.created_at
FROM tavern_messages tm
ORDER BY tm.created_at DESC
LIMIT 10;
"""
    
    print(sql_script)
    print("=" * 60)
    
    # Alternative: Update via API calls
    print("\n🔄 Alternative: Updating via API calls...")
    
    if update_via_api():
        print("✅ Update completed successfully!")
        verify_update()
    else:
        print("❌ API update failed. Please use the SQL script above.")

def update_via_api():
    """Update records via API calls (alternative method)"""
    
    try:
        # First, get all tavern messages
        print("📥 Fetching all tavern messages...")
        
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json'
        }
        
        # Get tavern messages
        url = f"{SUPABASE_URL}/rest/v1/tavern_messages"
        response = requests.get(url, headers=headers, verify=False)
        
        if response.status_code != 200:
            print(f"❌ Failed to fetch tavern messages: {response.status_code}")
            return False
        
        messages = response.json()
        print(f"📊 Found {len(messages)} tavern messages")
        
        # Get all users
        print("👥 Fetching all users...")
        url = f"{SUPABASE_URL}/rest/v1/users"
        response = requests.get(url, headers=headers, verify=False)
        
        if response.status_code != 200:
            print(f"❌ Failed to fetch users: {response.status_code}")
            return False
        
        users = response.json()
        users_dict = {user['email']: user['display_name'] for user in users}
        print(f"👥 Found {len(users)} users")
        
        # Update each message
        print("🔄 Updating messages...")
        updated_count = 0
        
        for msg in messages:
            user_email = msg.get('user_email')
            if user_email in users_dict:
                display_name = users_dict[user_email]
                
                # Update the message with display_name
                update_data = {
                    'display_name': display_name
                }
                
                update_url = f"{SUPABASE_URL}/rest/v1/tavern_messages?id=eq.{msg['id']}"
                update_response = requests.patch(
                    update_url, 
                    headers=headers, 
                    json=update_data, 
                    verify=False
                )
                
                if update_response.status_code in [200, 204]:
                    updated_count += 1
                    print(f"  ✅ Updated message {msg['id']} for {user_email}")
                else:
                    print(f"  ❌ Failed to update message {msg['id']}: {update_response.status_code}")
        
        print(f"✅ Updated {updated_count}/{len(messages)} messages")
        return updated_count > 0
        
    except Exception as e:
        print(f"❌ Error in API update: {e}")
        return False

if __name__ == "__main__":
    main()