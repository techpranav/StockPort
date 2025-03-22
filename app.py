import streamlit as st
import pandas as pd
from main import process_stock_symbol
import time
from reports.generate_excel import generate_excel_report
from util.googledrive import uploadFilesToDrive
from util.Utils import getOutputDirectory
import os

# Set page config
st.set_page_config(
    page_title="Stock Analyzer",
    page_icon="📈",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        margin-top: 10px;
    }
    .main {
        padding: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

def main():
    st.title("📈 Stock Analyzer")
    st.markdown("---")

    # Sidebar for parameter selection
    with st.sidebar:
        st.header("Export Parameters")
        export_params = {
            "Basic Info": st.checkbox("Basic Information", value=True),
            "Financial Statements": st.checkbox("Financial Statements", value=True),
            "Technical Analysis": st.checkbox("Technical Analysis", value=True),
            "AI Recommendations": st.checkbox("AI Recommendations", value=True)
        }

    # Main content area
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Single Stock Analysis")
        symbol = st.text_input("Enter Stock Symbol (e.g., AAPL, MSFT)", "").strip()
        
        if st.button("Analyze Stock"):
            if symbol:
                with st.spinner(f"Analyzing {symbol}..."):
                    try:
                        result = process_stock_symbol(symbol)
                        st.success(f"Analysis completed for {symbol}")
                        
                        # Display results
                        st.subheader("Analysis Results")
                        st.write(f"**Symbol:** {result['symbol']}")
                        
                        # Download button for individual stock report
                        directory = os.path.join(getOutputDirectory(), symbol)
                        word_file = os.path.join(directory, f"{symbol}_Analysis_Report.docx")
                        if os.path.exists(word_file):
                            with open(word_file, 'rb') as f:
                                st.download_button(
                                    label="Download Word Report",
                                    data=f,
                                    file_name=f"{symbol}_Analysis_Report.docx",
                                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                                )
                    except Exception as e:
                        st.error(f"Error analyzing {symbol}: {str(e)}")
            else:
                st.warning("Please enter a stock symbol")

    with col2:
        st.subheader("Mass Analysis")
        uploaded_file = st.file_uploader("Upload CSV with Stock Symbols", type=['csv'])
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                symbols = df.iloc[:, 0].tolist()  # Assuming first column contains symbols
                st.write(f"Found {len(symbols)} symbols")
                
                if st.button("Analyze All Stocks"):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    results = []
                    for i, symbol in enumerate(symbols):
                        try:
                            status_text.text(f"Processing {symbol}...")
                            result = process_stock_symbol(symbol)
                            results.append(result)
                            progress_bar.progress((i + 1) / len(symbols))
                            time.sleep(1)  # Rate limiting
                        except Exception as e:
                            st.error(f"Error processing {symbol}: {str(e)}")
                    
                    st.success("Mass analysis completed!")
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")

    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center'>
            <p>Stock Analyzer v1.0 | Powered by AI</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 