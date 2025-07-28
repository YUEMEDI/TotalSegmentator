#!/usr/bin/env python3
"""
Google OAuth Configuration Checker for YueTransfer
This script helps verify your Google OAuth setup
"""

import requests
import json

def check_google_oauth_config():
    """Check if Google OAuth is properly configured"""
    
    print("🔍 Google OAuth Configuration Checker")
    print("=" * 50)
    
    # Read the current configuration from the server file
    try:
        with open('start_server_step3_google_fixed.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract Google OAuth configuration
        lines = content.split('\n')
        client_id = None
        client_secret = None
        
        for line in lines:
            if 'GOOGLE_CLIENT_ID =' in line:
                client_id = line.split('=')[1].strip().strip('"').strip("'")
            elif 'GOOGLE_CLIENT_SECRET =' in line:
                client_secret = line.split('=')[1].strip().strip('"').strip("'")
        
        print(f"📋 Current Configuration:")
        print(f"   Client ID: {client_id}")
        print(f"   Client Secret: {client_secret[:10]}..." if client_secret and len(client_secret) > 10 else f"   Client Secret: {client_secret}")
        
        # Check for placeholder values
        if "YOUR_GOOGLE_CLIENT_ID_HERE" in client_id or "YOUR_GOOGLE_CLIENT_SECRET_HERE" in client_secret:
            print("\n❌ ERROR: You still have placeholder values!")
            print("   Please follow the setup guide to get real credentials.")
            print("   Current values:")
            print(f"   - Client ID: {client_id}")
            print(f"   - Client Secret: {client_secret}")
            return False
            
        if not client_id or not client_secret:
            print("\n❌ ERROR: Missing Google OAuth credentials!")
            return False
            
        print("\n✅ Configuration looks good!")
        
        # Test the redirect URI
        redirect_uri = "http://localhost:5000/login/google/authorized"
        print(f"\n🔗 Redirect URI: {redirect_uri}")
        
        # Provide next steps
        print("\n📝 Next Steps:")
        print("1. Make sure these URLs are added to Google Cloud Console:")
        print("   - Authorized JavaScript origins:")
        print("     * http://localhost:5000")
        print("     * http://127.0.0.1:5000")
        print("   - Authorized redirect URIs:")
        print("     * http://localhost:5000/login/google/authorized")
        print("     * http://127.0.0.1:5000/login/google/authorized")
        print("\n2. Run: start_google_oauth_fixed.bat")
        print("3. Test login at: http://localhost:5000")
        
        return True
        
    except FileNotFoundError:
        print("❌ ERROR: start_server_step3_google_fixed.py not found!")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    check_google_oauth_config() 