# End-to-end flow

This page gives the high-level system flow from startup to execution.

## Flow

```mermaid
flowchart TD
    start[SystemStart] --> config[LoadConfig]
    config --> providers[InitProviders]
    providers --> scan[ScanUniverse]
    scan --> strategies[RunStrategies]
    strategies --> signals[EmitSignals]
    signals --> decide[ApplyRiskAndCapitalGates]
    decide -->|approve| execute[CreateAndRouteOrder]
    decide -->|reject| reject[RecordRejection]
    execute --> monitor[MonitorOrderLifecycle]
    monitor --> ui[PublishUpdatesToUI]
    reject --> ui
```

## Notes

Each stage has its own failure modes; see [Operations troubleshooting](../operations/troubleshooting.md).


