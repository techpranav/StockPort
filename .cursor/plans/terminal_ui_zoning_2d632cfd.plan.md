---
name: Terminal UI Zoning
overview: Restructure Stockport v5 UI into a consistent 5-zone trading terminal layout (Z1–Z5) across all v5 workspaces, using reusable components and standardized styling, without changing backend APIs or adding features.
todos:
  - id: add-zone-layout
    content: Add reusable Z1–Z5 layout wrappers (`sp_zone`, shell helper) and wire sticky zone styling hooks.
    status: completed
  - id: build-z1-z2-bars
    content: Implement standardized Z1 System Bar + Z2 Context Bar using existing UI data services; enforce compact terminal constraints.
    status: completed
    dependencies:
      - add-zone-layout
  - id: z5-sidebar-panel
    content: Implement Z5 as a sidebar detail/action panel that is hidden by default and opens on selection; reuse existing detail components.
    status: completed
    dependencies:
      - add-zone-layout
  - id: refactor-workspaces
    content: Refactor v5 workspaces (Insight/Discover/Decide/Execute/Review) to render into Z3 (hero) + Z4 (stream) and drive Z5 via selection.
    status: completed
    dependencies:
      - build-z1-z2-bars
      - z5-sidebar-panel
  - id: style-density-pass
    content: Update `ui/theme/styles.css` to reduce borders, increase density, add scrollable stream styling, and keep accent/action color discipline.
    status: completed
    dependencies:
      - refactor-workspaces
---

# Stockport v5 UI: 5-Zone Terminal Restructure

## Goal

Standardize the **v5 Trading OS UI only** (entrypoint [`app.py`](app.py) → [`ui/app_v5.py`](ui/app_v5.py) + [`ui/workspaces/`](ui/workspaces/)) into the mandatory **5 reusable zones (Z1–Z5)** with higher density, consistent hierarchy, and reusable terminal primitives—**no backend changes, no new features**.

## What we’ll build (UI-only primitives)

- **Zone layout wrappers (reusable everywhere)** in [`ui/components/layout/zones.py`](ui/components/layout/zones.py)
- `sp_zone(zone_id, css_class=..., aria_label=...)` contextmanager (same pattern as `sp_surface` in [`ui/components/layout/surfaces.py`](ui/components/layout/surfaces.py))
- `render_terminal_shell(render_z3, render_z4, ...)` helper so each workspace is just “fill Z3/Z4”
- **Z1 System Bar** (always visible, max ~48px) in [`ui/components/bars/system_bar.py`](ui/components/bars/system_bar.py)
- Inline: **Mode**, **Algo confidence (number+color)**, **Market bias**, **Health/latency indicator**, **Pause/Resume/Kill** actions
- Uses existing data sources only: `get_ui_data_service().get_system_status()`, `get_metric_deriver().get_algo_confidence()`, `get_metric_deriver().get_todays_bias()`, `get_ui_data_service().get_data_health()`.
- **Z2 Context Bar** (muted, glanceable) in [`ui/components/bars/context_bar.py`](ui/components/bars/context_bar.py)
- Regime / Volatility / Breadth / Liquidity as compact **metric badges**; optional micro-sparkline only if already available from existing UI data (no new API).
- **Z4 Stream Row** + primitives in [`ui/components/terminal/primitives.py`](ui/components/terminal/primitives.py)
- `render_status_pill()`, `render_metric_badge()`, `render_stream_row()` (dense, row-first; expand-on-click via selection → Z5)
- Keep existing `render_empty_state()` from [`ui/components/visual/empty_state.py`](ui/components/visual/empty_state.py) as the canonical empty state.
- **Z5 Detail / Action Panel** implemented as `st.sidebar` in [`ui/components/panels/detail_panel.py`](ui/components/panels/detail_panel.py)
- Hidden by default; opens only when `st.session_state` has a selection (symbol/signal/order)
- Shows existing detail components (ex: `render_signal_card(..., show_expanded=True)`) rather than inventing new data.

## Styling / density standardization

- Update [`ui/theme/styles.css`](ui/theme/styles.css) to introduce:
- `.sp-z1` and `.sp-z2` sticky bars (Z1 at `top:0`, Z2 at `top:48px`), compact typography, no card borders
- `.sp-z3` hero canvas background (darker, minimal chrome)
- `.sp-z4` scrollable stream region with fixed height using viewport math (`max-height: calc(100vh - <bars> - <padding>)`) and `overflow-y:auto`
- `.sp-z5` sidebar detail styling (high contrast, focused)
- Reduce borders/shadows globally (shift from borders → spacing/contrast), and ensure **accent color is action-only**.

## Workspace-by-workspace refactor (no feature changes)

### Insight ([`ui/workspaces/insight.py`](ui/workspaces/insight.py))

- **Z1**: System bar
- **Z2**: Market context badges (regime/vol/breadth/liquidity)
- **Z3 (hero)**: Algo confidence (reuse `render_confidence_gauge`) + 1–2 key KPIs
- **Z4**: Minimal/optional (e.g., compact health summary rows) or intentional empty state
- **Z5**: Sidebar opens only when inspecting a provider/symbol (if selected)

### Discover ([`ui/workspaces/discover.py`](ui/workspaces/discover.py))

- **Z3 (hero)**: Opportunity Radar (keep existing `render_opportunity_radar`)
- **Z4 (right stream)**: Replace card stack + expander with dense stream rows sorted by urgency; keep existing filters but compress them into the top of Z4 (still same functionality)
- **Z5 (sidebar)**: On selecting a stream row, set active context and show the full `render_signal_card(..., show_expanded=True)`.

### Decide ([`ui/workspaces/decide.py`](ui/workspaces/decide.py))

- **Z3 (hero)**: Risk–reward visualization (`render_risk_reward_map`)
- **Z4**: Supporting signal breakdown (indicator contribution list, compact)
- **Z5**: Sidebar shows decision context + any existing controls/notes (no new actions)

### Execute ([`ui/workspaces/execute.py`](ui/workspaces/execute.py))

- **Z3 (hero)**: Execution performance / order timeline (`render_execution_timeline`)
- **Z4**: Active orders + fills as dense rows (no tables by default)
- **Z5**: Sidebar shows selected order details (read-only unless existing actions already exist)

### Review ([`ui/workspaces/review.py`](ui/workspaces/review.py))

- Replace inner “tabs dashboard” feel with the same zone structure:
- **Z3 (hero)**: One performance-focused hero (PnL/drawdown/replay placeholder stays placeholder—just re-housed)
- **Z4**: Trade/order history stream
- **Z5**: Sidebar trade inspection

## App shell updates

- Update [`ui/app_v5.py`](ui/app_v5.py) to use the new zone shell (Z1/Z2 always visible, consistent layout wrapper).
- Replace legacy `render_command_bar()` usage with the new **Z1 system bar** (or refactor [`ui/components/command_bar.py`](ui/components/command_bar.py) into the Z1 implementation).

## Regression & constraints checks

- Ensure **no backend calls change** (same `UIDataService`/`MetricDeriver` methods).
- Replace all ad-hoc `st.info("No ...")`/`st.warning("No ...")` empty messages in v5 workspaces with the intentional empty state component.