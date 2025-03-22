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
    
    uploaded_file = st.file_uploader(
        "Upload Stock Symbols File",
        type=["txt", "csv"],
        help="Upload a file containing stock symbols (one per line)"
    )
    
    if not uploaded_file:
        return {"symbols": [], "analyze": False}
    
    # Process uploaded file
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
        symbols = df.iloc[:, 0].tolist()  # Assuming first column contains symbols
    else:
        symbols = [line.decode().strip() for line in uploaded_file.readlines()]
    
    st.write(f"Found {len(symbols)} symbols")
    st.write("First few symbols:", ", ".join(symbols[:5]))
    
    return {
        "symbols": symbols,
        "analyze": bool(st.button("Analyze All Stocks", type="primary"))
    }

def display_analysis_results(results: List[Dict[str, Any]], output_dir: Path) -> None:
    """Display analysis results and download options."""
    if not results:
        st.warning("No results to display.")
        return
    
    # Initialize services based on enabled features
    technical_service = TechnicalAnalysisService() if ENABLE_TECHNICAL_ANALYSIS else None
    fundamental_service = FundamentalAnalysisService() if ENABLE_FUNDAMENTAL_ANALYSIS else None
    portfolio_service = PortfolioService() if ENABLE_PORTFOLIO_ANALYSIS else None
    
    for result in results:
        st.subheader(f"Analysis Results for {result['symbol']}")
        
        # Create tabs based on enabled features
        tabs = ["Overview"]
        if ENABLE_TECHNICAL_ANALYSIS:
            tabs.append("Technical Analysis")
        if ENABLE_FUNDAMENTAL_ANALYSIS:
            tabs.append("Fundamental Analysis")
        if ENABLE_PORTFOLIO_ANALYSIS:
            tabs.append("Portfolio")
            
        tab_objects = st.tabs(tabs)
        
        # print(f"result: {result}")
        # Overview tab is always present
        with tab_objects[0]:
            display_overview(result)
        
        # print(f"result: {result}")
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
        
        st.markdown("---")

def display_overview(result: Dict[str, Any]) -> None:
    """Display overview of the analysis results."""
    # Display metrics in a table format
    if result.get('metrics'):
        metrics_df = pd.DataFrame([result['metrics']])
        st.dataframe(metrics_df)
    
    # Display AI summary only if AI features are enabled
    if ENABLE_AI_FEATURES and result.get('summary'):
        st.markdown("### AI Analysis")
        st.write(result['summary'])

def display_technical_analysis(result: Dict[str, Any], technical_service: TechnicalAnalysisService) -> None:
    """Display technical analysis results."""
    if not ENABLE_TECHNICAL_ANALYSIS:
        st.info("Technical analysis features are currently disabled.")
        return
        
    if 'history' in result:
        # Calculate technical indicators
        df = technical_service.calculate_technical_indicators(result['history'])
        
        # Create and display price chart
        fig = technical_service.create_price_chart(df, result['symbol'])
        st.plotly_chart(fig, use_container_width=True)
        
        # Display technical signals
        signals = technical_service.get_technical_signals(df)
        st.markdown("### Technical Signals")
        for category, signal in signals.items():
            st.write(f"{category.title()}: {signal}")

def display_fundamental_analysis(result: Dict[str, Any], fundamental_service: FundamentalAnalysisService) -> None:
    """Display fundamental analysis results."""
    if not ENABLE_FUNDAMENTAL_ANALYSIS:
        st.info("Fundamental analysis features are currently disabled.")
        return
        
    # Calculate financial ratios
    ratios = fundamental_service.calculate_financial_ratios(result)
    
    # Display ratios by category
    for category, category_ratios in ratios.items():
        st.markdown(f"### {category.title()} Ratios")
        ratio_df = pd.DataFrame([category_ratios])
        st.dataframe(ratio_df)
    
    # Display fundamental signals
    signals = fundamental_service.get_fundamental_signals(ratios)
    st.markdown("### Fundamental Signals")
    for category, signal in signals.items():
        st.write(f"{category.title()}: {signal}")

def display_portfolio_analysis(result: Dict[str, Any], portfolio_service: PortfolioService) -> None:
    """Display portfolio analysis results."""
    if not ENABLE_PORTFOLIO_ANALYSIS:
        st.info("Portfolio analysis features are currently disabled.")
        return
        
    # Create a sample portfolio with the current stock
    positions = [{
        'symbol': result['symbol'],
        'shares': 100,  # Sample position size
        'cost_basis': result.get('metrics', {}).get('current_price', 0),
        'sector': result.get('info', {}).get('sector', 'Unknown')
    }]
    
    prices = {result['symbol']: result.get('history', pd.DataFrame())}
    
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