#!/usr/bin/env python3
"""
Test the exact overlap scenario the user described
"""

from datetime import datetime

def test_user_scenario():
    """Test the exact scenario: 9am-9am existing, 10am new"""
    
    print("Testing User's Exact Scenario")
    print("=" * 40)
    
    # Simulate what we get from Supabase after field mapping
    existing_event = {
        "id": "test-123",
        "name": "Test Event",
        "start": "9:00 AM",  # This comes from Supabase 'time' field
        "end": "9:00 AM",    # This comes from Supabase 'end_time' field
        "day": "Thursday",
        "creator_email": "test@example.com"
    }
    
    print("Existing Event (after field mapping):")
    for key, value in existing_event.items():
        print(f"  {key}: {value}")
    
    # New event details
    new_start_time = "10:00 AM"
    new_day = "Thursday"
    user_email = "test@example.com"
    
    print(f"\nNew Event:")
    print(f"  start_time: {new_start_time}")
    print(f"  day: {new_day}")
    print(f"  user_email: {user_email}")
    
    # Check if same day and same host
    if (existing_event.get('day') == new_day and 
        existing_event.get('creator_email') == user_email):
        
        print(f"\n+ Same day and same host - checking for overlap")
        
        # Parse existing event times
        existing_start = datetime.strptime(existing_event.get('start', '12:00 AM'), "%I:%M %p")
        existing_end_str = existing_event.get('end', existing_event.get('end_time', existing_event.get('time', '12:00 AM')))
        
        print(f"  existing_start: {existing_start}")
        print(f"  existing_end_str: {existing_end_str}")
        
        if existing_end_str == existing_event.get('time', '12:00 AM'):
            # No end time specified, assume 2-hour duration
            existing_end = existing_start.replace(hour=(existing_start.hour + 2) % 24)
            print(f"  No end time - assuming 2-hour duration")
        else:
            existing_end = datetime.strptime(existing_end_str, "%I:%M %p")
            print(f"  Using explicit end time")
        
        print(f"  existing_end: {existing_end}")
        
        # Parse new event start time
        start_dt = datetime.strptime(new_start_time, "%I:%M %p")
        print(f"  start_dt: {start_dt}")
        
        # Check for overlap
        overlap_condition = existing_start <= start_dt < existing_end
        print(f"\nOverlap Check:")
        print(f"  Condition: {existing_start} <= {start_dt} < {existing_end}")
        print(f"  Result: {overlap_condition}")
        
        if overlap_condition:
            print(f"  X BLOCKED - Event would overlap")
        else:
            print(f"  O ALLOWED - No overlap detected")
            
    else:
        print(f"\n- Different day or different host - no overlap check needed")

if __name__ == "__main__":
    test_user_scenario()
