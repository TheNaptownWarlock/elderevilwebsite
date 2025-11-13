import requests
import urllib3
import uuid
from datetime import datetime

# Disable SSL warnings
urllib3.disable_warnings()

# Test data - simulate a logged-in user
test_user_email = "benbusald@gmail.com"
test_display_name = "Ben 'Buzzy'"
test_message = "Debug test - checking display_name saving"

print(f"Testing tavern message save for user: {test_user_email}")
print(f"Display name: {test_display_name}")
print(f"Message: {test_message}")
print("=" * 60)

# Simulate the send_tavern_message function call
message_data = {
    "id": str(uuid.uuid4()),
    "user_email": test_user_email,
    "message": test_message,
    "display_name": test_display_name  # This should be saved to the display_name column
}

print("Data being sent to Supabase:")
import json
print(json.dumps(message_data, indent=2))

# Send to Supabase directly (same as save_to_supabase function)
base_url = "https://uvsdbuonyfzajhtrgnxq.supabase.co"
api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV2c2RidW9ueWZ6YWpodHJnbnhxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEwNjUxNjgsImV4cCI6MjA3NjY0MTE2OH0.tq_dQfCIl68bSt2BUPP0lWW2DjjwPpxcKV6LIt2LRFg"

headers = {
    'apikey': api_key,
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json',
    'Prefer': 'return=minimal'
}

print("\nSending to Supabase...")
url = f"{base_url}/rest/v1/tavern_messages"
response = requests.post(url, headers=headers, json=message_data, verify=False)

print(f"Response status: {response.status_code}")
print(f"Response text: {response.text}")

if response.status_code in [200, 201]:
    print("✅ Message saved successfully!")
    
    # Verify it was saved correctly
    print("\nVerifying the message was saved with display_name...")
    response = requests.get(f"{base_url}/rest/v1/tavern_messages?id=eq.{message_data['id']}", headers=headers, verify=False)
    
    if response.status_code == 200:
        saved_messages = response.json()
        if saved_messages:
            saved_msg = saved_messages[0]
            print(f"✅ Message retrieved:")
            print(f"   ID: {saved_msg['id']}")
            print(f"   User Email: {saved_msg['user_email']}")
            print(f"   Display Name: {repr(saved_msg.get('display_name'))}")
            print(f"   Message: {saved_msg['message']}")
        else:
            print("❌ No message found with that ID")
    else:
        print(f"❌ Failed to retrieve saved message: {response.status_code}")
else:
    print("❌ Failed to save message")
    if "constraint" in response.text:
        print("   This might be a foreign key constraint issue")