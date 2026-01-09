---
name: Stockport UI Redesign - Trading OS Workspace Model
overview: Complete UI redesign transforming Stockport from a page-based dashboard to a trading operating system with 5 core workspaces (Insight, Discover, Decide, Execute, Review), replacing sidebar navigation with a command bar, implementing dark theme, and creating reusable visual components.
todos:
  - id: theme-system
    content: Create theme system with dark theme colors, CSS injection, and theme manager
    status: completed
  - id: command-bar
    content: Build command bar component with mode selector, market status, algo confidence, and controls
    status: completed
    dependencies:
      - theme-system
  - id: workspace-nav
    content: Create workspace navigation component with 5 workspace tabs and keyboard shortcuts
    status: completed
    dependencies:
      - theme-system
  - id: visual-components
    content: "Build reusable visual components: confidence gauge, risk meter, signal card, provider health tile, strategy card"
    status: completed
    dependencies:
      - theme-system
  - id: chart-components-v5
    content: "Create v5 chart components: opportunity radar, signal cards, confidence gauge, execution timeline (simple)"
    status: completed
    dependencies:
      - theme-system
  - id: chart-components-v6
    content: "Defer to v5.1/v6: correlation cluster, portfolio impact simulation, full trade replay (optional/phase 2)"
    status: completed
  - id: insight-workspace
    content: "Implement Insight workspace with 3-column layout: Market Regime, Algo State, System Health"
    status: completed
    dependencies:
      - command-bar
      - workspace-nav
      - visual-components
      - chart-components-v5
  - id: discover-workspace
    content: Implement Discover workspace with opportunity radar, signal stream, and filter sliders
    status: completed
    dependencies:
      - command-bar
      - workspace-nav
      - visual-components
      - chart-components-v5
  - id: decide-workspace
    content: Implement Decide workspace with strategy reasoning, indicator contributions, and risk-reward mapping
    status: completed
    dependencies:
      - command-bar
      - workspace-nav
      - visual-components
      - chart-components-v5
  - id: execute-workspace
    content: Implement Execute workspace with order timeline, execution quality, and real-time feedback
    status: completed
    dependencies:
      - command-bar
      - workspace-nav
      - visual-components
      - chart-components-v5
  - id: review-workspace
    content: Implement Review workspace with performance tabs, strategy health, and trade replay feature
    status: completed
    dependencies:
      - command-bar
      - workspace-nav
      - visual-components
      - chart-components-v5
  - id: ui-metric-derivation
    content: "Create UI metric derivation layer: derive algo confidence, market readiness, signal stream from existing APIs (no new backend endpoints)"
    status: completed
  - id: polling-service
    content: Create polling service for real-time updates (primary method, 1-3s intervals)
    status: completed
  - id: websocket-client-optional
    content: Create optional WebSocket client for enhanced real-time updates (secondary, non-blocking)
    status: completed
    dependencies:
      - polling-service
  - id: app-v5
    content: Create new main app (app_v5.py) with workspace routing and theme injection
    status: completed
    dependencies:
      - insight-workspace
      - discover-workspace
      - decide-workspace
      - execute-workspace
      - review-workspace
  - id: migration
    content: Update entry point, deprecate old UI, add migration notices, and maintain backward compatibility
    status: completed
    dependencies:
      - app-v5
---

# S

tockport UI Redesign - Trading Operating System

## Overview

Transform Stockport from a page-based dashboard to a **trading operating system** with 5 core workspaces that answer key questions: market state, algo thinking, decisions, execution, and review. Replace sidebar navigation with a command bar, implement dark theme, and create modern visual components.

## Architecture Changes

### Current Structure

- Sidebar navigation with 6 pages
- Light theme (default Streamlit)
- Table-heavy displays
- Static data presentation

### New Structure

- Command bar (always visible top navigation)
- 5 workspaces: Insight, Discover, Decide, Execute, Review
- Dark theme with custom styling
- Visual-first components (radar, heatmaps, gauges)
- Real-time updates via polling (primary) with optional WebSocket enhancement

## Implementation Plan

### Phase 1: Foundation & Theme System

#### 1.1 Create Theme System

**File**: `ui/theme/theme_manager.py`

- Dark theme color palette
- CSS injection system
- Theme configuration
- Color constants

**File**: `ui/theme/styles.css`

- Global dark theme styles
- Component-specific styles
- Animation definitions
- Responsive breakpoints

**Colors**:

- Background: `#0B1220` / `#111827`
- Surface: `#121A2A` / `#161B22`
- Accent: `#3B82F6`
- Profit: `#22C55E`
- Loss: `#EF4444`
- Warning: `#F59E0B`

