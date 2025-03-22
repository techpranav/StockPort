from docx import Document
from docx.shared import Pt
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import markdown
from bs4 import BeautifulSoup
import re
from datetime import datetime
from typing import Dict, Any
from pathlib import Path
import pandas as pd
from core.config import OUTPUT_DIR, ENABLE_AI_FEATURES

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
        if "income_stmt" in data and not data["income_stmt"].empty:
            doc.add_heading("Income Statement", level=1)
            self._add_dataframe_to_doc(doc, data["income_stmt"])
        
        if "balance_sheet" in data and not data["balance_sheet"].empty:
            doc.add_heading("Balance Sheet", level=1)
            self._add_dataframe_to_doc(doc, data["balance_sheet"])
        
        if "cash_flow" in data and not data["cash_flow"].empty:
            doc.add_heading("Cash Flow Statement", level=1)
            self._add_dataframe_to_doc(doc, data["cash_flow"])
        
        # Add AI summary if available
        if ENABLE_AI_FEATURES and "summary" in data and data["summary"]:
            doc.add_heading("AI Analysis Summary", level=1)
            doc.add_paragraph(data["summary"])
        
        # Save the document
        output_path = self.output_dir / f"{symbol}_Analysis_Report.docx"
        doc.save(str(output_path))
        
        return output_path
    
    def generate_excel_report(self, symbol: str, data: Dict[str, Any]) -> Path:
        """Generate Excel report with financial data."""
        try:
            # Create output directory if it doesn't exist
            output_dir = Path(OUTPUT_DIR)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Create Excel file path
            excel_file = output_dir / f"{symbol}_Analysis_Report.xlsx"
            
            # Create Excel writer
            with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                # Write company info
                if 'info' in data:
                    info_df = pd.DataFrame([data['info']])
                    info_df.to_excel(writer, sheet_name='Company Info', index=False)
                
                # Write metrics
                if 'metrics' in data:
                    metrics_df = pd.DataFrame([data['metrics']])
                    metrics_df.to_excel(writer, sheet_name='Key Metrics', index=False)
                
                # Write yearly financial statements
                if 'yearly_income_stmt' in data and not data['yearly_income_stmt'].empty:
                    data['yearly_income_stmt'].to_excel(writer, sheet_name='Yearly Income Statement', index=True)
                
                if 'yearly_balance_sheet' in data and not data['yearly_balance_sheet'].empty:
                    data['yearly_balance_sheet'].to_excel(writer, sheet_name='Yearly Balance Sheet', index=True)
                
                if 'yearly_cash_flow' in data and not data['yearly_cash_flow'].empty:
                    data['yearly_cash_flow'].to_excel(writer, sheet_name='Yearly Cash Flow', index=True)
                
                # Write quarterly financial statements
                if 'quarterly_income_stmt' in data and not data['quarterly_income_stmt'].empty:
                    data['quarterly_income_stmt'].to_excel(writer, sheet_name='Quarterly Income Statement', index=True)
                
                if 'quarterly_balance_sheet' in data and not data['quarterly_balance_sheet'].empty:
                    data['quarterly_balance_sheet'].to_excel(writer, sheet_name='Quarterly Balance Sheet', index=True)
                
                if 'quarterly_cash_flow' in data and not data['quarterly_cash_flow'].empty:
                    data['quarterly_cash_flow'].to_excel(writer, sheet_name='Quarterly Cash Flow', index=True)
            
            return excel_file
            
        except Exception as e:
            raise Exception(f"Error generating Excel report: {str(e)}")
    
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