# Stockport v4 Documentation

This directory contains comprehensive documentation for Stockport v4, built with MkDocs and Material theme.

## Documentation Structure

### Developer Documentation

Located in `docs/` directory, served with `mkdocs.yml`:

- **Architecture**: System design and component details
- **Setup**: Installation and configuration guides
- **Backend**: Backend component documentation
- **API**: REST API and WebSocket documentation
- **Frontend**: UI components and navigation
- **Testing**: Testing guides and best practices
- **Operations**: Deployment and monitoring

### User Documentation

Located in `docs/user/` directory, served with `mkdocs-user.yml`:

- **Getting Started**: User onboarding guide
- **Dashboard**: How to use the dashboard
- **Market Scanner**: Using the scanner
- **Strategies**: Managing strategies
- **Portfolio**: Portfolio management
- **Execution**: Order execution monitoring
- **Settings**: Configuration guide
- **Guides**: Best practices and troubleshooting

## Quick Start

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Serve Developer Documentation

```bash
# From project root
mkdocs serve

# Documentation will be available at:
# http://localhost:8000
```

### Serve User Documentation

```bash
# From project root
mkdocs serve -f mkdocs-user.yml

# Documentation will be available at:
# http://localhost:8000
```

### Build Documentation

```bash
# Build developer docs
mkdocs build

# Build user docs
mkdocs build -f mkdocs-user.yml

# Output will be in site/ and site-user/ directories
```

## Adding Content

1. Edit markdown files in `docs/` or `docs/user/` directories
2. Update `mkdocs.yml` or `mkdocs-user.yml` navigation if adding new pages
3. Test locally with `mkdocs serve`
4. Commit changes

## Documentation Guidelines

- Use clear, concise language
- Include code examples where helpful
- Add diagrams for complex concepts
- Keep navigation organized
- Update both user and dev docs when features change

## Key Documents

- **[CHATGPT_COMPREHENSIVE_GUIDE.md](CHATGPT_COMPREHENSIVE_GUIDE.md)**: Complete system overview for AI assistants
- **[GETTING_STARTED.md](GETTING_STARTED.md)**: Developer getting started guide
- **[DOCUMENTATION_SETUP.md](DOCUMENTATION_SETUP.md)**: Documentation maintenance guide
- **[DOCUMENTATION_SUMMARY.md](DOCUMENTATION_SUMMARY.md)**: Implementation summary

## References

- [MkDocs Documentation](https://www.mkdocs.org/)
- [Material Theme](https://squidfunk.github.io/mkdocs-material/)
