import requests
import json

requests.packages.urllib3.disable_warnings()

headers = {
    'apikey': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV2c2RidW9ueWZ6YWpodHJnbnhxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEwNjUxNjgsImV4cCI6MjA3NjY0MTE2OH0.tq_dQfCIl68bSt2BUPP0lWW2DjjwPpxcKV6LIt2LRFg',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV2c2RidW9ueWZ6YWpodHJnbnhxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEwNjUxNjgsImV4cCI6MjA3NjY0MTE2OH0.tq_dQfCIl68bSt2BUPP0lWW2DjjwPpxcKV6LIt2LRFg'
}

r = requests.get('https://uvsdbuonyfzajhtrgnxq.supabase.co/rest/v1/tavern_messages?select=*&order=created_at.desc&limit=10', headers=headers, verify=False)

if r.status_code == 200:
    msgs = r.json()
    print(f"Found {len(msgs)} recent messages:")
    print("-" * 60)
    
    for i, m in enumerate(msgs, 1):
        user_email = m.get('user_email', 'unknown')
        display_name = m.get('display_name', 'NULL')
        message = m.get('message', '')[:40]
        created_at = m.get('created_at', '')
        
        print(f"{i}. {user_email}")
        print(f"   Display Name: {display_name}")
        print(f"   Message: {message}...")
        print(f"   Time: {created_at}")
        
        if not display_name or display_name == 'null':
            print("   ❌ MISSING DISPLAY NAME!")
        else:
            print("   ✅ Has display name")
        print()
else:
    print(f"Error: {r.status_code}")
    print(r.text)