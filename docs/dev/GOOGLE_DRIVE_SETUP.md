# Google Drive Setup Guide

This guide explains how to connect the app to Google Drive for uploading generated reports. Two auth modes are supported:

- **Shared OAuth Client (Recommended)** – Single JSON file for all users; each user signs in once
- User OAuth (Desktop) – good for local development; prompts you to sign in once
- Service Account – best for servers/CI; no interactive login

## 🎯 **Recommended: Shared OAuth Client for All Users**

### **Why Use Shared OAuth Client?**

- ✅ **Single setup** - You create one OAuth client, all users use it
- ✅ **No user setup** - Users just click "Connect" and sign in
- ✅ **Production ready** - Perfect for end-user applications
- ✅ **Simplified UX** - No JSON uploads or complex setup for users

### **Setup Process (One-time for you):**

1. **Create OAuth Client** (you do this once)
   - Follow steps 1-6 in "Option A" below
   - Download the `client_secret.json` file
   - Place it in `config/credentials/client_secret.json` in your app

2. **Publish OAuth App** (for production)
   - Go to "OAuth consent screen" → "Publishing status"
   - Click "Publish App" to remove user limits
   - This allows unlimited users to use your app

3. **Users just connect** (no setup needed)
   - Users click "Connect Google Drive" in the app
   - Browser opens for Google sign-in
   - User authorizes the app once
   - Done! Reports upload to their Drive

### **User Experience:**
```
User clicks "Connect Google Drive" 
→ Browser opens for Google sign-in
→ User authorizes "Stock Analysis Tool"
→ Connected! Reports upload automatically
```

### **📅 Date-Based Folder Organization**

**New Feature:** Users can now organize reports by date automatically!

**How it works:**
1. **Select base folder** - Choose your main Google Drive folder
2. **Enable date folders** - Check "📅 Create date-based subfolders"
3. **Automatic organization** - Reports are uploaded to date folders like:
   ```
   Your Drive Folder/
   ├── 2025-08-08/
   │   ├── AAPL_analysis.xlsx
   │   ├── AAPL_analysis.docx
   │   ├── GOOGL_analysis.xlsx
   │   └── GOOGL_analysis.docx
   ├── 2025-08-09/
   │   ├── MSFT_analysis.xlsx
   │   └── MSFT_analysis.docx
   └── 2025-08-10/
       ├── TSLA_analysis.xlsx
       └── TSLA_analysis.docx
   ```

**Benefits:**
- ✅ **Automatic organization** - No manual folder creation needed
- ✅ **Date-based sorting** - Easy to find reports by date
- ✅ **Clean structure** - Each day's analysis in its own folder
- ✅ **Scalable** - Works for any number of reports

**Usage:**
1. Go to "🔗 Google Drive Setup"
2. Enter your Drive folder ID
3. Check "📅 Create date-based subfolders"
4. Click "Connect Google Drive"
5. Run analysis - reports automatically go to date folders!

### **💾 Persistent Authentication & Settings**

**New Feature:** One-time setup, automatic reuse!

**How it works:**
1. **First time setup** - Connect to Google Drive once
2. **Settings saved** - Folder ID and preferences are stored
3. **Automatic reuse** - No need to re-authenticate or re-select folders
4. **Easy changes** - Modify settings anytime via "⚙️ Change Settings"

**Benefits:**
- ✅ **One-time setup** - Configure once, use forever
- ✅ **No re-authentication** - Credentials saved securely
- ✅ **Persistent settings** - Folder ID and date folder preference remembered
- ✅ **Easy management** - Change settings or disconnect anytime

**User Experience:**
```
First Run:
1. Go to "🔗 Google Drive Setup"
2. Enter folder ID and preferences
3. Click "Connect Google Drive"
4. ✅ Settings saved!

Subsequent Runs:
1. Go to "🔗 Google Drive Setup"
2. See "✅ Google Drive is already configured!"
3. Run analysis directly - no setup needed!

To Change Settings:
1. Go to "🔗 Google Drive Setup"
2. Click "⚙️ Change Settings"
3. Modify folder ID or date folder preference
4. Click "💾 Save Changes"

To Disconnect:
1. Go to "🔗 Google Drive Setup"
2. Click "🔌 Disconnect Google Drive"
3. All settings cleared
```

**Technical Details:**
- **Credentials saved:** `config/credentials/gdrive_token.json`
- **Settings saved:** `config/credentials/gdrive_settings.json`
- **Automatic refresh:** Tokens refreshed automatically when expired
- **Secure storage:** Settings stored locally in JSON format

---

## 1) Prerequisites

- Make sure dependencies are installed (already in `requirements.txt`):
  - `google-auth`, `google-auth-oauthlib`, `google-auth-httplib2`, `google-api-python-client`, `pydrive2`

## 2) Enable Google Drive API

1. Open the Google Cloud Console (`https://console.cloud.google.com/`)
2. Create/select a project
3. Go to "APIs & Services" → "Library" → enable "Google Drive API"

## 3) OAuth Consent Screen

1. Go to "APIs & Services" → "OAuth consent screen"
2. Choose "External" (or "Internal" for Workspace), fill in required fields
3. Add scopes (recommended minimal scope):
   - `https://www.googleapis.com/auth/drive.file`

## 4) Option A – User OAuth (Desktop App)

### Step-by-Step OAuth Client JSON Download

