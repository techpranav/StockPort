# Examples

This document provides examples of common use cases for the Stock Analysis Tool.

## Basic Usage

### 1. Fetching Stock Data

```python
from services.stock_service import StockService
from services.report_service import ReportService

# Initialize services
stock_service = StockService()
report_service = ReportService()

# Fetch data for a single stock
symbol = "AAPL"
stock_data = stock_service.fetch_stock_data(symbol)

# Print basic information
print(f"Company: {stock_data.company_info.name}")
print(f"Current Price: ${stock_data.technical_analysis.current_price:.2f}")
print(f"Market Cap: ${stock_data.company_info.market_cap:,.2f}")
```

### 2. Generating Reports

```python
# Generate Excel report
excel_path = report_service.generate_excel_report(symbol, stock_data.to_dict())
print(f"Excel report generated: {excel_path}")

# Generate Word report
word_path = report_service.generate_word_report(symbol, stock_data.to_dict())
print(f"Word report generated: {word_path}")
```

### 3. Technical Analysis

```python
from services.technical_analysis_service import TechnicalAnalysisService

# Initialize service
tech_service = TechnicalAnalysisService()

# Get historical data
historical_data = stock_service.fetch_historical_data(symbol, period="1y", interval="1d")

# Calculate indicators
indicators = tech_service.calculate_indicators(historical_data)
print(f"RSI: {indicators['rsi']:.2f}")
print(f"MACD: {indicators['macd']:.2f}")

# Calculate signals
signals = tech_service.calculate_signals(historical_data)
print(f"Trend: {signals['trend']}")
print(f"Momentum: {signals['momentum']}")
```

## Advanced Usage

### 1. Batch Processing

```python
def process_multiple_stocks(symbols: List[str]):
    results = {}
    for symbol in symbols:
        try:
            stock_data = stock_service.fetch_stock_data(symbol)
            report_service.generate_excel_report(symbol, stock_data.to_dict())
            results[symbol] = "Success"
        except Exception as e:
            results[symbol] = f"Error: {str(e)}"
    return results

# Process multiple stocks
symbols = ["AAPL", "MSFT", "GOOGL", "AMZN"]
results = process_multiple_stocks(symbols)
for symbol, status in results.items():
    print(f"{symbol}: {status}")
```

### 2. Custom Analysis

```python
def custom_analysis(stock_data: StockData) -> Dict[str, Any]:
    analysis = {}
    
    # Price analysis
    current_price = stock_data.technical_analysis.current_price
    sma_50 = stock_data.technical_analysis.sma_50
    analysis['price_vs_sma'] = (current_price - sma_50) / sma_50 * 100
    
    # Volume analysis
    volume = stock_data.technical_analysis.volume
    volume_sma = stock_data.technical_analysis.volume_sma
    analysis['volume_trend'] = "High" if volume > volume_sma * 1.5 else "Low"
    
    # Financial analysis
    pe_ratio = stock_data.metrics.pe_ratio
    analysis['valuation'] = "Overvalued" if pe_ratio > 30 else "Undervalued"
    
    return analysis

# Perform custom analysis
analysis = custom_analysis(stock_data)
print("Custom Analysis Results:")
for metric, value in analysis.items():
    print(f"{metric}: {value}")
```

### 3. Portfolio Analysis

```python
def analyze_portfolio(symbols: List[str], weights: Dict[str, float]) -> Dict[str, Any]:
    portfolio_data = {}
    total_return = 0
    total_risk = 0
    
    for symbol, weight in weights.items():
        stock_data = stock_service.fetch_stock_data(symbol)
        portfolio_data[symbol] = {
            'return': stock_data.metrics.beta * weight,
            'risk': stock_data.metrics.beta * weight,
            'weight': weight
        }
        total_return += portfolio_data[symbol]['return']
        total_risk += portfolio_data[symbol]['risk']
    
    return {
        'portfolio_data': portfolio_data,
        'total_return': total_return,
        'total_risk': total_risk,
        'sharpe_ratio': total_return / total_risk if total_risk != 0 else 0
    }

# Analyze portfolio
portfolio = {
    'AAPL': 0.4,
    'MSFT': 0.3,
    'GOOGL': 0.3
}
analysis = analyze_portfolio(list(portfolio.keys()), portfolio)
print("Portfolio Analysis:")
print(f"Total Return: {analysis['total_return']:.2%}")
print(f"Total Risk: {analysis['total_risk']:.2%}")
print(f"Sharpe Ratio: {analysis['sharpe_ratio']:.2f}")
```

