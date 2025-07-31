#!/usr/bin/env python3
"""
Simple script to update Google OAuth credentials in start_server_step3_google_fixed.py
"""

import re

def update_google_credentials():
    """Update Google OAuth credentials in the server file"""
    
    print("🔧 Google OAuth Credentials Updater")
    print("=" * 50)
    
    # Get credentials from user
    print("\n📝 Please enter your Google OAuth credentials:")
    client_id = input("Google Client ID: ").strip()
    client_secret = input("Google Client Secret: ").strip()
    
    if not client_id or not client_secret:
        print("❌ Error: Both Client ID and Client Secret are required!")
        return False
    
    # Read the server file
    try:
        with open('start_server_step3_google_fixed.py', 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ Error: start_server_step3_google_fixed.py not found!")
        return False
    
    # Replace the credentials
    content = re.sub(
        r"GOOGLE_CLIENT_ID = 'YOUR_GOOGLE_CLIENT_ID_HERE'",
        f"GOOGLE_CLIENT_ID = '{client_id}'",
        content
    )
    
    content = re.sub(
        r"GOOGLE_CLIENT_SECRET = 'YOUR_GOOGLE_CLIENT_SECRET_HERE'",
        f"GOOGLE_CLIENT_SECRET = '{client_secret}'",
        content
    )
    
    # Write back to file
    try:
        with open('start_server_step3_google_fixed.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("\n✅ Successfully updated Google OAuth credentials!")
        print("🔄 Please restart the server to apply changes.")
        return True
    except Exception as e:
        print(f"❌ Error writing file: {e}")
        return False

if __name__ == '__main__':
    update_google_credentials()