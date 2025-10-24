#!/usr/bin/env python3
"""
Debug script to check what secrets are available
"""

import streamlit as st

def main():
    st.title("Debug Secrets")
    
    st.write("All secrets:")
    try:
        for key, value in st.secrets.items():
            if isinstance(value, str) and len(value) > 20:
                st.write(f"{key}: {value[:20]}...")
            else:
                st.write(f"{key}: {value}")
    except Exception as e:
        st.error(f"Error reading secrets: {e}")
    
    st.write("\nSpecific checks:")
    st.write(f"SUPABASE_URL: {st.secrets.get('SUPABASE_URL', 'NOT FOUND')}")
    st.write(f"SUPABASE_KEY: {st.secrets.get('SUPABASE_KEY', 'NOT FOUND')}")
    
    # Try different ways to access
    try:
        st.write(f"Direct access SUPABASE_URL: {st.secrets['SUPABASE_URL']}")
    except:
        st.write("Direct access SUPABASE_URL: FAILED")
    
    try:
        st.write(f"Direct access SUPABASE_KEY: {st.secrets['SUPABASE_KEY'][:20]}...")
    except:
        st.write("Direct access SUPABASE_KEY: FAILED")

if __name__ == "__main__":
    main()