### 4. Data Visualization

```python
import matplotlib.pyplot as plt
import seaborn as sns

def plot_stock_analysis(symbol: str):
    # Fetch data
    stock_data = stock_service.fetch_stock_data(symbol)
    historical_data = stock_service.fetch_historical_data(symbol, period="1y")
    
    # Create subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Plot price and moving averages
    ax1.plot(historical_data.index, historical_data['Close'], label='Price')
    ax1.plot(historical_data.index, historical_data['SMA20'], label='SMA20')
    ax1.plot(historical_data.index, historical_data['SMA50'], label='SMA50')
    ax1.set_title(f'{symbol} Price and Moving Averages')
    ax1.legend()
    
    # Plot volume
    ax2.bar(historical_data.index, historical_data['Volume'])
    ax2.set_title('Volume')
    
    plt.tight_layout()
    plt.show()

# Create visualization
plot_stock_analysis("AAPL")
```

### 5. Custom Report Generation

```python
def generate_custom_report(symbol: str, template_path: str):
    # Fetch data
    stock_data = stock_service.fetch_stock_data(symbol)
    
    # Create custom report
    report = {
        'company': {
            'name': stock_data.company_info.name,
            'sector': stock_data.company_info.sector,
            'market_cap': stock_data.company_info.market_cap
        },
        'technical': {
            'current_price': stock_data.technical_analysis.current_price,
            'rsi': stock_data.technical_analysis.rsi,
            'macd': stock_data.technical_analysis.macd
        },
        'fundamental': {
            'pe_ratio': stock_data.metrics.pe_ratio,
            'eps': stock_data.metrics.eps,
            'dividend_yield': stock_data.metrics.dividend_yield
        }
    }
    
    # Generate report using template
    report_path = report_service.generate_custom_report(symbol, report, template_path)
    return report_path

# Generate custom report
template_path = "templates/custom_report.html"
report_path = generate_custom_report("AAPL", template_path)
print(f"Custom report generated: {report_path}")
```

### 6. Error Handling

```python
def safe_stock_analysis(symbol: str) -> Dict[str, Any]:
    try:
        # Fetch data with retry
        stock_data = stock_service.fetch_stock_data(symbol)
        
        # Validate data
        if not stock_data.company_info or not stock_data.technical_analysis:
            raise ValueError("Incomplete data received")
        
        # Perform analysis
        analysis = {
            'company': stock_data.company_info.name,
            'price': stock_data.technical_analysis.current_price,
            'metrics': {
                'pe_ratio': stock_data.metrics.pe_ratio,
                'eps': stock_data.metrics.eps
            }
        }
        
        return analysis
        
    except RateLimitError:
        print(f"Rate limit exceeded for {symbol}")
        return {'error': 'Rate limit exceeded'}
        
    except ConnectionError:
        print(f"Connection error for {symbol}")
        return {'error': 'Connection error'}
        
    except Exception as e:
        print(f"Unexpected error for {symbol}: {str(e)}")
        return {'error': str(e)}

# Safe analysis
result = safe_stock_analysis("AAPL")
if 'error' in result:
    print(f"Analysis failed: {result['error']}")
else:
    print("Analysis successful:")
    print(f"Company: {result['company']}")
    print(f"Price: ${result['price']:.2f}")
```

## Best Practices

1. Always use error handling
2. Implement rate limiting
3. Cache frequently accessed data
4. Validate input data
5. Use type hints
6. Document your code
7. Write unit tests
8. Monitor performance 