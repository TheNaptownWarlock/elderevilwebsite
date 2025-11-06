import requests

base_url = 'https://uvsdbuonyfzajhtrgnxq.supabase.co'
api_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV2c2RidW9ueWZ6YWpodHJnbnhxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEwNjUxNjgsImV4cCI6MjA3NjY0MTE2OH0.tq_dQfCIl68bSt2BUPP0lWW2DjjwPpxcKV6LIt2LRFg'
headers = {'apikey': api_key, 'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}

# Current avatar mappings
AVATAR_OPTIONS = {
    "🧙‍♂️": "Trash Wizard",
    "⚔️": "Chaos Goblin", 
    "🏹": "Rotten Archer",
    "🛡️": "Self-Righteous Nerd",
    "🗡️": "Stabby Rogue",
    "🔮": "Skooma Sorc",
    "📚": "Da Worm",
    "🎭": "Theatre Kid",
    "🐉": "Scaly Bastard",
    "🦄": "Unicorn Corpse",
    "🔥": "Fire Hazard",
    "❄️": "Buzzkill",
    "🌟": "Special Little Guy",
    "🦅": "Sky Rat",
    "👑": "Mole King",
    "🦊": "Foxy Schmoxy",
    "🐸": "Froggo",
    "🦉": "Pondering Owl",
    "🐺": "Luuupe",
    "🦋": "Cottage Core Wench",
    "🌙": "Astrology Hoe",
    "☀️": "Praiser of da Sun",
    "⚡": "Sparky Lad",
    "🌊": "Catch-a-ride",
    "🌪️": "Disaster Gay",
    "🍄": "Shroom Enjoyer",
    "🌿": "Illya's Fated Foe",
    "💀": "Rag N' Bones"
}

print("Updating tavern message class names in database...")

# 1. Get all users to map emails to avatars
print("Getting user avatars...")
users_response = requests.get(f'{base_url}/rest/v1/users', headers=headers, verify=False)
user_avatars = {}
if users_response.status_code == 200:
    users = users_response.json()
    for user in users:
        email = user.get('email')
        avatar = user.get('avatar', '🧙‍♂️')
        user_avatars[email] = avatar
        print(f"  {email}: {avatar} -> {AVATAR_OPTIONS.get(avatar, 'Unknown')}")
else:
    print(f"Failed to get users: {users_response.status_code}")
    exit(1)

# 2. Get all tavern messages
print("\nGetting tavern messages...")
messages_response = requests.get(f'{base_url}/rest/v1/tavern_messages', headers=headers, verify=False)
if messages_response.status_code != 200:
    print(f"Failed to get messages: {messages_response.status_code}")
    exit(1)

messages = messages_response.json()
print(f"Found {len(messages)} tavern messages")

# 3. Update each message with correct class name
updated_count = 0
for msg in messages:
    msg_id = msg.get('id')
    user_email = msg.get('user_email')
    current_class = msg.get('user_class', '')
    
    if user_email in user_avatars:
        user_avatar = user_avatars[user_email]
        correct_class = AVATAR_OPTIONS.get(user_avatar, 'Adventurer')
        
        if current_class != correct_class:
            print(f"\nUpdating message {msg_id[:8]}...")
            print(f"  User: {user_email}")
            print(f"  Avatar: {user_avatar}")
            print(f"  Old class: {current_class}")
            print(f"  New class: {correct_class}")
            
            # Update the message in database
            update_url = f"{base_url}/rest/v1/tavern_messages?id=eq.{msg_id}"
            update_data = {"user_class": correct_class}
            
            update_response = requests.patch(update_url, headers=headers, json=update_data, verify=False)
            if update_response.status_code in [200, 204]:
                print(f"  ✅ Updated successfully")
                updated_count += 1
            else:
                print(f"  ❌ Update failed: {update_response.status_code}")
        else:
            print(f"Message {msg_id[:8]} already has correct class: {correct_class}")

print(f"\n🎉 Updated {updated_count} tavern messages with correct class names!")