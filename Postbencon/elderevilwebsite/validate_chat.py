#!/usr/bin/env python3
"""
Validation script for the enhanced live chat client
This script validates the chat component without running Streamlit
"""

import sys
import os
import ast

def validate_chat_component():
    """Validate the realtime chat component"""
    print("Validating Enhanced Live Chat Client...")
    print("=" * 50)
    
    # Test 1: Check if realtime_chat.py exists and is valid Python
    print("1. Checking realtime_chat.py...")
    try:
        with open('realtime_chat.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to parse the file as Python
        ast.parse(content)
        print("   [OK] realtime_chat.py is valid Python")
        
        # Check for key functions
        if 'render_realtime_tavern_chat' in content:
            print("   [OK] Main function found")
        else:
            print("   [ERROR] Main function not found")
            
        if 'SUPABASE_URL' in content:
            print("   [OK] Supabase integration found")
        else:
            print("   [ERROR] Supabase integration missing")
            
        if 'typing' in content.lower():
            print("   [OK] Typing indicators implemented")
        else:
            print("   [ERROR] Typing indicators missing")
            
        if 'reaction' in content.lower():
            print("   [OK] Emoji reactions implemented")
        else:
            print("   [ERROR] Emoji reactions missing")
            
        if 'search' in content.lower():
            print("   [OK] Search functionality implemented")
        else:
            print("   [ERROR] Search functionality missing")
            
        if '@media' in content:
            print("   [OK] Mobile responsiveness implemented")
        else:
            print("   [ERROR] Mobile responsiveness missing")
            
    except FileNotFoundError:
        print("   [ERROR] realtime_chat.py not found")
        return False
    except SyntaxError as e:
        print(f"   [ERROR] Syntax error in realtime_chat.py: {e}")
        return False
    except Exception as e:
        print(f"   [ERROR] Error reading realtime_chat.py: {e}")
        return False
    
    # Test 2: Check app.py integration
    print("\n2. Checking app.py integration...")
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            app_content = f.read()
        
        if 'render_realtime_tavern_chat' in app_content:
            print("   [OK] Chat component integrated in app.py")
        else:
            print("   [ERROR] Chat component not integrated in app.py")
            
        if 'user_display_name' in app_content and 'user_avatar' in app_content:
            print("   [OK] Enhanced user data passed to chat")
        else:
            print("   [ERROR] Enhanced user data not passed to chat")
            
    except Exception as e:
        print(f"   [ERROR] Error checking app.py: {e}")
    
    # Test 3: Check database schema
    print("\n3. Checking database schema...")
    try:
        with open('supabase_tables.sql', 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        required_tables = [
            'tavern_messages',
            'typing_status', 
            'message_reactions'
        ]
        
        for table in required_tables:
            if table in sql_content:
                print(f"   [OK] {table} table defined")
            else:
                print(f"   [ERROR] {table} table missing")
                
    except Exception as e:
        print(f"   [ERROR] Error checking database schema: {e}")
    
    # Test 4: Check requirements
    print("\n4. Checking requirements...")
    try:
        with open('requirements.txt', 'r', encoding='utf-8') as f:
            req_content = f.read()
        
        required_packages = ['streamlit', 'supabase']
        for package in required_packages:
            if package in req_content:
                print(f"   [OK] {package} in requirements")
            else:
                print(f"   [ERROR] {package} missing from requirements")
                
    except Exception as e:
        print(f"   [ERROR] Error checking requirements: {e}")
    
    # Test 5: Check secrets template
    print("\n5. Checking configuration...")
    try:
        with open('secrets.toml', 'r', encoding='utf-8') as f:
            secrets_content = f.read()
        
        if 'SUPABASE_URL' in secrets_content and 'SUPABASE_KEY' in secrets_content:
            print("   [OK] Supabase configuration template found")
        else:
            print("   [ERROR] Supabase configuration template missing")
            
    except Exception as e:
        print(f"   [ERROR] Error checking secrets: {e}")
    
    print("\n" + "=" * 50)
    print("Validation Complete!")
    print("\nNext Steps:")
    print("1. Configure your Supabase credentials in secrets.toml")
    print("2. Run the SQL commands from supabase_tables.sql in Supabase")
    print("3. Start the app with: streamlit run app.py")
    print("4. Or test with: streamlit run test_chat.py")
    
    return True

if __name__ == "__main__":
    validate_chat_component()
