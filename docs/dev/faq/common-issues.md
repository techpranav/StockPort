# FAQ (Common issues)

## Docs build failures

### “Page referenced in nav does not exist”

- Create the missing page under `docs/dev/` (dev site) or `docs/` (user site)
- Or remove/update the nav entry in `mkdocs.yml` / `mkdocs-user.yml`

### “exclude_docs expected multiline string”

MkDocs expects:

```yaml
exclude_docs: |
  dev/**
```

## No opportunities or signals

- Provider health is degraded (YELLOW/RED)
- Universe is too small (or filters too strict)
- Indicator computation is incomplete for the strategy (missing `roc`, `volume_ratio`, Bollinger fields, etc)

## Decisions always rejected

Common reasons from `DecisionEngine`:

- Signal expired or opportunity stale
- Position size is zero (capital/stop invalid)
- Risk checks failed (risk limits, sector, correlation, kill-switch)
- Risk–reward < **1.5:1**

## Execution failures

- Broker credentials/config not set
- Market closed or symbol not tradable
- Order rejected by broker (see broker logs + execution timeline)


