import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, Any, Tuple, List

class TechnicalAnalysisService:
    def __init__(self):
        """Initialize technical analysis service."""
        pass
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators for the given DataFrame."""
        # Ensure we have the required columns
        if 'Close' not in df.columns or 'Volume' not in df.columns:
            return df
        
        # Calculate Moving Averages
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
        
        # Calculate RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Calculate MACD
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
        
        # Calculate Bollinger Bands
        df['BB_Middle'] = df['Close'].rolling(window=20).mean()
        bb_std = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
        
        # Calculate Volume indicators
        df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()
        
        return df
    
    def create_price_chart(self, df: pd.DataFrame, symbol: str) -> go.Figure:
        """Create an interactive price chart with technical indicators."""
        fig = make_subplots(rows=4, cols=1, 
                           shared_xaxes=True,
                           vertical_spacing=0.05,
                           row_heights=[0.5, 0.25, 0.25, 0.25])
        
        # Candlestick chart
        fig.add_trace(go.Candlestick(x=df.index,
                                    open=df['Open'],
                                    high=df['High'],
                                    low=df['Low'],
                                    close=df['Close'],
                                    name='Price'),
                     row=1, col=1)
        
        # Add moving averages
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'],
                               name='SMA 20',
                               line=dict(color='blue')),
                     row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'],
                               name='SMA 50',
                               line=dict(color='orange')),
                     row=1, col=1)
        
        # Add Bollinger Bands
        fig.add_trace(go.Scatter(x=df.index, y=df['BB_Upper'],
                               name='BB Upper',
                               line=dict(color='gray', dash='dash')),
                     row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['BB_Lower'],
                               name='BB Lower',
                               line=dict(color='gray', dash='dash')),
                     row=1, col=1)
        
        # Volume chart
        fig.add_trace(go.Bar(x=df.index, y=df['Volume'],
                           name='Volume'),
                     row=2, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['Volume_SMA'],
                               name='Volume SMA',
                               line=dict(color='orange')),
                     row=2, col=1)
        
        # RSI chart
        fig.add_trace(go.Scatter(x=df.index, y=df['RSI'],
                               name='RSI',
                               line=dict(color='purple')),
                     row=3, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
        
        # MACD chart
        fig.add_trace(go.Scatter(x=df.index, y=df['MACD'],
                               name='MACD',
                               line=dict(color='blue')),
                     row=4, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['Signal_Line'],
                               name='Signal Line',
                               line=dict(color='orange')),
                     row=4, col=1)
        
        # Update layout
        fig.update_layout(
            title=f'Technical Analysis for {symbol}',
            xaxis_title='Date',
            yaxis_title='Price',
            yaxis2_title='Volume',
            yaxis3_title='RSI',
            yaxis4_title='MACD',
            height=1000,
            showlegend=True
        )
        
        return fig
    
    def get_technical_signals(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate technical analysis signals."""
        signals = {
            'trend': self._analyze_trend(df),
            'momentum': self._analyze_momentum(df),
            'volatility': self._analyze_volatility(df),
            'volume': self._analyze_volume(df)
        }
        return signals
    
    def _analyze_trend(self, df: pd.DataFrame) -> str:
        """Analyze price trend."""
        if df['Close'].iloc[-1] > df['SMA_20'].iloc[-1] > df['SMA_50'].iloc[-1]:
            return "Strong Uptrend"
        elif df['Close'].iloc[-1] > df['SMA_20'].iloc[-1]:
            return "Weak Uptrend"
        elif df['Close'].iloc[-1] < df['SMA_20'].iloc[-1] < df['SMA_50'].iloc[-1]:
            return "Strong Downtrend"
        elif df['Close'].iloc[-1] < df['SMA_20'].iloc[-1]:
            return "Weak Downtrend"
        return "Sideways"
    
    def _analyze_momentum(self, df: pd.DataFrame) -> str:
        """Analyze momentum."""
        if df['RSI'].iloc[-1] > 70:
            return "Overbought"
        elif df['RSI'].iloc[-1] < 30:
            return "Oversold"
        return "Neutral"
    
    def _analyze_volatility(self, df: pd.DataFrame) -> str:
        """Analyze volatility."""
        if df['Close'].iloc[-1] > df['BB_Upper'].iloc[-1]:
            return "High Volatility (Upper Band)"
        elif df['Close'].iloc[-1] < df['BB_Lower'].iloc[-1]:
            return "High Volatility (Lower Band)"
        return "Normal Volatility"
    
    def _analyze_volume(self, df: pd.DataFrame) -> str:
        """Analyze volume."""
        if df['Volume'].iloc[-1] > df['Volume_SMA'].iloc[-1] * 1.5:
            return "High Volume"
        elif df['Volume'].iloc[-1] < df['Volume_SMA'].iloc[-1] * 0.5:
            return "Low Volume"
        return "Normal Volume" 