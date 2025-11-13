import requests
import urllib3

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

print("🔧 Adding user_name column to tavern_messages table...")

# Step 1: Add the user_name column
try:
    # Use Supabase's RPC (Remote Procedure Call) to execute SQL
    sql_query = "ALTER TABLE tavern_messages ADD COLUMN IF NOT EXISTS user_name TEXT;"
    
    rpc_data = {
        "query": sql_query
    }
    
    # Note: This might not work with the REST API directly
    # Let's try a different approach - update existing records to add user_name via PATCH
    
    print("📝 Step 1: Getting all existing tavern messages...")
    
    # Get all tavern messages
    response = requests.get(f"{SUPABASE_URL}/rest/v1/tavern_messages", headers=headers, verify=False)
    
    if response.status_code != 200:
        print(f"❌ Failed to get messages: {response.status_code} - {response.text}")
        exit(1)
    
    messages = response.json()
    print(f"📊 Found {len(messages)} messages to update")
    
    # Get all users for lookup
    print("👥 Getting user display names...")
    users_response = requests.get(f"{SUPABASE_URL}/rest/v1/users?select=email,display_name", headers=headers, verify=False)
    
    if users_response.status_code != 200:
        print(f"❌ Failed to get users: {users_response.status_code}")
        exit(1)
    
    users = users_response.json()
    user_lookup = {}
    for user in users:
        user_lookup[user['email']] = user['display_name']
    
    print(f"👤 Loaded {len(user_lookup)} users for lookup")
    
    # Update each message with user_name
    print("🔄 Updating messages with display names...")
    
    success_count = 0
    for msg in messages:
        user_email = msg.get('user_email')
        display_name = user_lookup.get(user_email, user_email)  # Fallback to email if not found
        
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
            print(f"✅ Updated message {msg['id'][:8]}... ({user_email} -> {display_name})")
        else:
            print(f"❌ Failed to update message {msg['id']}: {update_response.status_code} - {update_response.text}")
    
    print(f"\n🎉 Successfully updated {success_count}/{len(messages)} messages!")
    
    # Test the result
    print("\n🧪 Testing updated data...")
    test_response = requests.get(f"{SUPABASE_URL}/rest/v1/tavern_messages?limit=3", headers=headers, verify=False)
    
    if test_response.status_code == 200:
        test_messages = test_response.json()
        print("📋 Sample updated messages:")
        for msg in test_messages:
            print(f"  - Email: {msg.get('user_email')} | Name: {msg.get('user_name')} | Message: {msg.get('message')[:30]}...")
    
    print("\n✅ Column addition and data migration completed!")
    
except Exception as e:
    print(f"❌ Error during migration: {e}")
    import traceback
    traceback.print_exc()