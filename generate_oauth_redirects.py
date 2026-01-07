#!/usr/bin/env python3
"""
Generate OAuth Redirect URIs for Google Cloud Console

This script generates all the redirect URIs you need to add to your Google Cloud Console
for OAuth to work on different ports.
"""

def generate_redirect_uris():
    """Generate redirect URIs for common development ports."""
    
    # Common Streamlit ports
    ports = [8501, 8502, 8503, 8504, 8505, 8506, 8507, 8508, 8509, 8510]
    
    print("🔗 OAuth Redirect URIs for Google Cloud Console")
    print("=" * 50)
    print()
    print("Copy and paste these URIs into your Google Cloud Console:")
    print("(APIs & Services → Credentials → OAuth 2.0 Client ID → Authorized redirect URIs)")
    print()
    
    for port in ports:
        print(f"http://localhost:{port}")
    
    print()
    print("📋 Instructions:")
    print("1. Go to https://console.cloud.google.com/")
    print("2. Select your project")
    print("3. Navigate to APIs & Services → Credentials")
    print("4. Find your OAuth 2.0 Client ID and click edit (pencil icon)")
    print("5. In 'Authorized redirect URIs' section, add all the URIs above")
    print("6. Click Save")
    print("7. Wait 2-3 minutes for changes to propagate")
    print()
    print("✅ After adding these URIs, OAuth will work on any port from 8501-8510")

if __name__ == "__main__":
    generate_redirect_uris()
