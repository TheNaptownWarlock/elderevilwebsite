import requests
import urllib3
import json

urllib3.disable_warnings()

url = 'https://uvsdbuonyfzajhtrgnxq.supabase.co/rest/v1/tavern_messages?select=id,user_email,message,users!tavern_messages_user_email_fkey(display_name,avatar)&limit=2'
headers = {
    'apikey': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV2c2RidW9ueWZ6YWpodHJnbnhxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEwNjUxNjgsImV4cCI6MjA3NjY0MTE2OH0.tq_dQfCIl68bSt2BUPP0lWW2DjjwPpxcKV6LIt2LRFg'
}

print('Testing JOIN query...')
r = requests.get(url, headers=headers, verify=False)
print(f'Status: {r.status_code}')
if r.status_code == 200:
    data = r.json()
    print('Sample result:')
    print(json.dumps(data, indent=2))
    print('\nParsed results:')
    for msg in data:
        user_info = msg.get('users', {})
        print(f"Email: {msg.get('user_email')} -> Display Name: {user_info.get('display_name') if user_info else 'NO JOIN DATA'}")
else:
    print(f'Error: {r.text}')