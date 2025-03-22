from setuptools import setup, find_packages

setup(
    name="stock_analyzer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "streamlit>=1.24.0",
        "yfinance>=0.2.18",
        "pandas>=1.5.3",
        "openpyxl>=3.1.2",
        "python-docx>=0.8.11",
        "openai>=0.27.8",
        "requests>=2.28.2",
        "beautifulsoup4>=4.12.2",
        "python-dateutil>=2.8.2",
        "pydrive>=1.3.1",
        "pydrive2>=1.9.1",
        "markdown>=3.4.3"
    ],
    python_requires=">=3.8",
) 