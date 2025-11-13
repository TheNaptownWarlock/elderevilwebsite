import requests
import urllib3

# Disable SSL warnings
urllib3.disable_warnings()

base_url = "https://uvsdbuonyfzajhtrgnxq.supabase.co"
api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV2c2RidW9ueWZ6YWpodHJnbnhxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEwNjUxNjgsImV4cCI6MjA3NjY0MTE2OH0.tq_dQfCIl68bSt2BUPP0lWW2DjjwPpxcKV6LIt2LRFg"

# Read the trigger SQL
with open('auto_populate_display_name_trigger.sql', 'r') as f:
    trigger_sql = f.read()

print("Applying database trigger to auto-populate display_name...")
print("=" * 60)

# Supabase uses PostgREST for database operations
# For DDL operations like CREATE FUNCTION and CREATE TRIGGER, we need to use the SQL endpoint
# This requires the service_role key, not the anon key

print("⚠️ NOTE: This script requires the service_role key to execute DDL operations.")
print("The anon key cannot create functions or triggers.")
print("\nTo apply this trigger:")
print("1. Go to your Supabase dashboard")
print("2. Navigate to the SQL Editor")
print("3. Copy and paste the contents of 'auto_populate_display_name_trigger.sql'")
print("4. Run the SQL query")
print("\nAlternatively, if you have the service_role key, you can:")
print("1. Replace the api_key above with your service_role key")
print("2. Uncomment the code below and run this script")

# Uncomment and modify this section if you have the service_role key:
"""
headers = {
    'apikey': api_key,  # This should be service_role key
    'Authorization': f'Bearer {api_key}',  # This should be service_role key
    'Content-Type': 'application/json'
}

# Execute the SQL
response = requests.post(
    f"{base_url}/rest/v1/rpc/exec_sql",
    headers=headers,
    json={"sql": trigger_sql},
    verify=False
)

if response.status_code == 200:
    print("✅ Trigger created successfully!")
else:
    print(f"❌ Failed to create trigger: {response.status_code} - {response.text}")
"""

print("\nAfter applying the trigger, test it by sending a new tavern message!")
print("The display_name should automatically populate from the users table.")