#### 1.2 Create Command Bar Component

**File**: `ui/components/command_bar.py`

- Top navigation bar (always visible)
- Mode selector (Live/Paper/Backtest/Replay)
- Market status indicator
- Algo confidence display
- Pause/kill switch button
- Settings button

**Features**:

- Real-time status updates
- One-click mode switching
- System controls

#### 1.3 Create Workspace Navigation

**File**: `ui/components/workspace_nav.py`

- Horizontal workspace tabs
- Active workspace indicator
- Keyboard shortcuts (S=Scanner, E=Execute, etc.)
- Workspace icons

### Phase 2: Reusable Component Library

#### 2.1 Visual Components

**File**: `ui/components/visual/confidence_gauge.py`

- Radial confidence meter
- Animated progress
- Color-coded thresholds

**File**: `ui/components/visual/risk_meter.py`

- Risk thermometer visualization
- Multi-level risk indicators
- Visual risk zones

**File**: `ui/components/visual/signal_card.py`

- Expandable signal cards
- Sparkline charts
- Confidence rings
- Real-time updates

**File**: `ui/components/visual/provider_health_tile.py`

- Provider status tiles (Angel/NSE/Backup)
- Green/Amber/Red glow
- Latency display
- Drop rate metrics

**File**: `ui/components/visual/strategy_card.py`

- Strategy status indicators
- Edge score visualization
- Regime compatibility
- Decay warnings

#### 2.2 Chart Components

**File**: `ui/components/charts/opportunity_radar.py`

- Circular/heatmap opportunity visualization
- Score × Volume × Volatility mapping
- Interactive filtering

**File**: `ui/components/charts/regime_timeline.py`

- Market regime timeline (last 30 days)
- Confidence bands
- Regime transitions

**File**: `ui/components/charts/risk_reward_map.py`

- Risk-reward scatter plot
- Entry/SL/Target zones
- Portfolio impact visualization (basic in v5, advanced in v5.1)

**File**: `ui/components/charts/execution_timeline.py`

- Order lifecycle animation
- Real-time order status
- Broker latency display

**File**: `ui/components/charts/correlation_cluster.py` (v5.1/v6 - Optional)

- Correlation heatmap
- Portfolio exposure wheel
- Risk clustering
- **Status**: Deferred to v5.1/v6

### Phase 3: Workspace Implementations

#### 3.1 Insight Workspace (Dashboard Replacement)

**File**: `ui/workspaces/insight.py`**Layout**: 3-column, no scrolling**Left Column - Market Regime**:

- Trend/Volatility/Breadth indicators
- Regime timeline chart
- Confidence band visualization

**Center Column - Algo State**:

- Large radial confidence gauge
- Today's bias (Bullish/Neutral/Bearish)
- Risk appetite indicator
- Next action ETA countdown

**Right Column - System Health**:

- Data provider health tiles
- Execution latency metrics
- Error rate display

**Components Used**:

- `regime_timeline.py`
- `confidence_gauge.py`
- `provider_health_tile.py`

#### 3.2 Discover Workspace (Scanner Replacement)

**File**: `ui/workspaces/discover.py`**Key Features**:

- Opportunity radar (circular/heatmap)
- Signal stream (card-based feed)
- Auto-updating with filters
- Sorted by confidence × freshness

**Filters as Sliders**:

- Confidence slider
- Liquidity slider
- Risk slider
- Strategy compatibility filter

**Components Used**:

- `opportunity_radar.py`
- `signal_card.py`

#### 3.3 Decide Workspace (New - Strategy Reasoning)

**File**: `ui/workspaces/decide.py`**For Each Signal**:

- Strategy reasoning display
- Indicator contribution bars
- Risk-reward map
- Portfolio impact simulation (basic in v5, full in v5.1)
- Confidence decay timer

**Visuals**:

- Indicator contribution visualization
- Entry/SL/Target zone chart
- Portfolio fit analysis

**Components Used**:

- `risk_reward_map.py`
- `signal_card.py` (enhanced)

#### 3.4 Execute Workspace (Execution Replacement)

**File**: `ui/workspaces/execute.py`**Design Goals**:

- Zero clutter
- Real-time feedback
- Calm under pressure

**Components**:

- Order timeline animation
- Broker latency live counter
- Execution quality score
- Slippage vs expected

**Components Used**:

- `execution_timeline.py`
- Custom order status cards

#### 3.5 Review Workspace (Portfolio/Performance Replacement)

**File**: `ui/workspaces/review.py`**Tabs**:

- Performance
- Strategy Health
- Risk & Drawdowns
- Learning & Decay
- Replay (gold feature)

