# Stockport v4 Developer Documentation

Welcome to the Stockport v4 developer documentation!

## What is Stockport v4?

Stockport v4 is a fully automated, always-on stock analysis and trading system designed for personal use. It functions as a "trading brain" that continuously scans the market, evaluates opportunities, manages capital and risk, and can execute trades automatically.

## Quick Links

- [Getting Started](GETTING_STARTED.md) - Set up your development environment
- [Architecture Overview](architecture/overview.md) - Understand the system design
- [API Documentation](api/rest-api.md) - REST API reference
- [Frontend Components](frontend/ui-components.md) - UI component guide

## Key Features

- **Always-on Backend**: System runs continuously, independent of UI
- **Event-driven Architecture**: Components communicate via Redis pub/sub
- **Capital-aware Decisions**: Every decision considers available capital and risk limits
- **Multi-strategy Evaluation**: Opportunities evaluated across multiple strategies
- **Learning System**: Tracks performance and improves strategy selection over time
- **Safety First**: Multiple layers of risk management and kill-switch mechanisms

## Documentation Structure

- **Architecture**: System design and component details
- **Setup**: Installation and configuration guides
- **Backend**: Backend component documentation
- **API**: REST API and WebSocket documentation
- **Frontend**: UI components and navigation
- **Testing**: Testing guides and best practices
- **Operations**: Deployment and monitoring

## For AI Assistants

See [CHATGPT_COMPREHENSIVE_GUIDE.md](CHATGPT_COMPREHENSIVE_GUIDE.md) for a complete overview of the system for AI assistants.

