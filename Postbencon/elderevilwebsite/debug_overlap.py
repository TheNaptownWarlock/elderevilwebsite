#!/usr/bin/env python3
"""
Debug script to test overlap detection logic
"""

from datetime import datetime

def test_overlap_detection():
    """Test the overlap detection logic with various scenarios"""
    
    print("Testing Overlap Detection Logic")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        {
            "name": "Existing: 9:00 AM - 9:00 AM, New: 10:00 AM",
            "existing_start": "9:00 AM",
            "existing_end": "9:00 AM", 
            "new_start": "10:00 AM",
            "expected": "ALLOWED"
        },
        {
            "name": "Existing: 9:00 AM - 10:00 AM, New: 10:00 AM",
            "existing_start": "9:00 AM",
            "existing_end": "10:00 AM",
            "new_start": "10:00 AM", 
            "expected": "ALLOWED"
        },
        {
            "name": "Existing: 9:00 AM - 10:00 AM, New: 9:30 AM",
            "existing_start": "9:00 AM",
            "existing_end": "10:00 AM",
            "new_start": "9:30 AM",
            "expected": "BLOCKED"
        },
        {
            "name": "Existing: 9:00 AM - 10:00 AM, New: 8:30 AM",
            "existing_start": "9:00 AM",
            "existing_end": "10:00 AM", 
            "new_start": "8:30 AM",
            "expected": "ALLOWED"
        },
        {
            "name": "Existing: 9:00 AM - 10:00 AM, New: 10:30 AM",
            "existing_start": "9:00 AM",
            "existing_end": "10:00 AM",
            "new_start": "10:30 AM",
            "expected": "ALLOWED"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_case['name']}")
        print("-" * 40)
        
        # Parse times
        existing_start = datetime.strptime(test_case['existing_start'], "%I:%M %p")
        existing_end = datetime.strptime(test_case['existing_end'], "%I:%M %p")
        new_start = datetime.strptime(test_case['new_start'], "%I:%M %p")
        
        print(f"Existing Event: {test_case['existing_start']} - {test_case['existing_end']}")
        print(f"New Event Start: {test_case['new_start']}")
        print(f"Parsed Times:")
        print(f"  existing_start: {existing_start}")
        print(f"  existing_end: {existing_end}")
        print(f"  new_start: {new_start}")
        
        # Test the overlap condition
        overlap_condition = existing_start <= new_start < existing_end
        print(f"Overlap Condition: {existing_start} <= {new_start} < {existing_end}")
        print(f"Result: {overlap_condition}")
        
        # Determine if blocked or allowed
        if overlap_condition:
            result = "BLOCKED"
        else:
            result = "ALLOWED"
            
        print(f"Expected: {test_case['expected']}")
        print(f"Actual: {result}")
        
        if result == test_case['expected']:
            print("PASS")
        else:
            print("FAIL")
            
        print()

def test_supabase_field_mapping():
    """Test how Supabase fields map to our logic"""
    
    print("\nTesting Supabase Field Mapping")
    print("=" * 50)
    
    # Simulate what we get from Supabase
    supabase_event = {
        "id": "test-123",
        "title": "Test Event",
        "date": "Thursday",
        "time": "9:00 AM",  # This is the start time
        "end_time": "10:00 AM",  # This is the end time
        "host_email": "test@example.com",
        "creator_email": "test@example.com"
    }
    
    print("Supabase Event Data:")
    for key, value in supabase_event.items():
        print(f"  {key}: {value}")
    
    print("\nField Mapping:")
    print(f"  start: {supabase_event.get('start', 'NOT FOUND')}")
    print(f"  end_time: {supabase_event.get('end_time', 'NOT FOUND')}")
    print(f"  time: {supabase_event.get('time', 'NOT FOUND')}")
    
    # Test the fallback logic
    existing_start_str = supabase_event.get('start', supabase_event.get('time', '12:00 AM'))
    existing_end_str = supabase_event.get('end_time', supabase_event.get('time', '12:00 AM'))
    
    print(f"\nFallback Logic:")
    print(f"  existing_start_str: {existing_start_str}")
    print(f"  existing_end_str: {existing_end_str}")
    
    # Parse the times
    existing_start = datetime.strptime(existing_start_str, "%I:%M %p")
    existing_end = datetime.strptime(existing_end_str, "%I:%M %p")
    
    print(f"  existing_start: {existing_start}")
    print(f"  existing_end: {existing_end}")
    
    # Test with a new event
    new_start = datetime.strptime("10:00 AM", "%I:%M %p")
    overlap_condition = existing_start <= new_start < existing_end
    
    print(f"\nTesting new event at 10:00 AM:")
    print(f"  Overlap condition: {overlap_condition}")
    print(f"  Result: {'BLOCKED' if overlap_condition else 'ALLOWED'}")

if __name__ == "__main__":
    test_overlap_detection()
    test_supabase_field_mapping()
