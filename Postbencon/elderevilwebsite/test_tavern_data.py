import requests
import json

# Test tavern messages and users data
url_messages = 'https://uvsdbuonyfzajhtrgnxq.supabase.co/rest/v1/tavern_messages'
url_users = 'https://uvsdbuonyfzajhtrgnxq.supabase.co/rest/v1/users?select=email,display_name'

headers = {
    'apikey': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV2c2RidW9ueWZ6YWpodHJnbnhxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEwNjUxNjgsImV4cCI6MjA3NjY0MTE2OH0.tq_dQfCIl68bSt2BUPP0lWW2DjjwPpxcKV6LIt2LRFg'
}

# Get tavern messages
print("=== TAVERN MESSAGES ===")
r = requests.get(url_messages, headers=headers, verify=False)
messages = r.json()[:5]  # First 5 messages
for i, msg in enumerate(messages):
    print(f"{i+1}. Email: {msg.get('user_email')}")
    print(f"   Message: {msg.get('message')[:50]}...")
    print("")

# Get users to match emails to display names
print("\n=== USERS ===")
r = requests.get(url_users, headers=headers, verify=False)
users = r.json()
user_lookup = {}
for user in users:
    user_lookup[user.get('email')] = user.get('display_name')
    print(f"Email: {user.get('email')} -> Display Name: {user.get('display_name')}")

print("\n=== MAPPING CHECK ===")
for i, msg in enumerate(messages):
    user_email = msg.get('user_email')
    display_name = user_lookup.get(user_email, 'NOT FOUND')
    print(f"{i+1}. {user_email} -> {display_name}")