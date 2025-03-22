import os
import pandas as pd
from openpyxl import load_workbook


def generate_excel_report(stock_summaries, excel_filename):
    """Generate an Excel file summarizing stock analysis and append new data if file exists."""
    df = pd.DataFrame(
        stock_summaries,
        columns=["Serial Number", "Stock Name", "Overview", "Summary", "Decision"]
    )

    if os.path.exists(excel_filename):
        # Open the existing workbook and get the last row in the default sheet.
        book = load_workbook(excel_filename)

        with pd.ExcelWriter(
                excel_filename,
                engine="openpyxl",
                mode="a",
                if_sheet_exists="overlay"
        ) as writer:
            # Access the existing workbook and worksheet directly
            workbook = writer.book
            sheet_name = "Sheet1"  # Change if your sheet name differs
            worksheet = workbook[sheet_name]
            startrow = worksheet.max_row  # Last used row
            # Write without headers to append rows.
            df.to_excel(writer, index=False, header=False, startrow=startrow)
    else:
        # Create a new Excel file.
        df.to_excel(excel_filename, index=False)

    return excel_filename