**Killer Feature - Trade Replay**:

- Step-by-step replay
- Market state → signal → decision → execution
- Interactive timeline

**Components Used**:

- `risk_meter.py`
- Performance charts
- `correlation_cluster.py` (v5.1/v6 - optional)

### Phase 4: UI Metric Derivation (No Backend Changes)

#### 4.1 Derive Metrics from Existing APIs

**File**: `ui/services/metric_deriver.py` (new)**Key Principle**: UI v5 is a **new lens, not a new brain**. All metrics derived from existing APIs.| UI Metric | Source ||-----------|--------|| Algo Confidence | Aggregate existing strategy confidence from `/strategies/performance` || Market Readiness | Combine regime + volatility + breadth from `/market/state` || Signal Stream | Use existing `/opportunities` endpoint with filtering || Execution Quality | Calculate from existing fill + slippage stats in `/orders` || Trade Replay | Build from existing audit logs in `/orders` history || Regime Timeline | Aggregate historical `/market/state` data (30 days) || Today's Bias | Derive from market state regime + breadth || Next Action ETA | Calculate from scanner frequency settings |**Implementation**:

- No new backend endpoints required
- All calculations done in UI layer
- Caching for expensive aggregations
- Fallback to defaults if data unavailable

#### 4.2 Real-time Updates (Polling-First Design)

**File**: `ui/services/polling_service.py` (new)**Primary Method**: Polling (1-3 second intervals)

- Poll existing REST endpoints
- Configurable refresh intervals per workspace
- Graceful degradation on errors
- Auto-backoff on failures

**File**: `ui/services/websocket_client.py` (new - Optional)**Secondary Method**: WebSocket (optional enhancement)

- WebSocket client for real-time updates
- Subscribe to events (signals, orders, market state)
- Auto-reconnect logic
- Event handlers
- **Non-blocking**: Falls back to polling if unavailable
- **Enhancement only**: Does not replace polling

**Integration Points**:

- Signal stream updates (polling primary, WebSocket optional)
- Order status changes (polling primary, WebSocket optional)
- Market state changes (polling primary, WebSocket optional)
- System health updates (polling primary, WebSocket optional)

### Phase 5: Main App Restructure

#### 5.1 New Main App

**File**: `ui/app_v5.py` (new)**Structure**:

```python
def main():
    # Inject dark theme CSS
    inject_theme()
    
    # Render command bar
    render_command_bar()
    
    # Get active workspace
    workspace = get_active_workspace()
    
    # Render workspace
    if workspace == "insight":
        render_insight_workspace()
    elif workspace == "discover":
        render_discover_workspace()
    # ... etc
```



#### 5.2 Workspace Router with Context Memory

**File**: `ui/workspaces/router.py`

- Workspace routing logic
- State management
- URL parameter handling
- Deep linking support
- **Context memory**: Persist active context across workspace navigation

**Context Memory Features**:

- Active symbol (when navigating from Discover → Decide → Execute)
- Active strategy ID
- Active signal ID
- Preserve context via session state + URL params
- Intelligent context restoration on workspace switch

### Phase 6: Migration & Cleanup

#### 6.1 Deprecate Old UI

- Mark `ui/app_v4.py` as deprecated
- Keep for backward compatibility
- Add migration notice

#### 6.2 Update Entry Point

**File**: `app.py`

- Switch to `ui/app_v5.py`
- Add feature flag for gradual rollout

#### 6.3 Component Migration

- Migrate reusable logic from old pages
- Extract common patterns
- Update API calls to use new endpoints

## File Structure

```javascript
ui/
├── app_v5.py                    # New main app
├── theme/
│   ├── theme_manager.py        # Theme system
│   └── styles.css               # Dark theme CSS
├── components/
│   ├── command_bar.py           # Top command bar
│   ├── workspace_nav.py         # Workspace navigation
│   ├── visual/
│   │   ├── confidence_gauge.py
│   │   ├── risk_meter.py
│   │   ├── signal_card.py
│   │   ├── provider_health_tile.py
│   │   └── strategy_card.py
│   └── charts/
│       ├── opportunity_radar.py
│       ├── regime_timeline.py
│       ├── risk_reward_map.py
│       ├── execution_timeline.py
│       └── correlation_cluster.py
├── workspaces/
│   ├── router.py                # Workspace routing
│   ├── insight.py               # Insight workspace
│   ├── discover.py              # Discover workspace
│   ├── decide.py                # Decide workspace
│   ├── execute.py               # Execute workspace
│   └── review.py                # Review workspace
└── services/
    ├── metric_deriver.py        # Derive UI metrics from existing APIs
    ├── polling_service.py       # Polling service (primary real-time method)
    └── websocket_client.py      # Optional WebSocket client (enhancement)
```



