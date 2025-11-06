import requests

base_url = 'https://uvsdbuonyfzajhtrgnxq.supabase.co'
api_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV2c2RidW9ueWZ6YWpodHJnbnhxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEwNjUxNjgsImV4cCI6MjA3NjY0MTE2OH0.tq_dQfCIl68bSt2BUPP0lWW2DjjwPpxcKV6LIt2LRFg'
headers = {'apikey': api_key, 'Authorization': f'Bearer {api_key}'}

# Check Test user's avatar
print("Checking Test user...")
users_response = requests.get(f'{base_url}/rest/v1/users?email=eq.Test', headers=headers, verify=False)
if users_response.status_code == 200:
    users = users_response.json()
    if users:
        avatar = users[0].get('avatar', 'Not found')
        print(f'Test user avatar: {avatar}')
        
        # Map avatar to class name
        AVATAR_OPTIONS = {
            "🧙‍♂️": "Trash Wizard",
            "⚔️": "Chaos Goblin", 
            "🏹": "Rotten Archer",
            "🛡️": "Self-Righteous Nerd",
            "🗡️": "Stabby Rogue",
        }
        correct_class = AVATAR_OPTIONS.get(avatar, 'Unknown')
        print(f'Should be class: {correct_class}')
    else:
        print('Test user not found')
else:
    print(f'Failed to get users: {users_response.status_code}')

# Check tavern messages
print("\nChecking tavern messages for Test user...")
msg_response = requests.get(f'{base_url}/rest/v1/tavern_messages?user_email=eq.Test', headers=headers, verify=False)
if msg_response.status_code == 200:
    messages = msg_response.json()
    for msg in messages:
        message_text = msg.get('message', '')[:30]
        stored_class = msg.get('user_class', 'No class stored')
        msg_id = msg.get('id', 'no-id')
        print(f'Message ID: {msg_id}')
        print(f'  Text: {message_text}...')
        print(f'  Stored class: {stored_class}')
        print()
else:
    print(f'Failed to get tavern messages: {msg_response.status_code}')