1. **Go to Google Cloud Console**
   - Open [Google Cloud Console](https://console.cloud.google.com/)
   - Sign in with your Google account

2. **Create or Select a Project**
   - Click on the project dropdown at the top
   - Click "New Project" or select an existing one
   - Give it a name like "Stock Analysis Tool"

3. **Enable Google Drive API**
   - In the left sidebar, go to "APIs & Services" → "Library"
   - Search for "Google Drive API"
   - Click on it and press "Enable"

4. **Configure OAuth Consent Screen**
   - Go to "APIs & Services" → "OAuth consent screen"
   - Choose "External" (or "Internal" for Google Workspace)
   - Fill in required fields:
     - App name: "Stock Analysis Tool"
     - User support email: your email
     - Developer contact information: your email
   - Click "Save and Continue"
   - On "Scopes" page, click "Add or Remove Scopes"
   - Search for and select: `https://www.googleapis.com/auth/drive.file`
   - Click "Save and Continue"
   - On "Test users" page, add your email if needed
   - Click "Save and Continue"

5. **Create OAuth Client ID**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - Application type: **"Desktop App"**
   - Name: "Stock Analysis Tool Desktop"
   - Click "Create"

6. **Download the JSON File**
   - A popup will appear with your client ID and client secret
   - Click the **"Download JSON"** button
   - Save the file as `client_secret.json`
   - **Important**: Keep this file secure and don't share it

7. **Use in the App**
   - **For shared use**: Place `client_secret.json` in `config/credentials/` folder
   - **For individual use**: Upload via the app's "Google Drive Setup" page
   - Enter your Google Drive folder ID
   - Click "Connect Google Drive"

### What the JSON File Contains

The downloaded `client_secret.json` looks like this:
```json
{
  "installed": {
    "client_id": "your-client-id.apps.googleusercontent.com",
    "project_id": "your-project-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "your-client-secret",
    "redirect_uris": ["http://localhost"]
  }
}
```

### Troubleshooting

- **"OAuth client not found"**: Make sure you downloaded the JSON file, not just copied the client ID
- **"Invalid client"**: Ensure you selected "Desktop App" as the application type
- **"Access blocked"**: Add your email to test users in OAuth consent screen
- **"Scope not allowed"**: Make sure you added `https://www.googleapis.com/auth/drive.file` scope

5. Set environment variables (e.g. in `.env`):

```
GOOGLE_DRIVE_USE_SERVICE_ACCOUNT=false
GOOGLE_DRIVE_CREDENTIALS_FILE=config/credentials/client_secret.json
GOOGLE_DRIVE_FOLDER_ID=<your_drive_folder_id>
GOOGLE_DRIVE_SCOPES=https://www.googleapis.com/auth/drive.file
```

6. On first run, a browser window will open to complete the sign-in; a local token file will be created for subsequent runs.

Minimal upload example (OAuth):

```python
import os
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

gauth = GoogleAuth()
gauth.LoadClientConfigFile(os.getenv("GOOGLE_DRIVE_CREDENTIALS_FILE"))
gauth.LocalWebserverAuth()  # prompts one-time login

drive = GoogleDrive(gauth)
folder_id = os.environ["GOOGLE_DRIVE_FOLDER_ID"]

f = drive.CreateFile({
    "title": "report.xlsx",
    "parents": [{"id": folder_id}],
})
f.SetContentFile("path/to/report.xlsx")
f.Upload()
```

## 5) Option B – Service Account (Headless)

1. "IAM & Admin" → "Service Accounts" → "Create Service Account"
2. Create a JSON key; download it
3. Save it to a secure location, e.g. `config/credentials/service_account.json`
4. Share the target Drive folder with the service account email (shows like `<name>@<project>.iam.gserviceaccount.com`)
   - For Shared Drives, add the service account as "Content manager"
5. Set environment variables:

```
GOOGLE_DRIVE_USE_SERVICE_ACCOUNT=true
GOOGLE_APPLICATION_CREDENTIALS=config/credentials/service_account.json
GOOGLE_DRIVE_FOLDER_ID=<your_drive_folder_id>
GOOGLE_DRIVE_SCOPES=https://www.googleapis.com/auth/drive.file
```

Minimal upload example (Service Account):

```python
import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = [os.getenv("GOOGLE_DRIVE_SCOPES", "https://www.googleapis.com/auth/drive.file")] 
creds = Credentials.from_service_account_file(
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"], scopes=SCOPES
)
service = build("drive", "v3", credentials=creds)

folder_id = os.environ["GOOGLE_DRIVE_FOLDER_ID"]
file_path = "path/to/report.xlsx"

file_metadata = {"name": "report.xlsx", "parents": [folder_id]}
media = MediaFileUpload(
    file_path,
    mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    resumable=True,
)
service.files().create(body=file_metadata, media_body=media, fields="id").execute()
```

## 6) How to find the Folder ID

- Open the folder in Drive; the URL looks like `https://drive.google.com/drive/folders/<FOLDER_ID>` – copy the `<FOLDER_ID>`

## 7) Recommended .env keys

```
# Choose one auth mode
GOOGLE_DRIVE_USE_SERVICE_ACCOUNT=false

# OAuth mode
GOOGLE_DRIVE_CREDENTIALS_FILE=config/credentials/client_secret.json

# Service Account mode
GOOGLE_APPLICATION_CREDENTIALS=config/credentials/service_account.json

# Common
GOOGLE_DRIVE_FOLDER_ID=<your_drive_folder_id>
GOOGLE_DRIVE_SCOPES=https://www.googleapis.com/auth/drive.file
```

## 8) Security Notes

- Never commit credentials JSON files to git
- Add `config/credentials/*.json` to `.gitignore`
- Restrict Drive scopes to the minimum required (`drive.file` is usually enough)

