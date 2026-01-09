# Stockport v4 UI Implementation

## Overview

The UI has been refactored to connect to the Stockport v4 backend via REST API instead of using mock data. The UI is now a proper multi-page application that subscribes to backend state and events.

## Changes Made

### 1. REST API Client (`ui/services/api_client.py`)

Created a new REST API client that:
- Connects to backend REST API (default: `http://localhost:8001`)
- Provides methods for all backend endpoints
- Handles errors gracefully with fallbacks
- Uses session-based HTTP requests with timeout

**Key Methods:**
- `get_status()` - System status
- `get_positions()` - Open positions
- `get_orders()` - Order history
- `get_all_settings()` - All settings
- `update_setting()` - Update a setting
- `get_opportunities()` - Recent opportunities
- `get_signals()` - Recent signals
- `get_strategy_performance()` - Strategy performance
- `get_market_state()` - Market state
- `get_data_health()` - Data health status

### 2. Updated UI Data Service (`ui/services/ui_data_service.py`)

Refactored to use REST API client instead of direct backend component access:
- All methods now use `api_client` instead of direct backend access
- Graceful fallbacks when backend is unavailable
- Error handling and logging

### 3. New v4 Main App (`ui/app_v4.py`)

Created a new multi-page Streamlit application with:
- Sidebar navigation with 6 pages:
  - 📊 Dashboard
  - 🔍 Market Scanner
  - ⚙️ Strategies
  - 💼 Portfolio
  - ⚡ Execution
  - ⚙️ Settings
- System status indicator in sidebar
- Clean, modern UI structure

### 4. Updated Settings Panel (`ui/settings_panel.py`)

Refactored to use REST API:
- Fetches settings via API client
- Updates settings via API
- Real-time updates when settings change
- Export/import functionality

### 5. Updated Main Entry Point (`app.py`)

Changed to use v4 app instead of old analysis tool:
```python
from ui.app_v4 import main
```

## Architecture

```
┌─────────────────────────────────────────┐
│         Streamlit UI (v4)               │
│  ┌───────────────────────────────────┐  │
│  │   UI Components                    │  │
│  │   (dashboard, scanner, etc.)       │  │
│  └──────────────┬────────────────────┘  │
│                 │                        │
│  ┌──────────────▼────────────────────┐  │
│  │   UIDataService                    │  │
│  │   (Unified data access)            │  │
│  └──────────────┬────────────────────┘  │
│                 │                        │
│  ┌──────────────▼────────────────────┐  │
│  │   APIClient                       │  │
│  │   (REST API client)               │  │
│  └──────────────┬────────────────────┘  │
└─────────────────┼───────────────────────┘
                  │ HTTP/REST
┌─────────────────▼───────────────────────┐
│      Backend REST API                    │
│      (http://localhost:8001)             │
└──────────────────────────────────────────┘
```

## Backend API Endpoints Required

The following endpoints need to be implemented in the backend REST API:

### Existing (already in `backend/api/rest_api.py`):
- ✅ `GET /status` - System status
- ✅ `GET /positions` - Get positions
- ✅ `GET /orders` - Get orders
- ✅ `GET /settings` - Get all settings
- ✅ `GET /settings/{key}` - Get setting
- ✅ `PUT /settings/{key}` - Update setting
- ✅ `GET /settings/definitions` - Get setting definitions

### New Endpoints Needed:
- ❌ `GET /capital/overview` - Capital overview
- ❌ `GET /opportunities` - Recent opportunities
- ❌ `GET /signals` - Recent signals
- ❌ `GET /strategies/performance` - Strategy performance
- ❌ `GET /market/state` - Market state
- ❌ `GET /data/health` - Data health status
- ❌ `POST /settings/reset/{key}` - Reset setting to default
- ❌ `POST /settings/reset-all` - Reset all settings

## Usage

### Starting the UI

```bash
streamlit run app.py
```

The UI will:
1. Connect to backend REST API at `http://localhost:8001` (configurable via `STOCKPORT_API_URL` env var)
2. Display system status in sidebar
3. Show real-time data from backend (when available)
4. Fall back gracefully when backend is unavailable

### Backend Connection

The UI expects the backend REST API to be running. To start the backend:

```bash
# Start REST API server
python -m backend.api.rest_api
```

Or use the trading engine which includes the API:

```bash
python -m backend.core.engine
```

## Next Steps

1. **Add Missing API Endpoints**: Implement the new endpoints listed above in `backend/api/rest_api.py`

2. **WebSocket Integration**: Add WebSocket client for real-time updates (currently UI polls via REST)

3. **Update UI Components**: Update dashboard, scanner_view, strategies_panel, portfolio_view, and execution_view to:
   - Use real data from API instead of mock data
   - Handle loading states
   - Show error messages when backend unavailable
   - Add refresh buttons

4. **Error Handling**: Improve error handling and user feedback when:
   - Backend is unavailable
   - API requests fail
   - Data is stale

5. **Real-time Updates**: Implement WebSocket client for:
   - Live opportunity stream
   - Real-time position updates
   - Order status changes
   - Market state changes

## Testing

To test the UI:

1. Start backend REST API server
2. Start Streamlit UI: `streamlit run app.py`
3. Navigate through pages
4. Verify data loads from backend
5. Test settings updates
6. Verify error handling when backend is down

## Notes

- The UI gracefully handles backend unavailability
- Mock data is still used as fallback in some components (needs to be removed)
- Settings panel is fully functional with API integration
- Other components need to be updated to use real API data

