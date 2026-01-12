@echo off
echo Starting Stock Analysis Tool...
echo.
echo Make sure you have Python and all dependencies installed.
echo If you haven't installed dependencies yet, run: pip install -r requirements.txt
echo.
pause
streamlit run ui/pages/main_page.py
pause
