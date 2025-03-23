import pandas as pd
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

class ExcelService:
    def generate_excel_report(self, symbol: str, data: Dict[str, Any], filename: Path) -> Path:
        """Generate an Excel report with financial data."""
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Company Info
            info = data.get("info", {})
            info_df = pd.DataFrame([info])
            info_df.to_excel(writer, sheet_name='Company Info', index=False)
            
            # Yearly Financials
            if 'yearly_financials' in data:
                yearly_financials = pd.DataFrame(data['yearly_financials'])
                yearly_financials.to_excel(writer, sheet_name='Yearly Financials', index=True)
            
            # Quarterly Financials
            if 'quarterly_financials' in data:
                quarterly_financials = pd.DataFrame(data['quarterly_financials'])
                quarterly_financials.to_excel(writer, sheet_name='Quarterly Financials', index=True)
            
            # Yearly Balance Sheet
            if 'yearly_balance_sheet' in data:
                yearly_balance = pd.DataFrame(data['yearly_balance_sheet'])
                yearly_balance.to_excel(writer, sheet_name='Yearly Balance Sheet', index=True)
            
            # Quarterly Balance Sheet
            if 'quarterly_balance_sheet' in data:
                quarterly_balance = pd.DataFrame(data['quarterly_balance_sheet'])
                quarterly_balance.to_excel(writer, sheet_name='Quarterly Balance Sheet', index=True)
            
            # Yearly Cash Flow
            if 'yearly_cashflow' in data:
                yearly_cash = pd.DataFrame(data['yearly_cashflow'])
                yearly_cash.to_excel(writer, sheet_name='Yearly Cash Flow', index=True)
            
            # Quarterly Cash Flow
            if 'quarterly_cashflow' in data:
                quarterly_cash = pd.DataFrame(data['quarterly_cashflow'])
                quarterly_cash.to_excel(writer, sheet_name='Quarterly Cash Flow', index=True)
            
            # Historical Data
            if 'historical_data' in data:
                historical = pd.DataFrame(data['historical_data'])
                historical.to_excel(writer, sheet_name='Historical Data', index=True)
            
            # News
            if 'news' in data:
                news_data = []
                for news_item in data['news']:
                    content = news_item.get('content', {})
                    news_data.append({
                        'Title': content.get('title', ''),
                        'Summary': content.get('summary', ''),
                        'Source': content.get('provider', {}).get('displayName', ''),
                        'Published': content.get('pubDate', ''),
                        'URL': content.get('canonicalUrl', {}).get('url', '')
                    })
                news_df = pd.DataFrame(news_data)
                news_df.to_excel(writer, sheet_name='News', index=False)
        
        return filename 