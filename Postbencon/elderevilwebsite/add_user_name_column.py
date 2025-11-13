"""
Script to add user_name column to tavern_messages and populate existing records
"""
import requests
import urllib3
import json
from datetime import datetime

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Supabase configuration
SUPABASE_URL = "https://uvsdbuonyfzajhtrgnxq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV2c2RidW9ueWZ6YWpodHJnbnhxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEwNjUxNjgsImV4cCI6MjA3NjY0MTE2OH0.tq_dQfCIl68bSt2BUPP0lWW2DjjwPpxcKV6LIt2LRFg"

headers = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json'
}

def add_user_name_column():
    """
    Since we can't run DDL via REST API, we'll simulate adding the column
    by trying to update a record with the new field. If it fails, we know the column doesn't exist.
    """
    print("🔧 Step 1: Testing if user_name column exists...")
    
    # Get a sample message to test with
    response = requests.get(f"{SUPABASE_URL}/rest/v1/tavern_messages?limit=1", headers=headers, verify=False)
    if response.status_code != 200 or not response.json():
        print("❌ No messages found to test with")
        return False
    
    test_message = response.json()[0]
    test_id = test_message['id']
    
    # Try to update with user_name field
    test_update = {"user_name": "TEST"}
    update_response = requests.patch(
        f"{SUPABASE_URL}/rest/v1/tavern_messages?id=eq.{test_id}", 
        headers=headers, 
        json=test_update, 
        verify=False
    )
    
    if update_response.status_code in [200, 204]:
        print("✅ user_name column already exists!")
        return True
    elif "does not exist" in update_response.text or "PGRST204" in update_response.text:
        print("❌ user_name column does not exist")
        print("📝 You need to add the column manually in Supabase dashboard:")
        print("   1. Go to https://app.supabase.com/project/uvsdbuonyfzajhtrgnxq/editor")
        print("   2. Select tavern_messages table")  
        print("   3. Click 'Add Column'")
        print("   4. Name: user_name, Type: text, Nullable: true")
        print("   5. Click Save")
        print("   6. Then run this script again")
        return False
    else:
        print(f"⚠️ Unexpected response: {update_response.status_code} - {update_response.text}")
        return False

def populate_user_names():
    """Populate user_name for all existing tavern messages"""
    print("\n📝 Step 2: Populating user_name for existing messages...")
    
    # Get all tavern messages
    response = requests.get(f"{SUPABASE_URL}/rest/v1/tavern_messages", headers=headers, verify=False)
    
    if response.status_code != 200:
        print(f"❌ Failed to get messages: {response.status_code} - {response.text}")
        return False
    
    messages = response.json()
    print(f"📊 Found {len(messages)} messages to update")
    
    # Get all users for lookup
    print("👥 Loading user display names...")
    users_response = requests.get(f"{SUPABASE_URL}/rest/v1/users?select=email,display_name", headers=headers, verify=False)
    
    if users_response.status_code != 200:
        print(f"❌ Failed to get users: {users_response.status_code}")
        return False
    
    users = users_response.json()
    user_lookup = {}
    for user in users:
        user_lookup[user['email']] = user['display_name']
    
    print(f"👤 Loaded {len(user_lookup)} users for lookup")
    
    # Update each message with user_name
    print("🔄 Updating messages...")
    
    success_count = 0
    error_count = 0
    
    for i, msg in enumerate(messages, 1):
        user_email = msg.get('user_email')
        display_name = user_lookup.get(user_email, user_email)  # Fallback to email if not found
        
        # Skip if user_name already exists and is correct
        if msg.get('user_name') == display_name:
            print(f"⏭️  {i}/{len(messages)}: {msg['id'][:8]}... already has correct user_name")
            success_count += 1
            continue
        
        # Update the message with user_name
        update_data = {"user_name": display_name}
        
        update_response = requests.patch(
            f"{SUPABASE_URL}/rest/v1/tavern_messages?id=eq.{msg['id']}", 
            headers=headers, 
            json=update_data, 
            verify=False
        )
        
        if update_response.status_code in [200, 204]:
            success_count += 1
            print(f"✅ {i}/{len(messages)}: Updated {msg['id'][:8]}... ({user_email} -> {display_name})")
        else:
            error_count += 1
            print(f"❌ {i}/{len(messages)}: Failed to update {msg['id']}: {update_response.status_code} - {update_response.text}")
    
    print(f"\n🎉 Update complete: {success_count} successful, {error_count} errors")
    return error_count == 0

def verify_updates():
    """Verify that updates were successful"""
    print("\n🧪 Step 3: Verifying updates...")
    
    response = requests.get(f"{SUPABASE_URL}/rest/v1/tavern_messages?limit=5", headers=headers, verify=False)
    
    if response.status_code == 200:
        messages = response.json()
        print("📋 Sample updated messages:")
        for msg in messages:
            user_name = msg.get('user_name', 'NOT SET')
            user_email = msg.get('user_email', 'NO EMAIL')
            message_text = msg.get('message', '')[:30] + '...' if len(msg.get('message', '')) > 30 else msg.get('message', '')
            print(f"  - Email: {user_email} | Name: {user_name} | Message: {message_text}")
        
        # Check if any messages still missing user_name
        missing_count = sum(1 for msg in messages if not msg.get('user_name'))
        if missing_count > 0:
            print(f"⚠️  {missing_count} messages still missing user_name")
            return False
        else:
            print("✅ All sample messages have user_name populated!")
            return True
    else:
        print(f"❌ Failed to verify: {response.status_code}")
        return False

def main():
    print("🚀 Starting tavern_messages user_name migration...")
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Check if column exists
    if not add_user_name_column():
        print("\n❌ Migration failed: user_name column does not exist")
        print("📋 Manual steps required:")
        print("   1. Add the column in Supabase dashboard (see instructions above)")
        print("   2. Run this script again")
        return
    
    # Step 2: Populate user names
    if not populate_user_names():
        print("\n❌ Migration failed during population step")
        return
    
    # Step 3: Verify
    if not verify_updates():
        print("\n❌ Migration completed but verification failed")
        return
    
    print(f"\n🎉 Migration completed successfully!")
    print(f"🕐 Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n📝 Next steps:")
    print("   1. Restart your Streamlit app")
    print("   2. Test the tavern chat - should now show display names")
    print("   3. New messages will automatically include user_name")

if __name__ == "__main__":
    main()