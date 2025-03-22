import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta
import yfinance as yf

class PortfolioService:
    def __init__(self):
        """Initialize portfolio service."""
        pass
    
    def calculate_portfolio_metrics(self, positions: List[Dict[str, Any]], prices: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Calculate portfolio metrics."""
        metrics = {
            'total_value': 0,
            'positions': [],
            'sector_allocation': {},
            'risk_metrics': {},
            'performance': {}
        }
        
        # Calculate position values and metrics
        for position in positions:
            symbol = position['symbol']
            shares = position['shares']
            cost_basis = position['cost_basis']
            
            if symbol in prices:
                current_price = prices[symbol]['Close'].iloc[-1]
                # Calculate position return
                if cost_basis > 0:
                    position_return = (current_price - cost_basis) / cost_basis * 100
                else:
                    position_return = 0  # Set return to 0 if cost basis is 0 or negative
                
                position_value = shares * current_price
                metrics['total_value'] += position_value
                metrics['positions'].append({
                    'symbol': symbol,
                    'shares': shares,
                    'cost_basis': cost_basis,
                    'current_price': current_price,
                    'position_value': position_value,
                    'return': position_return
                })
                position['position_value'] = position_value
                position['current_price'] = current_price
                position['return']= position_return
        
        # Calculate sector allocation
        metrics['sector_allocation'] = self._calculate_sector_allocation(positions)
        
        # Calculate risk metrics
        metrics['risk_metrics'] = self._calculate_risk_metrics(positions, prices)
        
        # Calculate performance metrics
        metrics['performance'] = self._calculate_performance_metrics(positions, prices)
        
        return metrics
    
    def _calculate_sector_allocation(self, positions: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate sector allocation percentages."""
        sector_values = {}
        print(f"Positions: {positions}")
        total_value = sum(pos['position_value'] for pos in positions)
        
        for position in positions:
            sector = position.get('sector', 'Unknown')
            sector_values[sector] = sector_values.get(sector, 0) + position['position_value']
        
        return {sector: (value / total_value) * 100 for sector, value in sector_values.items()}
    
    def _calculate_risk_metrics(self, positions: List[Dict[str, Any]], prices: Dict[str, pd.DataFrame]) -> Dict[str, float]:
        """Calculate portfolio risk metrics."""
        # Calculate portfolio volatility
        returns = []
        for position in positions:
            symbol = position['symbol']
            if symbol in prices:
                price_data = prices[symbol]['Close']
                # Ensure price data is timezone-naive
                if price_data.index.tz is not None:
                    price_data.index = price_data.index.tz_localize(None)
                position_returns = price_data.pct_change().dropna()
                returns.append(position_returns * (position['position_value'] / sum(p['position_value'] for p in positions)))
        
        if returns:
            portfolio_returns = pd.concat(returns, axis=1).sum(axis=1).squeeze()
            volatility = portfolio_returns.std() * np.sqrt(252)  # Annualized volatility
            
            # Calculate Beta (assuming market data is available)
            market_returns = self._get_market_returns()
            
            if not market_returns.empty:
                # Align the dates between portfolio and market returns
                aligned_returns = pd.DataFrame({
                    'portfolio': portfolio_returns,
                    'market': market_returns
                }).dropna()
                
                if not aligned_returns.empty:
                    # Calculate beta using aligned returns
                    beta = np.cov(aligned_returns['portfolio'], aligned_returns['market'])[0,1] / np.var(aligned_returns['market'])
                    
                    # Calculate Sharpe Ratio (assuming risk-free rate)
                    risk_free_rate = 0.02  # 2% annual risk-free rate
                    excess_returns = aligned_returns['portfolio'] - (risk_free_rate/252)
                    sharpe_ratio = np.sqrt(252) * excess_returns.mean() / excess_returns.std()
                    
                    return {
                        'volatility': volatility * 100,  # Convert to percentage
                        'beta': beta,
                        'sharpe_ratio': sharpe_ratio
                    }
            
            return {
                'volatility': volatility * 100,  # Convert to percentage
                'beta': 0.0,  # Default value when market data is not available
                'sharpe_ratio': 0.0  # Default value when market data is not available
            }
        
        return {}
    
    def _calculate_performance_metrics(self, positions: List[Dict[str, Any]], prices: Dict[str, pd.DataFrame]) -> Dict[str, float]:
        """Calculate portfolio performance metrics."""
        # Calculate total return
        total_return = sum(pos['return'] for pos in positions)
        
        # Calculate daily returns for the last 30 days
        daily_returns = []
        for position in positions:
            symbol = position['symbol']
            if symbol in prices:
                price_data = prices[symbol]['Close'].tail(30)
                position_returns = price_data.pct_change().dropna()
                daily_returns.append(position_returns * (position['position_value'] / sum(p['position_value'] for p in positions)))
        
        if daily_returns:
            portfolio_daily_returns = pd.concat(daily_returns, axis=1).sum(axis=1)
            
            # Calculate 30-day return
            thirty_day_return = (portfolio_daily_returns + 1).prod() - 1
            
            # Calculate maximum drawdown
            cumulative_returns = (1 + portfolio_daily_returns).cumprod()
            rolling_max = cumulative_returns.expanding().max()
            drawdowns = (cumulative_returns - rolling_max) / rolling_max
            max_drawdown = drawdowns.min()
            
            return {
                'total_return': total_return,
                'thirty_day_return': thirty_day_return * 100,
                'max_drawdown': max_drawdown * 100
            }
        
        return {}
    
    def _get_market_returns(self) -> pd.Series:
        """Get market returns using S&P 500 (^GSPC) as benchmark."""
        try:
            # Fetch S&P 500 data for the last 2 years to ensure enough data for calculations
            end_date = datetime.now()
            start_date = end_date - timedelta(days=730)
            
            sp500 = yf.download('^GSPC', start=start_date, end=end_date)
            
            if sp500.empty:
                print("Warning: No market data available")
                return pd.Series()
            
            # Calculate daily returns and ensure 1-dimensional
            market_returns = sp500['Close'].pct_change().dropna().squeeze()
            
            # Convert to timezone-naive
            market_returns.index = market_returns.index.tz_localize(None)
            
            return market_returns
            
        except Exception as e:
            print(f"Error fetching market returns: {str(e)}")
            return pd.Series()
    
    def generate_portfolio_report(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate portfolio analysis report."""
        report = {
            'summary': self._generate_summary(metrics),
            'risk_analysis': self._analyze_risk(metrics),
            'performance_analysis': self._analyze_performance(metrics),
            'recommendations': self._generate_recommendations(metrics)
        }
        return report
    
    def _generate_summary(self, metrics: Dict[str, Any]) -> str:
        """Generate portfolio summary."""
        total_value = metrics['total_value']
        total_return = metrics['performance'].get('total_return', 0)
        
        summary = f"Portfolio Summary:\n"
        summary += f"Total Value: ${total_value:,.2f}\n"
        summary += f"Total Return: {total_return:.2f}%\n"
        summary += f"Number of Positions: {len(metrics['positions'])}\n"
        
        return summary
    
    def _analyze_risk(self, metrics: Dict[str, Any]) -> str:
        """Analyze portfolio risk."""
        risk_metrics = metrics['risk_metrics']
        
        analysis = "Risk Analysis:\n"
        analysis += f"Portfolio Volatility: {risk_metrics.get('volatility', 0):.2f}%\n"
        analysis += f"Beta: {risk_metrics.get('beta', 0):.2f}\n"
        analysis += f"Sharpe Ratio: {risk_metrics.get('sharpe_ratio', 0):.2f}\n"
        
        return analysis
    
    def _analyze_performance(self, metrics: Dict[str, Any]) -> str:
        """Analyze portfolio performance."""
        performance = metrics['performance']
        
        analysis = "Performance Analysis:\n"
        analysis += f"30-Day Return: {performance.get('thirty_day_return', 0):.2f}%\n"
        analysis += f"Maximum Drawdown: {performance.get('max_drawdown', 0):.2f}%\n"
        
        return analysis
    
    def _generate_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate portfolio recommendations."""
        recommendations = []
        
        # Analyze sector concentration
        sector_allocation = metrics['sector_allocation']
        for sector, percentage in sector_allocation.items():
            if percentage > 30:
                recommendations.append(f"High concentration in {sector} sector ({percentage:.1f}%). Consider diversifying.")
        
        # Analyze risk metrics
        risk_metrics = metrics['risk_metrics']
        if risk_metrics.get('volatility', 0) > 20:
            recommendations.append("High portfolio volatility. Consider adding more defensive positions.")
        if risk_metrics.get('beta', 0) > 1.2:
            recommendations.append("High market sensitivity. Consider adding low-beta positions.")
        
        # Analyze performance
        performance = metrics['performance']
        if performance.get('max_drawdown', 0) < -20:
            recommendations.append("Large drawdown risk. Consider implementing stop-loss orders.")
        
        return recommendations 