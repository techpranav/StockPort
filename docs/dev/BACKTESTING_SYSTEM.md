# Backtesting System Documentation

## Overview

The Backtesting System allows you to test trading strategies on historical data to evaluate their performance before risking real capital.

## Features

- **Strategy Testing**: Test entry/exit signals on historical data
- **Performance Metrics**: Comprehensive performance analysis
- **Trade Simulation**: Realistic trade execution with transaction costs
- **Risk Management**: Stop-loss and take-profit support
- **Backtest History**: Save, retrieve, and compare backtests

## Performance Metrics

### Returns
- **Total Return**: Absolute profit/loss
- **Total Return %**: Percentage return on initial capital

### Trade Statistics
- **Total Trades**: Number of trades executed
- **Winning Trades**: Number of profitable trades
- **Losing Trades**: Number of losing trades
- **Win Rate**: Percentage of winning trades

### Profit Analysis
- **Average Profit**: Average profit per winning trade
- **Average Loss**: Average loss per losing trade
- **Profit Factor**: Ratio of total profit to total loss

### Risk Metrics
- **Max Drawdown**: Maximum peak-to-trough decline
- **Max Drawdown %**: Drawdown as percentage
- **Sharpe Ratio**: Risk-adjusted return measure

## Usage

### Running a Backtest

```python
from services.backtesting.backtest_engine import BacktestEngine
from datetime import datetime, timedelta

engine = BacktestEngine()

result = engine.run_backtest(
    strategy_name="My Strategy",
    symbols=["AAPL", "GOOGL"],
    start_date=datetime(2023, 1, 1),
    end_date=datetime(2023, 12, 31),
    initial_capital=100000.0,
    position_size_pct=10.0,
    transaction_cost=0.001,
    stop_loss_pct=5.0,
    take_profit_pct=10.0
)
```

### Saving Backtest Results

```python
from services.storage.backtest_storage import BacktestStorage

storage = BacktestStorage()
storage.save_backtest(result)
```

### Retrieving Backtest History

```python
# List all backtests
backtests = storage.list_backtests(limit=50)

# Load specific backtest
result = storage.load_backtest(backtest_id)

# Compare backtests
comparison = storage.compare_backtests([id1, id2, id3])
```

## Strategy Execution

The system executes strategies by:

1. **Iterating through date range** (daily)
2. **Analyzing stock data** for each date
3. **Generating entry signals** based on analysis
4. **Entering trades** when buy signals detected
5. **Managing positions** with stop-loss/take-profit
6. **Exiting trades** on sell signals or targets
7. **Calculating P&L** for each trade

## Trade Lifecycle

1. **Entry**: Trade opened on buy signal
2. **Open**: Position held, monitoring for exit
3. **Exit**: Trade closed on sell signal, stop-loss, or take-profit
4. **Closed**: Trade completed, P&L calculated

## UI Components

### Backtest Runner
- Configure backtest parameters
- Select stocks and date range
- Set capital and position sizing
- Configure risk management
- Run backtest

### Results View
- Performance metrics dashboard
- Trades table with details
- P&L breakdown
- Visual charts (future)

### History View
- List all backtests
- Compare multiple backtests
- Filter by strategy or date
- Delete old backtests

## Configuration

Backtest settings in `config/constants/BacktestConstants.py`:

- `DEFAULT_INITIAL_CAPITAL`: Starting capital (default: ₹100,000)
- `DEFAULT_POSITION_SIZE_PCT`: Position size percentage (default: 10%)
- `DEFAULT_TRANSACTION_COST`: Transaction cost (default: 0.1%)
- `DEFAULT_STOP_LOSS_PCT`: Default stop-loss (default: 5%)
- `DEFAULT_TAKE_PROFIT_PCT`: Default take-profit (default: 10%)

## Best Practices

1. **Use Realistic Parameters**: Set transaction costs and position sizes realistically
2. **Test Multiple Strategies**: Compare different approaches
3. **Review Trade Logs**: Understand why trades were entered/exited
4. **Consider Market Conditions**: Backtests may not reflect future market behavior
5. **Use Stop-Losses**: Always include risk management
6. **Analyze Drawdowns**: Understand maximum risk exposure
7. **Compare Strategies**: Use comparison feature to find best approach

## Limitations

- **Historical Data Only**: Cannot predict future performance
- **Simplified Execution**: May not reflect real trading conditions
- **No Slippage**: Assumes perfect execution at signal prices
- **Market Impact**: Large positions may affect prices (not modeled)

## Future Enhancements

- Visual charts and graphs
- Walk-forward analysis
- Monte Carlo simulation
- Portfolio-level backtesting
- Strategy optimization

