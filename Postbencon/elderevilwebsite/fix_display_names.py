import requests

def fix_missing_display_names():
    """Fix existing messages that are missing display_name"""
    
    print("🔧 Fixing missing display_names in tavern_messages...")
    
    # Disable SSL warnings
    requests.packages.urllib3.disable_warnings()
    
    base_url = "https://uvsdbuonyfzajhtrgnxq.supabase.co"
    api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV2c2RidW9ueWZ6YWpodHJnbnhxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEwNjUxNjgsImV4cCI6MjA3NjY0MTE2OH0.tq_dQfCIl68bSt2BUPP0lWW2DjjwPpxcKV6LIt2LRFg"
    
    headers = {
        'apikey': api_key,
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # 1. Get all messages missing display_name (get all and filter in Python)
    messages_url = f"{base_url}/rest/v1/tavern_messages?select=*"
    messages_response = requests.get(messages_url, headers=headers, verify=False)
    
    if messages_response.status_code != 200:
        print(f"❌ Error fetching messages: {messages_response.status_code}")
        return
    
    all_messages = messages_response.json()
    # Filter for messages with null or missing display_name
    messages_missing_names = [msg for msg in all_messages if not msg.get('display_name')]
    print(f"📊 Found {len(messages_missing_names)} out of {len(all_messages)} messages missing display_name")
    
    if not messages_missing_names:
        print("✅ All messages already have display_name!")
        return
    
    # 2. Get all users for lookup
    users_url = f"{base_url}/rest/v1/users?select=email,display_name"
    users_response = requests.get(users_url, headers=headers, verify=False)
    
    if users_response.status_code != 200:
        print(f"❌ Error fetching users: {users_response.status_code}")
        return
    
    users = users_response.json()
    users_dict = {user['email']: user['display_name'] for user in users}
    print(f"👥 Loaded {len(users_dict)} users for lookup")
    
    # 3. Update each message
    updated_count = 0
    for msg in messages_missing_names:
        message_id = msg.get('id')
        user_email = msg.get('user_email')
        
        if user_email in users_dict:
            display_name = users_dict[user_email]
            
            # Update the message
            update_url = f"{base_url}/rest/v1/tavern_messages?id=eq.{message_id}"
            update_data = {'display_name': display_name}
            
            response = requests.patch(update_url, headers=headers, json=update_data, verify=False)
            
            if response.status_code in [200, 204]:
                print(f"✅ Updated message {message_id}: {user_email} -> '{display_name}'")
                updated_count += 1
            else:
                print(f"❌ Failed to update message {message_id}: {response.status_code}")
                print(f"   Error: {response.text}")
        else:
            print(f"⚠️ No user found for email: {user_email}")
    
    print(f"\n🎉 Successfully updated {updated_count}/{len(messages_missing_names)} messages!")

if __name__ == "__main__":
    fix_missing_display_names()