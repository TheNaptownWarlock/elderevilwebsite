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

print("Checking all tavern messages and their display_name values:")
print("=" * 60)

response = requests.get(f"{base_url}/rest/v1/tavern_messages?order=created_at.desc", headers=headers, verify=False)

if response.status_code == 200:
    messages = response.json()
    for i, msg in enumerate(messages):
        display_name = msg.get('display_name')
        if display_name is None:
            display_status = "NULL"
        elif display_name == "":
            display_status = "EMPTY STRING"
        else:
            display_status = f'"{display_name}"'
        
        print(f"{i+1}. User: {msg['user_email']}")
        print(f"   Display Name: {display_status}")
        print(f"   Message: {msg['message'][:50]}...")
        print(f"   Created: {msg.get('created_at', 'NO TIMESTAMP')}")
        print()
else:
    print(f"Error: {response.status_code} - {response.text}")