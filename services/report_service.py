from docx import Document
from docx.shared import Pt
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import markdown
from bs4 import BeautifulSoup
import re
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path
import pandas as pd
from core.config import OUTPUT_DIR, ENABLE_AI_FEATURES
from constants.Constants import (
    FINANCIAL_STATEMENT_FILTER_KEYS,
    FINANCIAL_SHEET_NAMES
)
import os

class ReportService:
    def __init__(self):
        """Initialize the report service."""
        self.output_dir = Path(OUTPUT_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_word_report(self, symbol: str, data: Dict[str, Any]) -> Path:
        """Generate a Word report for the stock analysis."""
        doc = Document()
        
        # Add title
        doc.add_heading(f"Stock Analysis Report: {symbol}", 0)
        
        # Add company info
        if "info" in data:
            doc.add_heading("Company Information", level=1)
            for key, value in data["info"].items():
                doc.add_paragraph(f"{key}: {value}")
        
        # Add financial statements
        if "income_statement" in data and not data["income_statement"].empty:
            doc.add_heading("Income Statement", level=1)
            self._add_dataframe_to_doc(doc, data["income_statement"])
        
        if "balance_sheet" in data and not data["balance_sheet"].empty:
            doc.add_heading("Balance Sheet", level=1)
            self._add_dataframe_to_doc(doc, data["balance_sheet"])
        
        if "cashflow" in data and not data["cashflow"].empty:
            doc.add_heading("Cash Flow Statement", level=1)
            self._add_dataframe_to_doc(doc, data["cashflow"])
        
        # Add AI summary if available
        if ENABLE_AI_FEATURES and "summary" in data and data["summary"]:
            doc.add_heading("AI Analysis Summary", level=1)
            doc.add_paragraph(data["summary"])
        
        # Save the document
        output_path = self.output_dir / f"{symbol}_Analysis_Report.docx"
        doc.save(str(output_path))
        
        return output_path
    
    def generate_excel_report(self, stock_summaries: List[Dict[str, Any]], output_file: str = "stock_report.xlsx"):
        """Generate Excel report with stock data."""
        try:
            print(f"Generating Excel report with {len(stock_summaries)} stocks...")
            
            # Create Excel writer
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                # Create Overview sheet
                overview_data = []
                for stock_data in stock_summaries:
                    symbol = stock_data.get('symbol', '')
                    metrics = stock_data.get('metrics', {})
                    info = stock_data.get('info', {})
                    
                    # Format large numbers with commas and 2 decimal places
                    formatted_metrics = {
                        'Symbol': symbol,
                        'Company Name': info.get('longName', ''),
                        'Market Cap': f"{metrics.get('Market Cap', 0):,.2f}",
                        'Revenue': f"{metrics.get('Revenue', 0):,.2f}",
                        'Net Income': f"{metrics.get('Net Income', 0):,.2f}",
                        'Operating Income': f"{metrics.get('Operating Income', 0):,.2f}",
                        'Total Assets': f"{metrics.get('Total Assets', 0):,.2f}",
                        'Total Liabilities': f"{metrics.get('Total Liabilities', 0):,.2f}",
                        'Total Equity': f"{metrics.get('Total Equity', 0):,.2f}",
                        'Operating Cash Flow': f"{metrics.get('Operating Cash Flow', 0):,.2f}",
                        'Investing Cash Flow': f"{metrics.get('Investing Cash Flow', 0):,.2f}",
                        'Financing Cash Flow': f"{metrics.get('Financing Cash Flow', 0):,.2f}"
                    }
                    overview_data.append(formatted_metrics)
                
                overview_df = pd.DataFrame(overview_data)
                overview_df.to_excel(writer, sheet_name='Overview', index=False)
                
                # Create Company Info sheet
                company_info_data = []
                for stock_data in stock_summaries:
                    symbol = stock_data.get('symbol', '')
                    info = stock_data.get('info', {})
                    
                    # Create a flat structure for nested dictionaries
                    flat_info = {
                        'Symbol': symbol,
                        'Company Name': info.get('longName', ''),
                        'Sector': info.get('sector', ''),
                        'Industry': info.get('industry', ''),
                        'Country': info.get('country', ''),
                        'Currency': info.get('currency', ''),
                        'Exchange': info.get('exchange', ''),
                        'Website': info.get('website', ''),
                        'Phone': info.get('phone', ''),
                        'Address': info.get('address1', ''),
                        'City': info.get('city', ''),
                        'State': info.get('state', ''),
                        'Zip': info.get('zip', ''),
                        'Description': info.get('longBusinessSummary', '')
                    }
                    company_info_data.append(flat_info)
                
                company_info_df = pd.DataFrame(company_info_data)
                company_info_df.to_excel(writer, sheet_name='Company Info', index=False)
                
                # Create Technical Analysis sheet
                technical_data = []
                for stock_data in stock_summaries:
                    symbol = stock_data.get('symbol', '')
                    technical = stock_data.get('technical_analysis', {})
                    
                    # Get technical signals
                    signals = stock_data.get('technical_signals', {})
                    
                    technical_info = {
                        'Symbol': symbol,
                        'Current Price': f"{technical.get('Current_Price', 0):,.2f}",
                        'SMA_20': f"{technical.get('SMA_20', 0):,.2f}",
                        'SMA_50': f"{technical.get('SMA_50', 0):,.2f}",
                        'SMA_200': f"{technical.get('SMA_200', 0):,.2f}",
                        'RSI': f"{technical.get('RSI', 0):,.2f}",
                        'MACD': f"{technical.get('MACD', 0):,.2f}",
                        'BB_Upper': f"{technical.get('BB_Upper', 0):,.2f}",
                        'BB_Middle': f"{technical.get('BB_Middle', 0):,.2f}",
                        'BB_Lower': f"{technical.get('BB_Lower', 0):,.2f}",
                        'Volume': f"{technical.get('Volume', 0):,.0f}",
                        'Trend Signal': signals.get('trend', ''),
                        'Momentum Signal': signals.get('momentum', ''),
                        'Volatility Signal': signals.get('volatility', ''),
                        'Volume Signal': signals.get('volume', '')
                    }
                    technical_data.append(technical_info)
                
                technical_df = pd.DataFrame(technical_data)
                technical_df.to_excel(writer, sheet_name='Technical Analysis', index=False)
                
                # Create Fundamental Analysis sheet
                fundamental_data = []
                for stock_data in stock_summaries:
                    symbol = stock_data.get('symbol', '')
                    fundamental = stock_data.get('fundamental_analysis', {})
                    
                    fundamental_info = {
                        'Symbol': symbol,
                        'Net Profit Margin (%)': f"{fundamental.get('Net_Profit_Margin', 0):,.2f}",
                        'Operating Margin (%)': f"{fundamental.get('Operating_Margin', 0):,.2f}",
                        'Current Ratio': f"{fundamental.get('Current_Ratio', 0):,.2f}",
                        'Debt Ratio': f"{fundamental.get('Debt_Ratio', 0):,.2f}",
                        'P/E Ratio': f"{fundamental.get('P/E_Ratio', 0):,.2f}",
                        'Revenue Growth (%)': f"{fundamental.get('Revenue_Growth', 0):,.2f}"
                    }
                    fundamental_data.append(fundamental_info)
                
                fundamental_df = pd.DataFrame(fundamental_data)
                fundamental_df.to_excel(writer, sheet_name='Fundamental Analysis', index=False)
                
                # Create Portfolio Analysis sheet
                portfolio_data = []
                for stock_data in stock_summaries:
                    symbol = stock_data.get('symbol', '')
                    portfolio = stock_data.get('portfolio_analysis', {})
                    
                    portfolio_info = {
                        'Symbol': symbol,
                        'Volatility (%)': f"{portfolio.get('Volatility', 0):,.2f}",
                        'Total Return (%)': f"{portfolio.get('Total_Return', 0):,.2f}",
                        'Dividend Yield (%)': f"{portfolio.get('Dividend_Yield', 0):,.2f}",
                        'Market Cap': f"{portfolio.get('Market_Cap', 0):,.2f}",
                        'Beta': f"{portfolio.get('Beta', 0):,.2f}"
                    }
                    portfolio_data.append(portfolio_info)
                
                portfolio_df = pd.DataFrame(portfolio_data)
                portfolio_df.to_excel(writer, sheet_name='Portfolio Analysis', index=False)
                
                # Create Financial Statements sheets for each stock
                for stock_data in stock_summaries:
                    symbol = stock_data.get('symbol', '')
                    print(f"Processing financial statements for {symbol}")
                    
                    # Process yearly statements
                    for statement_type in ['income_statement', 'balance_sheet', 'cashflow']:
                        key = f'yearly_{statement_type}'
                        if key in stock_data and not stock_data[key].empty:
                            sheet_name = f"{symbol} {FINANCIAL_SHEET_NAMES['yearly'][statement_type]}"
                            print(f"Writing {sheet_name}")
                            stock_data[key].to_excel(writer, sheet_name=sheet_name)
                    
                    # Process quarterly statements
                    for statement_type in ['income_statement', 'balance_sheet', 'cashflow']:
                        key = f'quarterly_{statement_type}'
                        if key in stock_data and not stock_data[key].empty:
                            sheet_name = f"{symbol} {FINANCIAL_SHEET_NAMES['quarterly'][statement_type]}"
                            print(f"Writing {sheet_name}")
                            stock_data[key].to_excel(writer, sheet_name=sheet_name)
                
                # Format all sheets
                for sheet_name in writer.sheets:
                    sheet = writer.sheets[sheet_name]
                    self._format_sheet(sheet)
            
            print(f"Excel report generated successfully: {output_file}")
            return output_file
            
        except Exception as e:
            print(f"Error generating Excel report: {str(e)}")
            raise
    
    def _add_dataframe_to_doc(self, doc: Document, df: pd.DataFrame) -> None:
        """Add a DataFrame to a Word document."""
        if df.empty:
            doc.add_paragraph("No data available")
            return
        
        # Convert DataFrame to table
        table = doc.add_table(rows=1, cols=len(df.columns) + 1)
        table.style = 'Table Grid'
        
        # Add headers
        header_cells = table.rows[0].cells
        header_cells[0].text = "Metric"
        for i, col in enumerate(df.columns):
            header_cells[i + 1].text = str(col)
        
        # Add data
        for idx, row in df.iterrows():
            row_cells = table.add_row().cells
            row_cells[0].text = str(idx)
            for i, value in enumerate(row):
                row_cells[i + 1].text = str(value)

    def _add_company_overview(self, doc: Document, data: Dict[str, Any]) -> None:
        """Add company overview section to the document."""
        doc.add_heading("Company Overview", level=2)
        info = data.get("info", {})
        
        overview_fields = [
            ("Name", "longName"),
            ("Business Summary", "longBusinessSummary"),
            ("Sector", "sector"),
            ("Industry", "industry"),
            ("Market Cap", "marketCap"),
            ("PE Ratio", "trailingPE"),
            ("Dividend Yield", "dividendYield"),
            ("Website", "website")
        ]

        for label, key in overview_fields:
            value = info.get(key, 'N/A')
            doc.add_paragraph().add_run(f"{label}: ").add_text(str(value))

    def _add_news_section(self, doc: Document, data: Dict[str, Any]) -> None:
        """Add news section to the document."""
        doc.add_heading("Recent News", level=2)
        news = data.get("news", [])

        if not news:
            doc.add_paragraph("No recent news available.")
            return

        for news_elem in news:
            article = news_elem.get('content', {})
            pub_time = article.get("pubDate", "Unknown Date")

            if pub_time != "Unknown Date":
                pub_time = datetime.strptime(pub_time, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M:%S")

            p = doc.add_paragraph(f" {article.get('title', 'No Title')}")
            p.style = "List Bullet"

            doc.add_paragraph(f"  {article.get('summary', 'Unknown')}")
            doc.add_paragraph(f"  Source: {article.get('provider', {}).get('displayName', 'Unknown')}")
            doc.add_paragraph(f"  Published: {pub_time}")
            doc.add_paragraph(f"  URL: {article.get('canonicalUrl', {}).get('url', 'Unknown')}\n")

    def _markdown_to_docx(self, md_text: str, doc: Document) -> None:
        """Convert Markdown to Word document format."""
        html_text = markdown.markdown(md_text)
        soup = BeautifulSoup(html_text, "html.parser")

        for elem in soup.children:
            if elem.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                level = int(elem.name[1])
                doc.add_paragraph(elem.text, style=f"Heading {level}")
            elif elem.name == "p":
                self._process_paragraph(doc, elem)
            elif elem.name == "pre":
                p = doc.add_paragraph()
                run = p.add_run(elem.text.strip())
                run.font.name = "Courier New"
            elif elem.name == "ul":
                for li in elem.find_all("li"):
                    doc.add_paragraph(li.text, style="ListBullet")
            elif elem.name == "ol":
                for li in elem.find_all("li"):
                    text = re.sub(r'^\d+\.?\s*', '', li.text)
                    doc.add_paragraph(text, style="ListNumber")
            elif elem.name == "blockquote":
                p = doc.add_paragraph()
                run = p.add_run(elem.text)
                p.paragraph_format.left_indent = Pt(20)
                run.italic = True
            elif elem.name == "a":
                p = doc.add_paragraph()
                self._add_hyperlink(p, elem["href"], elem.text)

    def _process_paragraph(self, doc: Document, elem: BeautifulSoup) -> None:
        """Process a paragraph with mixed formatting."""
        p = doc.add_paragraph()
        for part in elem.contents:
            if part.name == "strong":
                run = p.add_run(part.text)
                run.bold = True
            elif part.name == "em":
                run = p.add_run(part.text)
                run.italic = True
            elif part.name == "code":
                run = p.add_run(part.text)
                run.font.name = "Courier New"
            else:
                run = p.add_run(part)

    def _add_hyperlink(self, paragraph: Document, url: str, text: str) -> None:
        """Add a clickable hyperlink to the document."""
        run = paragraph.add_run(text)
        run.font.color.rgb = (0, 0, 255)
        run.underline = True
        part = paragraph._p
        hyperlink = OxmlElement("w:hyperlink")
        hyperlink.set(qn("r:id"), url)
        part.append(hyperlink) 