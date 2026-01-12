# Settings Persistence Documentation

## Overview

The Stock Analysis Tool implements a robust settings persistence system that works seamlessly in both local and cloud environments. Each user's settings are isolated and persist across app restarts.

## How It Works

### Local Environment
- **Storage**: Settings are saved to a local JSON file (`user_settings.json`)
- **Persistence**: Settings survive app restarts and system reboots
- **User Isolation**: Single-user environment, so all settings belong to the local user

### Cloud Environment (Streamlit Cloud)
- **Storage**: Settings are stored using Streamlit's caching and session state
- **Persistence**: Settings persist within the user's session and across page reruns
- **User Isolation**: Each user gets their own isolated session with unique settings
- **Cache TTL**: Settings are cached for 1 hour to improve performance

## Architecture

### UserSettingsManager
The main class that handles all settings operations:

```python
from utils.user_settings_manager import UserSettingsManager

# Initialize the manager
user_settings = UserSettingsManager()

# Save sidebar configuration
user_settings.save_sidebar_config(config)

# Load sidebar configuration
config = user_settings.load_sidebar_config()
```

### CloudStorage
A helper class for cloud environments that provides:
- User-specific storage using session state
- Caching with TTL (Time To Live)
- Fallback to default settings on errors

## Settings Types

### 1. Sidebar Configuration
- Export options (Word, Excel)
- AI model selection
- Google Drive integration settings
- Analysis parameters (days back, cleanup days, etc.)

### 2. Google Drive Settings
- OAuth credentials
- Folder ID configuration
- Date folder preferences
- Authentication tokens

### 3. User Preferences
- Custom user-specific settings
- Analysis preferences
- UI preferences

## Usage Examples

### Saving Settings
```python
# Sidebar settings are automatically saved when changed
config = {
    'export_word': True,
    'export_excel': False,
    'ai_model': 'gpt-4',
    'days_back': 180
}
user_settings.save_sidebar_config(config)
```

### Loading Settings
```python
# Settings are automatically loaded on app startup
config = user_settings.load_sidebar_config()
export_word = config.get('export_word', True)
```

### Google Drive Settings
```python
# Set Google Drive folder
user_settings.set_google_drive_folder_id('your_folder_id')

# Get Google Drive folder
folder_id = user_settings.get_google_drive_folder_id()

# Check if Google Drive is configured
is_configured = user_settings.is_google_drive_configured()
```

## Environment Detection

The system automatically detects the environment:

```python
def _is_cloud_environment(self) -> bool:
    """Check if we're running in a cloud environment."""
    return (
        "STREAMLIT_SERVER_RUNNING" in os.environ or
        "STREAMLIT_CLOUD" in os.environ or
        "STREAMLIT_SHARING" in os.environ or
        os.path.exists("/app/.streamlit/")
    )
```

## Benefits

### For Local Users
- Settings persist across app restarts
- No internet connection required
- Fast access to settings
- Full control over data

### For Cloud Users
- Settings persist within their session
- User isolation (each user has their own settings)
- No file system dependencies
- Scalable for multiple users

## Future Enhancements

For production cloud deployments, consider:

1. **Database Integration**: Replace the simple caching with a proper database (PostgreSQL, MongoDB, etc.)
2. **User Authentication**: Implement proper user authentication and user IDs
3. **Settings Sync**: Allow users to sync settings across devices
4. **Settings Export/Import**: Allow users to backup and restore their settings
5. **Settings Versioning**: Track changes to settings over time

## Troubleshooting

### Settings Not Persisting
1. Check if the app is running in the correct environment
2. Verify that the settings file exists (local environment)
3. Check for any error messages in the console
4. Try refreshing the page (cloud environment)

### Settings Reset
If settings are reset unexpectedly:
1. Check if the cache has expired (cloud environment)
2. Verify file permissions (local environment)
3. Check for any configuration errors

## Security Considerations

- **Local Environment**: Settings are stored in plain text JSON files
- **Cloud Environment**: Settings are stored in session state (isolated per user)
- **OAuth Credentials**: Should be handled securely and not logged
- **User Data**: Each user's data is isolated in cloud environments

## Performance

- **Local Environment**: File I/O operations (fast)
- **Cloud Environment**: Cached operations with 1-hour TTL (very fast)
- **Memory Usage**: Minimal overhead for both environments
