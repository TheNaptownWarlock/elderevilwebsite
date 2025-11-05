# Recursion Detection System Analysis

## What Was Added

I've added a comprehensive recursion detection and stack inspection system to your Streamlit app without changing its functionality. Here's what the system does:

### 1. Core Monitoring Functions

- **`log_function_call()`**: Tracks every function call with timestamp, caller info, and stack depth
- **`check_recursion_pattern()`**: Detects if a function is called more than 5 times in 5 seconds
- **`emergency_recursion_check()`**: Monitors overall stack depth and exits if it exceeds 100 frames
- **`get_detailed_stack_trace()`**: Provides detailed stack traces with file names and line numbers

### 2. Recursion Guards

Added `@recursion_guard` decorators to key functions that might cause recursion:

- `sync_session_with_db()`
- `load_users_from_db()`
- `load_events_from_db()`
- `refresh_data()`
- `rsvp_to_event()`
- `register_user()`

### 3. Streamlit Function Monitoring

- Monitors `st.rerun()` calls to prevent infinite rerun loops
- Blocks recursive calls to `st.rerun()` and `st.experimental_rerun()`
- Logs when these functions are called and from where

### 4. Real-time Debug Interface

Added a debug panel at the bottom of each page that shows:
- Most frequently called functions
- Current stack depth with color-coded warnings
- Current call stack (top 10 frames)
- Session state debug information
- Recursion detection status

## How to Use

1. **Run your app normally** - the system works in the background
2. **Check the debug panel** at the bottom of any page to see function call statistics
3. **Look for warnings** in the console output - the system prints detailed logs
4. **Monitor for recursion alerts** - blocked recursive calls will be logged

## Console Output

The system provides detailed console logging:
- `🔍 RECURSION DETECTION SYSTEM INITIALIZED` when the system starts
- `🔄 function_name: Starting...` when monitored functions are called  
- `🚨 RECURSION ALERT: Function 'X' called Y times in 5 seconds!` when recursion is detected
- `🛑 BLOCKING RECURSIVE st.rerun() CALL!` when infinite rerun loops are prevented

## Key Safety Features

1. **Automatic Blocking**: Functions called too frequently are automatically blocked
2. **Stack Depth Monitoring**: Deep call stacks trigger warnings and emergency exits
3. **Detailed Logging**: Every function call is logged with context
4. **Session State Tracking**: Changes to session state are monitored
5. **Graceful Degradation**: If recursion is detected, the system continues but blocks problematic calls

## What to Look For

### In Console Output:
- High frequency calls to the same function
- Deep stack warnings (>30 frames)
- Blocked function calls

### In Debug Panel:
- Red indicators (🔴) next to function names indicate high call frequency
- Stack depth warnings
- Recursion detection alerts

## Common Recursion Patterns

The system will help you identify these common Streamlit recursion issues:

1. **Infinite Rerun Loops**: `st.rerun()` called in response to state changes that trigger more reruns
2. **Database Sync Loops**: Database loading functions calling each other recursively
3. **Event Handler Cascades**: UI events triggering other events in a loop
4. **Session State Feedback**: State changes triggering functions that change more state

## Next Steps

1. Run your app and watch the console output
2. Interact with the app normally to trigger the recursion
3. Check the debug panel for high-frequency function calls
4. Look for blocked function calls in the logs
5. Use the stack trace information to identify the exact source of recursion

The system will help you pinpoint exactly which functions are causing problems and where they're being called from, making it much easier to fix the recursion issues.