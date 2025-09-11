#!/usr/bin/env python3
"""
OAuth Redirect URI Setup Helper

This script generates the redirect URIs you need to add to your OAuth providers.
"""

def generate_redirect_uris():
    """Generate redirect URIs for common Streamlit ports."""
    ports = list(range(8501, 8521))  # Ports 8501-8520
    
    print("🔗 OAuth Redirect URI Setup Helper")
    print("=" * 40)
    print("\n📋 Copy these redirect URIs to your OAuth providers:\n")
    
    print("Google OAuth (Google Cloud Console):")
    print("APIs & Services > Credentials > Your OAuth Client > Authorized redirect URIs")
    print("-" * 60)
    for port in ports:
        print(f"http://localhost:{port}")
    
    print("\nMicrosoft OAuth (Azure Portal):")
    print("Azure Active Directory > App registrations > Your App > Authentication")
    print("-" * 60)
    for port in ports:
        print(f"http://localhost:{port}")
    
    print("\n🌐 For Production (Streamlit Cloud):")
    print("Add your production URL:")
    print("https://your-app-name.streamlit.app")
    
    print("\n📝 Instructions:")
    print("1. Copy the URIs above")
    print("2. Go to your OAuth provider dashboard")
    print("3. Add each URI to the redirect URI list")
    print("4. Save the changes")
    print("5. Test with: streamlit run app.py --server.port 8515")
    
    print("\n✅ After setup, OAuth will work on any port from 8501-8520!")

if __name__ == "__main__":
    generate_redirect_uris()
