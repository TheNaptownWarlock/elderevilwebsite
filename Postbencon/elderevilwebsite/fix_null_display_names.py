import requests
import urllib3

# Disable SSL warnings
urllib3.disable_warnings()

base_url = "https://uvsdbuonyfzajhtrgnxq.supabase.co"
api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV2c2RidW9ueWZ6YWpodHJnbnhxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEwNjUxNjgsImV4cCI6MjA3NjY0MTE2OH0.tq_dQfCIl68bSt2BUPP0lWW2DjjwPpxcKV6LIt2LRFg"

headers = {
    'apikey': api_key,
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

print("Fixing messages with NULL display_name values...")
print("=" * 50)

# Get all messages with NULL display_name
response = requests.get(f"{base_url}/rest/v1/tavern_messages?display_name=is.null", headers=headers, verify=False)

if response.status_code == 200:
    null_messages = response.json()
    print(f"Found {len(null_messages)} messages with NULL display_name")
    
    # Get user data to lookup display names
    users_response = requests.get(f"{base_url}/rest/v1/users", headers=headers, verify=False)
    if users_response.status_code == 200:
        users = {user['email']: user['display_name'] for user in users_response.json()}
        
        for msg in null_messages:
            user_email = msg['user_email']
            message_id = msg['id']
            
            # Get display name for this user
            if user_email in users:
                display_name = users[user_email]
                print(f"Updating message '{msg['message'][:30]}...' from {user_email}")
                print(f"  Setting display_name to: {display_name}")
                
                # Update the message
                update_data = {"display_name": display_name}
                update_response = requests.patch(
                    f"{base_url}/rest/v1/tavern_messages?id=eq.{message_id}",
                    headers=headers,
                    json=update_data,
                    verify=False
                )
                
                if update_response.status_code == 204:
                    print(f"  ✅ Updated successfully")
                else:
                    print(f"  ❌ Update failed: {update_response.status_code} - {update_response.text}")
            else:
                print(f"❌ No user found for email: {user_email}")
            print()
    else:
        print(f"Failed to fetch users: {users_response.status_code}")
else:
    print(f"Failed to fetch messages: {response.status_code}")

print("✅ Finished updating NULL display_name values")