## Technical Decisions

### Visualization Approach

- **Plotly** for interactive charts (radar, heatmaps, timelines)
- **HTML/CSS** for layout, styling, and custom components
- **Streamlit components** for advanced interactions

### Real-time Updates

**Polling-First Design**:

- **Primary**: Polling (1-3 second intervals) via REST API
- **Secondary**: WebSocket (optional enhancement, non-blocking)
- **Auto-refresh** with configurable intervals per workspace
- **Graceful degradation**: Falls back to polling if WebSocket unavailable
- **No dependency on WebSocket** for core functionality

### State Management

**Critical Rule**: **Backend = Source of Truth, UI State = Presentation Only**

- **Backend state** = Source of truth (via API/WebSocket)
- **UI state** = Presentation only (workspace selection, filters, view preferences)
- **No business logic in UI** - all calculations derived from backend data
- **No confidence recalculation stored in session** - recompute on every refresh
- **UI recomputes view on every refresh** - no stale cached business logic

**State Ownership**:

- **Session state**: Workspace selection, UI preferences, active context (symbol, strategy, signal)
- **URL parameters**: Deep linking, workspace navigation, context passing
- **Backend state**: All business data, metrics, decisions (read-only in UI)

### Performance

- **Lazy loading** for workspace content
- **Caching** for expensive calculations
- **Debouncing** for filter inputs
- **Virtual scrolling** for long lists

## Backend Changes Required

### ✅ No Backend API Changes for v5

**Critical Decision**: UI v5 redesign does NOT require new backend endpoints.All metrics and visualizations are derived from existing APIs:

- `/status` - System status
- `/positions` - Positions data
- `/orders` - Order history and execution data
- `/opportunities` - Opportunity stream
- `/signals` - Signal data
- `/strategies/performance` - Strategy metrics
- `/market/state` - Market state data
- `/data/health` - Data health status
- `/capital/overview` - Capital metrics

**Future (v6+): Backend Optimizations (Optional)**

- Dedicated endpoints for aggregated metrics (if performance becomes an issue)
- WebSocket event streaming (if real-time requirements increase)
- Trade replay API (if replay feature becomes critical)

### WebSocket Events (Optional Enhancement)

If WebSocket is implemented (optional):

- `signal.new` - New signal detected
- `order.status` - Order status change
- `market.state` - Market state update
- `system.health` - System health change

## Testing Strategy

### Unit Tests

- Component rendering
- Theme application
- Workspace routing
- API client methods

### Integration Tests

- Workspace navigation
- Real-time updates
- API integration
- WebSocket connection

### Visual Tests

- Dark theme rendering
- Component layouts
- Responsive design
- Animation smoothness

## Migration Path

1. **Phase 1-2**: Build foundation (theme, components) - non-breaking
2. **Phase 3**: Build workspaces alongside existing pages
3. **Phase 4**: Create UI metric derivation layer (no backend changes)
4. **Phase 5**: Create new app structure with workspace router
5. **Phase 6**: Switch entry point, deprecate old UI

**Key Advantage**: No backend coordination required - UI can be developed and deployed independently.

## Success Criteria

- [ ] Command bar replaces sidebar
- [ ] All 5 workspaces functional
- [ ] Dark theme applied globally
- [ ] Real-time updates working
- [ ] Visual components match design samples
- [ ] Performance <1s load time for Insight
- [ ] All existing functionality preserved
- [ ] Backward compatibility maintained

## Dependencies

### New Python Packages

- `streamlit-components` (if needed for advanced components)
- `websocket-client` or `websockets` for WebSocket support (optional, v5.1+)

### Existing Packages (Already Used)

- `streamlit`
- `plotly`
- `pandas`
- `requests`

## Notes

- Keep existing `ui/app_v4.py` for backward compatibility
- Use feature flags for gradual rollout
- Maintain API compatibility with existing backend
- **No backend changes required** - UI redesign is independent
- **Polling-first design** - WebSocket is optional enhancement
- **UI derives all metrics** - no new backend endpoints needed
- **Context memory** - preserve user context across workspace navigation
- **State ownership** - backend is source of truth, UI is presentation only

## Chart Component Phasing

### v5 (Must-Have)

- Opportunity Radar
- Signal Cards
- Confidence Gauge
- Execution Timeline (simple)
- Regime Timeline (basic)

### v5.1 / v6 (Optional / Phase 2)

- Correlation Cluster
- Portfolio Impact Simulation (advanced)