# Theming & Layout

Stockport applies a global theme via `ui/theme/`.

## Theme injection

- `ui/app_v5.py` calls `inject_theme()` from `ui/theme/theme_manager.py`.
- CSS lives in `ui/theme/styles.css`.

## Hierarchy surfaces

The UI uses a three-level visual system:

- **L1 (hero)**: primary canvas per workspace
- **L2**: supporting sections
- **L3**: optional/detail sections

To apply consistent surfaces in Streamlit, layout wrappers are implemented in:

- `ui/components/layout/surfaces.py` (`sp_surface`)


