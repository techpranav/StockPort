# Documentation publishing (MkDocs)

Stockport has **two MkDocs sites**:

- **User docs**: `mkdocs-user.yml` → `docs/` → output `site-user/`
- **Dev docs**: `mkdocs.yml` → `docs/dev/` → output `site/`

## Local usage

```bash
# Dev docs
mkdocs serve -f mkdocs.yml

# User docs
mkdocs serve -f mkdocs-user.yml
```

## GitHub Pages (two sites)

Recommended approach: publish both sites to a single `gh-pages` branch under subpaths:

- `/dev/` → developer docs (`site/`)
- `/user/` → user docs (`site-user/`)

This repo includes a GitHub Actions workflow: `.github/workflows/docs.yml`.

### One-time GitHub Pages settings

In your GitHub repository settings:

1. Go to **Settings → Pages**
2. Set **Source** to **Deploy from a branch**
3. Select branch **`gh-pages`** and folder **`/ (root)`**

After the workflow runs, your docs will be available at:

- `https://<org>.github.io/<repo>/dev/`
- `https://<org>.github.io/<repo>/user/`

### Build commands

```bash
mkdocs build -f mkdocs.yml
mkdocs build -f mkdocs-user.yml
```

### Deploy concept

Copy the build outputs into a single folder structure before publishing:

- `public/dev/` ← `site/`
- `public/user/` ← `site-user/`

Then publish `public/` to GitHub Pages.


