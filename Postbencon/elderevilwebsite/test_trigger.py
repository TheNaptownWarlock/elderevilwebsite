"""
Modified save_to_database call for tavern_messages after trigger is applied.

Instead of:
save_to_database("tavern_messages", {
    "id": message_data["id"],
    "user_email": message_data["user_email"],
    "message": message_data["message"],
    "display_name": message_data["user_name"]  # Remove this line
})

Use:
save_to_database("tavern_messages", {
    "id": message_data["id"],
    "user_email": message_data["user_email"],
    "message": message_data["message"]
    # display_name will be auto-populated by the database trigger
})
"""

# Test script to verify the trigger works
import requests
import urllib3
import uuid

urllib3.disable_warnings()

base_url = "https://uvsdbuonyfzajhtrgnxq.supabase.co"
api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV2c2RidW9ueWZ6YWpodHJnbnhxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEwNjUxNjgsImV4cCI6MjA3NjY0MTE2OH0.tq_dQfCIl68bSt2BUPP0lWW2DjjwPpxcKV6LIt2LRFg"

headers = {
    'apikey': api_key,
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json',
    'Prefer': 'return=minimal'
}

def test_trigger():
    """Test that the trigger auto-populates display_name"""
    print("Testing database trigger for auto-populating display_name...")
    
    # Test message WITHOUT display_name
    test_message = {
        "id": str(uuid.uuid4()),
        "user_email": "benbusald@gmail.com",
        "message": "Testing auto-populate trigger - no display_name passed"
        # Note: NO display_name field passed - let trigger handle it
    }
    
    print("Sending message WITHOUT display_name:")
    print(f"Data: {test_message}")
    
    # Send to database
    url = f"{base_url}/rest/v1/tavern_messages"
    response = requests.post(url, headers=headers, json=test_message, verify=False)
    
    print(f"Response status: {response.status_code}")
    
    if response.status_code in [200, 201]:
        print("✅ Message inserted successfully!")
        
        # Fetch the message back to see if display_name was populated
        print("\nFetching message to verify display_name was auto-populated...")
        fetch_response = requests.get(
            f"{base_url}/rest/v1/tavern_messages?id=eq.{test_message['id']}", 
            headers=headers, 
            verify=False
        )
        
        if fetch_response.status_code == 200:
            saved_msg = fetch_response.json()[0]
            display_name = saved_msg.get('display_name')
            
            print(f"Retrieved message:")
            print(f"  ID: {saved_msg['id']}")
            print(f"  User Email: {saved_msg['user_email']}")
            print(f"  Display Name: {repr(display_name)}")
            print(f"  Message: {saved_msg['message']}")
            
            if display_name and display_name != "":
                print("✅ SUCCESS: display_name was auto-populated by trigger!")
            else:
                print("❌ FAILED: display_name is still NULL - trigger not working")
        else:
            print(f"❌ Failed to fetch message: {fetch_response.status_code}")
    else:
        print(f"❌ Failed to insert message: {response.status_code} - {response.text}")

if __name__ == "__main__":
    print("This script tests the database trigger.")
    print("Make sure you've applied the trigger SQL first!")
    print("=" * 50)
    test_trigger()