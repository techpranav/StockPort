# ☁️ Streamlit Cloud Deployment Guide

This guide explains how to deploy the Stock Analysis Tool on Streamlit Cloud with proper Google Drive integration for multiple users.

## 🎯 Why Streamlit Cloud?

**Streamlit Cloud** provides:
- ✅ **Multi-user access** - Each user gets their own isolated session
- ✅ **No server management** - Fully managed by Streamlit
- ✅ **Automatic scaling** - Handles multiple concurrent users
- ✅ **Secure isolation** - Each user's data is completely separate
- ✅ **Easy deployment** - Connect your GitHub repository and deploy

## 🚀 Quick Deployment Steps

### 1. Prepare Your Repository

**Remove hardcoded credentials:**
```bash
# Remove these files from your repository
config/credentials/client_secret.json
config/credentials/service_account.json
.env
```

**Update .gitignore:**
```gitignore
# Credentials and secrets
config/credentials/
.env
*.json
!package.json
!requirements.txt

# User-specific data
output/
reports/
logs/
venv/
__pycache__/
*.pyc
```

### 2. Deploy to Streamlit Cloud

1. **Go to [share.streamlit.io](https://share.streamlit.io)**
2. **Sign in with GitHub**
3. **Click "New app"**
4. **Select your repository**
5. **Set main file path:** `ui/pages/main_page.py`
6. **Click "Deploy!"**

## 🔐 Google Drive Configuration for Cloud

### How It Works in Cloud

**Local Deployment:**
- ❌ Credentials stored in files
- ❌ Shared configuration
- ❌ Single user setup

**Streamlit Cloud:**
- ✅ **Per-user OAuth setup**
- ✅ **Session-based storage**
- ✅ **No credential files**
- ✅ **Automatic isolation**

### User Experience

1. **User visits your app**
2. **Clicks "Google Drive Setup"**
3. **Pastes their OAuth credentials**
4. **Configures their folder ID**
5. **Settings stored in their session**
6. **Reports upload automatically**

## 📋 Required Changes for Cloud

### 1. Update Main Page

The main page now automatically detects cloud vs local environment:

```python
def render_google_drive_setup():
    """Render appropriate Google Drive setup based on environment."""
    
    # Check if we're in a cloud environment
    is_cloud = (
        "STREAMLIT_SERVER_RUNNING" in os.environ or
        "STREAMLIT_CLOUD" in os.environ or
        "STREAMLIT_SHARING" in os.environ or
        os.path.exists("/app/.streamlit/")
    )
    
    if is_cloud:
        # Use cloud setup (per-user OAuth)
        render_cloud_google_drive_setup()
    else:
        # Use local setup (file-based)
        render_google_drive_setup()
```

### 2. Cloud Google Drive Manager

New manager that stores settings per user:

```python
class CloudGoogleDriveManager:
    """Google Drive manager for Streamlit Cloud."""
    
    def __init__(self):
        self.user_settings = UserSettingsManager()  # Session-based
        # ... rest of implementation
```

### 3. User Settings Manager

Stores all user preferences in Streamlit session state:

```python
class UserSettingsManager:
    """Manages user-specific settings in session state."""
    
    def __init__(self):
        self._init_session_state()
    
    def _init_session_state(self):
        if 'google_drive_configured' not in st.session_state:
            st.session_state.google_drive_configured = False
        # ... more settings
```

## 🔧 Cloud Configuration

### Environment Variables

**Streamlit Cloud Secrets:**
```toml
# .streamlit/secrets.toml
_is_cloud = true
```

**Or use environment detection:**
```python
def is_cloud_environment():
    return (
        "STREAMLIT_SERVER_RUNNING" in os.environ or
        "STREAMLIT_CLOUD" in os.environ or
        "STREAMLIT_SHARING" in os.environ or
        os.path.exists("/app/.streamlit/")
    )
```

### Cloud Settings

Use the unified configuration in `config/app_config.py`. In cloud, OAuth is used by default and user-specific Drive settings are handled in the UI.

Environment variables supported:

```
GOOGLE_DRIVE_USE_SERVICE_ACCOUNT=false
GOOGLE_DRIVE_SCOPES=https://www.googleapis.com/auth/drive.file
# Optional default folder (users can override in UI)
GOOGLE_DRIVE_FOLDER_ID=
```

## 📱 User Setup Process

### For End Users

1. **Visit your Streamlit Cloud app**
2. **Click "☁️ Google Drive Setup" in sidebar**
3. **Choose setup method:**
   - **🔑 OAuth Setup (Recommended)** - Full automation
   - **📁 Manual Setup** - Just store folder ID

### OAuth Setup (Recommended)

1. **Get OAuth credentials:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create project and enable Drive API
   - Create OAuth 2.0 credentials (Desktop app)
   - Download JSON file

2. **Paste credentials:**
   - Copy entire JSON content
   - Paste in the app's OAuth field
   - Test connection

3. **Configure folder:**
   - Enter your Google Drive folder ID
   - Choose date folder preference
   - Save configuration

### Manual Setup

1. **Find your folder ID:**
   - Go to [Google Drive](https://drive.google.com)
   - Navigate to target folder
   - Copy ID from URL: `.../folders/FOLDER_ID_HERE`

2. **Enter folder ID:**
   - Paste in the app
   - Choose date folder preference
   - Save configuration

## 🔒 Security Features

### User Isolation

- ✅ **Session-based storage** - No cross-user data access
- ✅ **OAuth tokens** - Stored per user session
- ✅ **Folder permissions** - Users only access their own folders
- ✅ **No credential files** - Nothing stored on server

### Data Privacy

- ✅ **No data sharing** between users
- ✅ **Temporary credentials** - Only in memory
- ✅ **Secure OAuth flow** - Google handles authentication
- ✅ **Session expiration** - Settings clear when session ends

## 📊 Benefits for Users

### Individual Control

- **Personal Google Drive** - Each user connects their own account
- **Custom folders** - Users choose their upload location
- **Personal settings** - Date folders, preferences, etc.
- **No conflicts** - Multiple users can use the app simultaneously

### Easy Setup

- **One-time configuration** - Set up once, works forever
- **No technical knowledge** - Simple copy-paste process
- **Automatic uploads** - Reports go to Drive automatically
- **Easy changes** - Modify settings anytime

## 🆘 Troubleshooting

### Common Issues

**"OAuth credentials not working"**
- Check JSON format (must be valid JSON)
- Ensure Drive API is enabled in Google Cloud
- Verify OAuth client type is "Desktop application"

**"Can't access folder"**
- Check folder ID is correct
- Ensure folder exists and is accessible
- Verify Google account has Drive access

**"Settings not saving"**
- Check if you're in a cloud environment
- Try refreshing the page
- Clear browser cache and cookies

### Support

1. **Check the help section** in the app
2. **Verify Google Cloud setup**
3. **Test with a simple folder first**
4. **Contact support** with specific error messages

## 🎉 Deployment Complete!

Your Stock Analysis Tool is now:
- ✅ **Deployed on Streamlit Cloud**
- ✅ **Multi-user ready**
- ✅ **Secure Google Drive integration**
- ✅ **No credential management needed**
- ✅ **Professional deployment**

**Users can now:**
1. Visit your app URL
2. Set up their own Google Drive
3. Analyze stocks with automatic uploads
4. Access their reports from anywhere

## 🔗 Useful Links

- **Streamlit Cloud:** [share.streamlit.io](https://share.streamlit.io)
- **Google Cloud Console:** [console.cloud.google.com](https://console.cloud.google.com)
- **Google Drive API:** [developers.google.com/drive](https://developers.google.com/drive)
- **OAuth 2.0 Guide:** [developers.google.com/identity/protocols/oauth2](https://developers.google.com/identity/protocols/oauth2)

---

**Happy Cloud Deployment! ☁️🚀**
