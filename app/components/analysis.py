import streamlit as st
from typing import Dict, Any, List
import pandas as pd
from pathlib import Path
from core.config import (
    ENABLE_AI_FEATURES,
    ENABLE_TECHNICAL_ANALYSIS,
    ENABLE_FUNDAMENTAL_ANALYSIS,
    ENABLE_PORTFOLIO_ANALYSIS
)
import plotly.graph_objects as go
from services.technical_analysis import TechnicalAnalysisService
from services.fundamental_analysis import FundamentalAnalysisService
from services.portfolio_service import PortfolioService
from utils.debug_utils import DebugUtils

def render_single_stock_analysis() -> Dict[str, Any]:
    """Render the single stock analysis section."""
    st.header("Single Stock Analysis")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        symbol = st.text_input("Enter Stock Symbol", placeholder="e.g., AAPL")
    with col2:
        analyze_button = st.button("Analyze Stock", type="primary")
    
    return {
        "symbol": symbol.upper(),
        "analyze": bool(analyze_button and symbol)
    }

def render_mass_analysis() -> Dict[str, Any]:
    """Render the mass analysis section."""
    st.header("Mass Stock Analysis")
    
    # Create a container for the file upload area
    upload_container = st.container()
    
    with upload_container:
        st.markdown("""
        <style>
        .upload-area {
            border: 2px dashed #ccc;
            border-radius: 5px;
            padding: 20px;
            text-align: center;
            background-color: #f8f9fa;
            margin: 10px 0;
        }
        .upload-area:hover {
            border-color: #2196F3;
            background-color: #f0f7ff;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="upload-area">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "📁 Drag and drop your stock symbols file here or click to browse",
            type=["txt", "csv"],
            help="Upload a file containing stock symbols (one per line)"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    if not uploaded_file:
        return {"symbols": [], "analyze": False}
    
    # Process uploaded file
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
            symbols = df.iloc[:, 0].tolist()  # Assuming first column contains symbols
        else:
            symbols = [line.decode().strip() for line in uploaded_file.readlines()]
        
        # Display file info and preview
        st.success(f"✅ Successfully loaded {len(symbols)} symbols from {uploaded_file.name}")
        
        # Create expandable preview
        with st.expander("📋 Preview Symbols", expanded=True):
            preview_df = pd.DataFrame(symbols, columns=['Symbol'])
            st.dataframe(preview_df.head(10), use_container_width=True)
            if len(symbols) > 10:
                st.info(f"... and {len(symbols) - 10} more symbols")
        
        # Add analyze button with visual feedback
        analyze_button = st.button("🚀 Start Analysis", type="primary", use_container_width=True)
        
        return {
            "symbols": symbols,
            "analyze": bool(analyze_button and symbols)
        }
        
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
        return {"symbols": [], "analyze": False}

def display_analysis_results(results: List[Dict[str, Any]], output_dir: Path) -> None:
    """Display analysis results and download options."""
    if not results:
        st.warning("No results to display.")
        return
    
    # Create a container for results
    results_container = st.container()
    
    with results_container:
        st.markdown("""
        <style>
        .results-area {
            border: 1px solid #e0e0e0;
            border-radius: 5px;
            padding: 15px;
            margin: 10px 0;
            background-color: #ffffff;
        }
        .results-area:hover {
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Initialize services based on enabled features
        technical_service = TechnicalAnalysisService() if ENABLE_TECHNICAL_ANALYSIS else None
        fundamental_service = FundamentalAnalysisService() if ENABLE_FUNDAMENTAL_ANALYSIS else None
        portfolio_service = PortfolioService() if ENABLE_PORTFOLIO_ANALYSIS else None
        
        # Display progress
        total_stocks = len(results)
        st.progress(1.0, text=f"Analysis complete for {total_stocks} stocks")
        
        # Create expandable sections for each result
        for i, result in enumerate(results, 1):
            with st.expander(f"📊 {result['symbol']} Analysis Results", expanded=(i == 1)):
                st.markdown('<div class="results-area">', unsafe_allow_html=True)
                
                # Create tabs based on enabled features
                tabs = ["Overview"]
                if ENABLE_TECHNICAL_ANALYSIS:
                    tabs.append("Technical Analysis")
                if ENABLE_FUNDAMENTAL_ANALYSIS:
                    tabs.append("Fundamental Analysis")
                if ENABLE_PORTFOLIO_ANALYSIS:
                    tabs.append("Portfolio")
                    
                tab_objects = st.tabs(tabs)
                
                # Overview tab is always present
                with tab_objects[0]:
                    display_overview(result)
                
                # Technical Analysis tab
                if ENABLE_TECHNICAL_ANALYSIS:
                    with tab_objects[tabs.index("Technical Analysis")]:
                        display_technical_analysis(result, technical_service)
                
                # Fundamental Analysis tab
                if ENABLE_FUNDAMENTAL_ANALYSIS:
                    with tab_objects[tabs.index("Fundamental Analysis")]:
                        display_fundamental_analysis(result, fundamental_service)
                
                # Portfolio tab
                if ENABLE_PORTFOLIO_ANALYSIS:
                    with tab_objects[tabs.index("Portfolio")]:
                        display_portfolio_analysis(result, portfolio_service)
                
                # Display download options
                display_download_options(result, output_dir)
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Add summary statistics
        st.markdown("### 📈 Analysis Summary")
        successful = sum(1 for r in results if r.get('status') == 'success')
        failed = sum(1 for r in results if r.get('status') == 'error')
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Stocks", total_stocks)
        with col2:
            st.metric("Successful", successful)
        with col3:
            st.metric("Failed", failed)

def display_overview(result: Dict[str, Any]) -> None:
    """Display overview of the analysis results."""
    
    # Create comprehensive overview with multiple sections
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Financial Metrics")
        if result.get('metrics'):
            metrics = result['metrics']
            
            # Create a clean metrics DataFrame
            metrics_data = []
            
            # Financial Performance
            if metrics.get('revenue'):
                metrics_data.append(['Revenue', f"${metrics['revenue']:,.0f}" if metrics['revenue'] else "N/A"])
            if metrics.get('net_income'):
                metrics_data.append(['Net Income', f"${metrics['net_income']:,.0f}" if metrics['net_income'] else "N/A"])
            if metrics.get('gross_profit'):
                metrics_data.append(['Gross Profit', f"${metrics['gross_profit']:,.0f}" if metrics['gross_profit'] else "N/A"])
            if metrics.get('operating_income'):
                metrics_data.append(['Operating Income', f"${metrics['operating_income']:,.0f}" if metrics['operating_income'] else "N/A"])
            
            # Financial Ratios
            if metrics.get('eps'):
                metrics_data.append(['EPS', f"${metrics['eps']:.2f}" if metrics['eps'] else "N/A"])
            if metrics.get('pe_ratio'):
                metrics_data.append(['P/E Ratio', f"{metrics['pe_ratio']:.2f}" if metrics['pe_ratio'] else "N/A"])
            if metrics.get('dividend_yield'):
                metrics_data.append(['Dividend Yield', f"{metrics['dividend_yield']*100:.2f}%" if metrics['dividend_yield'] else "N/A"])
            if metrics.get('beta'):
                metrics_data.append(['Beta', f"{metrics['beta']:.2f}" if metrics['beta'] else "N/A"])
            
            if metrics_data:
                metrics_df = pd.DataFrame(metrics_data, columns=['Metric', 'Value'])
                st.dataframe(metrics_df, use_container_width=True, hide_index=True)
            else:
                st.info("No financial metrics available")
    
    with col2:
        st.markdown("#### 🏢 Company Information")
        if result.get('info'):
            info = result['info']
            
            # Create company info DataFrame
            info_data = []
            if info.get('name'):
                info_data.append(['Company Name', info['name']])
            if info.get('sector'):
                info_data.append(['Sector', info['sector']])
            if info.get('industry'):
                info_data.append(['Industry', info['industry']])
            if info.get('market_cap'):
                info_data.append(['Market Cap', f"${info['market_cap']:,.0f}" if info['market_cap'] else "N/A"])
            if info.get('employees'):
                info_data.append(['Employees', f"{info['employees']:,}" if info['employees'] else "N/A"])
            if info.get('country'):
                info_data.append(['Country', info['country']])
            if info.get('exchange'):
                info_data.append(['Exchange', info['exchange']])
            if info.get('currency'):
                info_data.append(['Currency', info['currency']])
            
            if info_data:
                info_df = pd.DataFrame(info_data, columns=['Attribute', 'Value'])
                st.dataframe(info_df, use_container_width=True, hide_index=True)
            else:
                st.info("No company information available")
    
    # Technical Analysis Section
    if result.get('technical_analysis'):
        st.markdown("#### 📈 Technical Analysis")
        tech_analysis = result['technical_analysis']
        
        col3, col4 = st.columns(2)
        
        with col3:
            st.markdown("**Price & Indicators**")
            tech_data = []
            if tech_analysis.get('current_price'):
                tech_data.append(['Current Price', f"${tech_analysis['current_price']:.2f}"])
            if tech_analysis.get('sma_20'):
                tech_data.append(['SMA 20', f"${tech_analysis['sma_20']:.2f}"])
            if tech_analysis.get('sma_50'):
                tech_data.append(['SMA 50', f"${tech_analysis['sma_50']:.2f}"])
            if tech_analysis.get('sma_200'):
                tech_data.append(['SMA 200', f"${tech_analysis['sma_200']:.2f}"])
            if tech_analysis.get('rsi'):
                tech_data.append(['RSI', f"{tech_analysis['rsi']:.2f}"])
            
            if tech_data:
                tech_df = pd.DataFrame(tech_data, columns=['Indicator', 'Value'])
                st.dataframe(tech_df, use_container_width=True, hide_index=True)
        
        with col4:
            st.markdown("**Technical Signals**")
            if result.get('technical_signals'):
                signals = result['technical_signals']
                signals_data = []
                if signals.get('trend'):
                    signals_data.append(['Trend', signals['trend']])
                if signals.get('momentum'):
                    signals_data.append(['Momentum', signals['momentum']])
                if signals.get('volatility'):
                    signals_data.append(['Volatility', signals['volatility']])
                if signals.get('volume'):
                    signals_data.append(['Volume', signals['volume']])
                
                if signals_data:
                    signals_df = pd.DataFrame(signals_data, columns=['Signal', 'Status'])
                    st.dataframe(signals_df, use_container_width=True, hide_index=True)
                else:
                    st.info("No technical signals available")
            else:
                st.info("No technical signals available")
    
    # Balance Sheet Summary
    if result.get('metrics'):
        metrics = result['metrics']
        balance_sheet_data = []
        
        if any(metrics.get(key) for key in ['total_assets', 'total_liabilities', 'total_equity']):
            st.markdown("#### 💰 Balance Sheet Summary")
            
            if metrics.get('total_assets'):
                balance_sheet_data.append(['Total Assets', f"${metrics['total_assets']:,.0f}"])
            if metrics.get('total_liabilities'):
                balance_sheet_data.append(['Total Liabilities', f"${metrics['total_liabilities']:,.0f}"])
            if metrics.get('total_equity'):
                balance_sheet_data.append(['Total Equity', f"${metrics['total_equity']:,.0f}"])
            
            if balance_sheet_data:
                balance_df = pd.DataFrame(balance_sheet_data, columns=['Item', 'Value'])
                st.dataframe(balance_df, use_container_width=True, hide_index=True)
    
    # Cash Flow Summary
    if result.get('metrics'):
        metrics = result['metrics']
        cash_flow_data = []
        
        if any(metrics.get(key) for key in ['operating_cash_flow', 'investing_cash_flow', 'financing_cash_flow', 'free_cash_flow']):
            st.markdown("#### 💸 Cash Flow Summary")
            
            if metrics.get('operating_cash_flow'):
                cash_flow_data.append(['Operating Cash Flow', f"${metrics['operating_cash_flow']:,.0f}"])
            if metrics.get('investing_cash_flow'):
                cash_flow_data.append(['Investing Cash Flow', f"${metrics['investing_cash_flow']:,.0f}"])
            if metrics.get('financing_cash_flow'):
                cash_flow_data.append(['Financing Cash Flow', f"${metrics['financing_cash_flow']:,.0f}"])
            if metrics.get('free_cash_flow'):
                cash_flow_data.append(['Free Cash Flow', f"${metrics['free_cash_flow']:,.0f}"])
            
            if cash_flow_data:
                cash_flow_df = pd.DataFrame(cash_flow_data, columns=['Cash Flow Type', 'Value'])
                st.dataframe(cash_flow_df, use_container_width=True, hide_index=True)
    
    # Display AI summary only if AI features are enabled
    if ENABLE_AI_FEATURES and result.get('summary'):
        st.markdown("#### 🤖 AI Analysis")
        st.write(result['summary'])

def display_technical_analysis(result: Dict[str, Any], technical_service: TechnicalAnalysisService) -> None:
    """Display technical analysis results."""
    if not ENABLE_TECHNICAL_ANALYSIS:
        st.info("Technical analysis features are currently disabled.")
        return
        
    if 'history' in result and not result['history'].empty:
        history_df = result['history']
        
        # Check if the DataFrame has the required columns
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_columns = [col for col in required_columns if col not in history_df.columns]
        
        if missing_columns:
            st.warning(f"Historical data is missing required columns: {', '.join(missing_columns)}")
            st.info("Technical analysis requires OHLCV data (Open, High, Low, Close, Volume)")
            return
        
        try:
            # Calculate technical indicators
            DebugUtils.info(f"Calculating technical indicators for {result['symbol']}")
            df = technical_service.calculate_technical_indicators(history_df)
            
            # Create and display price chart
            fig = technical_service.create_price_chart(df, result['symbol'])
            st.plotly_chart(fig, use_container_width=True)
            
            # Display technical signals
            signals = technical_service.get_technical_signals(df)
            st.markdown("### Technical Signals")
            for category, signal in signals.items():
                st.write(f"{category.title()}: {signal}")
                
        except Exception as e:
            DebugUtils.log_error(e, f"Error in technical analysis for {result['symbol']}")
            st.error(f"Error performing technical analysis: {str(e)}")
    else:
        st.info("No historical data available for technical analysis.")

def display_fundamental_analysis(result: Dict[str, Any], fundamental_service: FundamentalAnalysisService) -> None:
    """Display fundamental analysis results."""
    if not ENABLE_FUNDAMENTAL_ANALYSIS:
        st.info("Fundamental analysis features are currently disabled.")
        return
    
    try:
        # Calculate financial ratios
        ratios = fundamental_service.calculate_financial_ratios(result)
        
        if not ratios or all(not category_ratios for category_ratios in ratios.values()):
            st.info("No financial data available for fundamental analysis.")
            return
        
        # Display ratios by category
        for category, category_ratios in ratios.items():
            if category_ratios:  # Only display if there are ratios in this category
                st.markdown(f"### {category.title()} Ratios")
                ratio_df = pd.DataFrame([category_ratios])
                st.dataframe(ratio_df)
        
        # Display fundamental signals
        signals = fundamental_service.get_fundamental_signals(ratios)
        if signals:
            st.markdown("### Fundamental Signals")
            for category, signal in signals.items():
                st.write(f"{category.title()}: {signal}")
                
    except Exception as e:
        DebugUtils.log_error(e, f"Error in fundamental analysis for {result['symbol']}")
        st.error(f"Error performing fundamental analysis: {str(e)}")

def display_portfolio_analysis(result: Dict[str, Any], portfolio_service: PortfolioService) -> None:
    """Display portfolio analysis results."""
    if not ENABLE_PORTFOLIO_ANALYSIS:
        st.info("Portfolio analysis features are currently disabled.")
        return
    
    # Check if historical data is available
    history_df = result.get('history', pd.DataFrame())
    if history_df.empty or 'Close' not in history_df.columns:
        st.info("Portfolio analysis requires historical price data which is not available.")
        return
        
    try:
        # Create a sample portfolio with the current stock
        positions = [{
            'symbol': result['symbol'],
            'shares': 100,  # Sample position size
            'cost_basis': result.get('metrics', {}).get('current_price', 0),
            'sector': result.get('info', {}).get('sector', 'Unknown')
        }]
        
        prices = {result['symbol']: history_df}
        
        # Calculate portfolio metrics
        metrics = portfolio_service.calculate_portfolio_metrics(positions, prices)
        
        # Generate and display portfolio report
        report = portfolio_service.generate_portfolio_report(metrics)
        
        st.markdown("### Portfolio Summary")
        st.write(report['summary'])
        
        st.markdown("### Risk Analysis")
        st.write(report['risk_analysis'])
        
        st.markdown("### Performance Analysis")
        st.write(report['performance_analysis'])
        
        if report['recommendations']:
            st.markdown("### Recommendations")
            for rec in report['recommendations']:
                st.write(f"- {rec}")
                
    except Exception as e:
        DebugUtils.log_error(e, f"Error in portfolio analysis for {result['symbol']}")
        st.error(f"Error performing portfolio analysis: {str(e)}")

def display_download_options(result: Dict[str, Any], output_dir: Path) -> None:
    """Display download options for reports."""
    col1, col2 = st.columns(2)
    
    with col1:
        if result.get('word_report_path'):
            word_path = Path(result['word_report_path'])
            if word_path.exists():
                with open(word_path, 'rb') as f:
                    st.download_button(
                        label="Download Word Report",
                        data=f,
                        file_name=word_path.name,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
    
    with col2:
        if result.get('excel_report_path'):
            excel_path = Path(result['excel_report_path'])
            if excel_path.exists():
                with open(excel_path, 'rb') as f:
                    st.download_button(
                        label="Download Excel Report",
                        data=f,
                        file_name=excel_path.name,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

def display_error(error: str) -> None:
    """Display error message."""
    st.error(error)

def display_success(message: str) -> None:
    """Display a success message."""
    st.success(message)

def display_progress(progress: float, message: str) -> None:
    """Display a progress bar with message."""
    st.progress(progress)
    st.write(message) 