"""
Backtest Result Model

Defines data structures for backtesting results.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class TradeType(Enum):
    """Trade types."""
    BUY = "buy"
    SELL = "sell"


class TradeStatus(Enum):
    """Trade status."""
    OPEN = "open"
    CLOSED = "closed"
    STOPPED = "stopped"


@dataclass
class BacktestTrade:
    """Represents a single trade in a backtest."""
    id: str
    symbol: str
    trade_type: TradeType
    entry_date: datetime
    entry_price: float
    exit_date: Optional[datetime] = None
    exit_price: Optional[float] = None
    quantity: int = 1
    status: TradeStatus = TradeStatus.OPEN
    profit_loss: Optional[float] = None
    profit_loss_pct: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    entry_signal: Optional[Dict[str, Any]] = None
    exit_reason: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'trade_type': self.trade_type.value,
            'entry_date': self.entry_date.isoformat(),
            'entry_price': self.entry_price,
            'exit_date': self.exit_date.isoformat() if self.exit_date else None,
            'exit_price': self.exit_price,
            'quantity': self.quantity,
            'status': self.status.value,
            'profit_loss': self.profit_loss,
            'profit_loss_pct': self.profit_loss_pct,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'entry_signal': self.entry_signal,
            'exit_reason': self.exit_reason
        }


@dataclass
class BacktestResult:
    """Represents complete backtest results."""
    id: str
    strategy_name: str
    symbols: List[str]
    start_date: datetime
    end_date: datetime
    initial_capital: float
    final_capital: float
    total_return: float
    total_return_pct: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    avg_profit: float
    avg_loss: float
    profit_factor: float
    max_drawdown: float
    max_drawdown_pct: float
    sharpe_ratio: Optional[float] = None
    trades: List[BacktestTrade] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'strategy_name': self.strategy_name,
            'symbols': self.symbols,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'initial_capital': self.initial_capital,
            'final_capital': self.final_capital,
            'total_return': self.total_return,
            'total_return_pct': self.total_return_pct,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': self.win_rate,
            'avg_profit': self.avg_profit,
            'avg_loss': self.avg_loss,
            'profit_factor': self.profit_factor,
            'max_drawdown': self.max_drawdown,
            'max_drawdown_pct': self.max_drawdown_pct,
            'sharpe_ratio': self.sharpe_ratio,
            'trades': [t.to_dict() for t in self.trades],
            'created_at': self.created_at.isoformat(),
            'metadata': self.metadata
        }

