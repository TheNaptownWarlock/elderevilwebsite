"""
Script to test and refresh tavern messages with proper display names
"""
import sys
sys.path.append('.')

# Import the updated function
from app import load_tavern_messages_from_db

print("🍺 Testing updated tavern message loading...")

# Load messages using the new JOIN approach
messages = load_tavern_messages_from_db()

print(f"\n📊 Loaded {len(messages)} messages:")
for i, msg in enumerate(messages[:5]):  # Show first 5
    print(f"{i+1}. Email: {msg.get('user_email')} -> Display: {msg.get('user_name')} | Message: {msg.get('message')[:30]}...")

print("\n✅ Test completed!")