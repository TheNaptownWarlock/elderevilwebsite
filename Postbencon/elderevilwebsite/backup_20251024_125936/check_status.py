#!/usr/bin/env python3
"""
Check the status of the Streamlit apps
"""

import subprocess
import sys
import time

def check_port(port):
    """Check if a port is in use"""
    try:
        result = subprocess.run(['netstat', '-an'], capture_output=True, text=True)
        return f":{port}" in result.stdout
    except:
        return False

def main():
    print("Checking Streamlit App Status...")
    print("=" * 40)
    
    # Check ports
    port_8501 = check_port(8501)
    port_8502 = check_port(8502)
    
    print(f"Port 8501 (main app): {'[RUNNING]' if port_8501 else '[NOT RUNNING]'}")
    print(f"Port 8502 (test app): {'[RUNNING]' if port_8502 else '[NOT RUNNING]'}")
    
    if port_8501:
        print("\nMain app should be available at: http://localhost:8501")
    if port_8502:
        print("Test app should be available at: http://localhost:8502")
    
    if not port_8501 and not port_8502:
        print("\nNo Streamlit apps detected. Try running:")
        print("  .venv\\Scripts\\python.exe -m streamlit run app.py --server.port 8501")
        print("  .venv\\Scripts\\python.exe -m streamlit run test_chat.py --server.port 8502")
    
    print("\n" + "=" * 40)
    print("Testing Complete!")

if __name__ == "__main__":
    main()

