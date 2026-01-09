# Stockport v5 UI - Trading Operating System

## Overview

Stockport v5 UI is a complete redesign transforming the application from a page-based dashboard to a **trading operating system** with 5 core workspaces. This new UI model answers key questions:

1. **What does the market look like right now?** → Insight workspace
2. **What opportunities exist?** → Discover workspace
3. **Why does the algo want this trade?** → Decide workspace
4. **What is happening right now?** → Execute workspace
5. **Is the system improving?** → Review workspace

## Key Features

### Command Bar (Replaces Sidebar)
- Always visible top navigation
- Mode selector (Live/Paper/Backtest/Replay)
- Market status indicator
- Algo confidence display
- One-click pause/kill switch

### 5 Core Workspaces

#### 🧠 Insight
- Market Regime (trend, volatility, breadth)
- Algo State (confidence, bias, risk appetite)
- System Health (data providers, latency, errors)

#### 🔍 Discover
- Opportunity Radar (visual discovery)
- Signal Stream (card-based feed)
- Filter sliders (confidence, liquidity, risk)

#### ⚙️ Decide
- Strategy reasoning
- Indicator contributions
- Risk-reward mapping
- Portfolio impact (basic in v5)

#### ⚡ Execute
- Order timeline animation
- Execution quality score
- Broker latency display
- Real-time feedback

#### 📊 Review
- Performance metrics
- Strategy health
- Risk & drawdowns
- Trade replay (v5.1)

## Architecture

### No Backend Changes Required
All metrics are **derived in the UI layer** from existing APIs:
- Algo confidence → aggregated from strategy performance
- Market readiness → combined from market state
- Signal stream → filtered from opportunities endpoint
- Execution quality → calculated from order history

### Polling-First Design
- **Primary**: REST API polling (1-3s intervals)
- **Secondary**: WebSocket (optional enhancement, non-blocking)
- Graceful degradation if WebSocket unavailable

### State Management
- **Backend = Source of Truth** (all business data)
- **UI State = Presentation Only** (workspace selection, filters)
- **Context Memory**: Preserves symbol/strategy/signal across workspaces

## Usage

### Enabling v5 UI

By default, v5 UI is enabled. To use legacy v4 UI:

```bash
# Set environment variable
export ENABLE_V5_UI=false

# Or in .env file
ENABLE_V5_UI=false
```

### Running the Application

```bash
streamlit run app.py
```

The app will automatically use v5 UI unless `ENABLE_V5_UI=false` is set.

## File Structure

```
ui/
├── app_v5.py                    # Main v5 application
├── theme/                       # Dark theme system
│   ├── theme_manager.py
│   └── styles.css
├── components/
│   ├── command_bar.py           # Top command bar
│   ├── workspace_nav.py         # Workspace navigation
│   ├── visual/                  # Visual components
│   │   ├── confidence_gauge.py
│   │   ├── risk_meter.py
│   │   ├── signal_card.py
│   │   ├── provider_health_tile.py
│   │   └── strategy_card.py
│   └── charts/                  # Chart components
│       ├── opportunity_radar.py
│       ├── regime_timeline.py
│       ├── risk_reward_map.py
│       └── execution_timeline.py
├── workspaces/                  # 5 core workspaces
│   ├── router.py                # Workspace routing + context
│   ├── insight.py
│   ├── discover.py
│   ├── decide.py
│   ├── execute.py
│   └── review.py
└── services/
    ├── metric_deriver.py        # Derive metrics from APIs
    ├── polling_service.py       # Primary real-time method
    └── websocket_client.py      # Optional enhancement
```

## Migration Notes

### From v4 to v5

- **v4 UI** (`ui/app_v4.py`) is deprecated but maintained for backward compatibility
- **v5 UI** (`ui/app_v5.py`) is the new default
- Old page components (`dashboard.py`, `scanner_view.py`, etc.) are still used by v4
- Feature flag allows gradual migration

### Breaking Changes

None - v5 is fully backward compatible. Old v4 UI remains available.

## Keyboard Shortcuts

- `Alt+I` → Insight workspace
- `Alt+D` → Discover workspace
- `Alt+E` → Decide workspace
- `Alt+X` → Execute workspace
- `Alt+R` → Review workspace

## Future Enhancements (v5.1/v6)

- Correlation cluster visualization
- Advanced portfolio impact simulation
- Full trade replay feature
- WebSocket real-time streaming (optional)

## Development

### Adding New Components

1. Visual components → `ui/components/visual/`
2. Chart components → `ui/components/charts/`
3. Workspace pages → `ui/workspaces/`

### Theme Customization

Edit `ui/theme/styles.css` and use `get_theme_colors()` from `theme_manager.py` for color constants.

### Adding Metrics

All metrics should be derived in `ui/services/metric_deriver.py` - no new backend endpoints required.

## Troubleshooting

### UI Not Loading
- Check backend is running: `python -m backend.api.rest_api`
- Verify API connection in command bar status

### Workspace Not Switching
- Check browser console for JavaScript errors
- Verify query params are being set correctly

### Dark Theme Not Applied
- Ensure `inject_theme()` is called in `app_v5.py`
- Check `ui/theme/styles.css` exists

## Support

For issues or questions:
1. Check existing documentation in `docs/`
2. Review plan: `.cursor/plans/stockport_ui_redesign_*.plan.md`
3. Verify backend API endpoints are available

