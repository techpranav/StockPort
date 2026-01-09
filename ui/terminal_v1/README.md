# Terminal v1 UI

Clean, professional trading terminal UI implementation.

## Structure

```
ui/terminal_v1/
├── app.py                   # Entry point
├── layout/                  # Z1-Z4 structure
│   ├── shell.py            # Z1 (System Bar) + Z2 (Workspace Tabs)
│   ├── context_strip.py    # Z3 (Filters/Scope)
│   └── canvas.py           # Z4 (Main Canvas)
├── workspaces/             # One file = one workspace
│   └── discover.py         # Discover workspace (IMPLEMENTED)
├── components/             # Reusable UI primitives
│   ├── primitives/        # Basic UI elements
│   ├── stream/            # Dense list components
│   └── charts/            # Chart visualizations
├── services/              # UI data adapters
│   └── ui_data_service.py # Data access layer
├── styles/                # CSS (single source of truth)
│   ├── tokens.css        # Design tokens
│   ├── layout.css        # Z1-Z4 rules
│   ├── components.css    # Primitive styles
│   ├── density.css       # Compact/normal modes
│   └── main.css          # Main stylesheet
└── utils/                 # Utilities
    ├── ui_guards.py      # Validation
    └── debug.py          # Logging
```

## Layout Contract

ALL screens follow this structure:

- **Z1**: System Bar (thin, full-width, fixed)
- **Z2**: Workspace Tabs (horizontal only)
- **Z3**: Context Strip (filters / scope)
- **Z4**: Main Canvas (workspace content)

## UI Primitives

All UI is composed from reusable primitives:

- `StatusPill` - Status indicators
- `MetricInline` - Inline metrics (label: value)
- `SectionHeader` - Section titles
- `EmptyState` - Empty state messages
- `Divider` - Visual separators
- `StreamRow` - Dense list rows
- `StreamList` - Scrollable list container

## Current Status

✅ **Implemented:**
- Layout shell (Z1-Z4)
- All UI primitives
- Discover workspace
- CSS styling system

⏸️ **Pending:**
- Other workspaces (insight, decide, execute, review)
- Additional chart components
- Advanced filtering

## Usage

Run the terminal v1 UI:

```bash
streamlit run ui/terminal_v1/app.py
```

## Design Principles

1. **Density > Beauty** - Information density is prioritized
2. **Consistency > Creativity** - Reuse primitives, avoid custom widgets
3. **Simplicity > Complexity** - Choose the simpler solution
4. **Left-aligned, Wide** - No centered cards, full-width layout
5. **Predictable** - Layout is boring (good for trading terminals)

