# 🚀 Quick Start Guide for End Users

Welcome to the Stock Analysis Tool! This guide will help you get started in just a few minutes.

## 📋 What You Need

- **Windows 10/11** or **macOS** or **Linux**
- **Internet connection** (for stock data and Python installation)
- **Google account** (optional, for automatic report uploads)

## 🎯 Quick Installation (Choose Your System)

### Windows Users (Recommended)
1. **Download** the tool folder to your computer
2. **Double-click** `EASY_INSTALL.bat` (automatically installs Python if needed)
3. **Wait** for installation to complete (5-15 minutes, including Python)
4. **The tool will open automatically** in your web browser

### Windows Users (Alternative)
1. **Download** the tool folder to your computer
2. **Double-click** `install_and_run.bat` (automatically installs Python if needed)
3. **Wait** for installation to complete
4. **The tool will open automatically** in your web browser

### macOS/Linux Users
1. **Download** the tool folder to your computer
2. **Open Terminal** and navigate to the tool folder
3. **Run**: `chmod +x install_and_run.sh`
4. **Run**: `./install_and_run.sh` (automatically installs Python if needed)
5. **The tool will open automatically** in your web browser

## 🔧 First Time Setup

1. **Wait** for the installation to complete (this may take 5-15 minutes)
   - **First time**: Python + dependencies (10-15 minutes)
   - **Subsequent times**: Just dependencies (5-10 minutes)
2. **The tool opens** in your web browser at `http://localhost:8501`
3. **You're ready to analyze stocks!**

## 🐍 Python Installation (Automatic!)

**Good news!** The tool automatically:
- ✅ **Detects** if Python is installed
- ✅ **Downloads** Python 3.11.8 if needed
- ✅ **Installs** Python with optimal settings
- ✅ **Configures** PATH automatically
- ✅ **Installs** pip package manager
- ✅ **Creates** virtual environment
- ✅ **Installs** all required packages

**No technical knowledge required!** Just run the installer and wait.

## 📊 How to Use the Tool

### Single Stock Analysis
1. **Enter a stock symbol** (e.g., AAPL for Apple, MSFT for Microsoft)
2. **Click "Analyze"**
3. **View results** in organized tabs
4. **Download reports** in Excel or Word format

### Mass Stock Analysis
1. **Create a text file** with stock symbols (one per line)
2. **Upload the file** using the file uploader
3. **Click "Analyze All"**
4. **Monitor progress** and view live results
5. **Download individual or combined reports**

## 🚀 Starting the Tool Again

### Windows
- **Double-click** `launch_tool.bat`

### macOS/Linux
- **Double-click** `launch_tool.sh` or run `./launch_tool.sh` in Terminal

## 📁 What Gets Created

The tool creates these folders automatically:
- `venv/` - Python environment (don't delete)
- `output/` - Your generated reports
- `logs/` - Tool activity logs

## 🆘 Need Help?

### Common Issues

**"Python not found"**
- The tool should install Python automatically
- If it fails, download Python from: https://www.python.org/downloads/
- Make sure to check "Add Python to PATH" during installation

**"Tool won't start"**
- Make sure you ran the installation script first
- Check that your antivirus isn't blocking the tool
- Try running as administrator (Windows)
- Try the PowerShell version: `install_and_run.ps1`

**"Can't download reports"**
- Check that you have write permissions in the folder
- Make sure your antivirus isn't blocking file creation

**"Stock data not loading"**
- Check your internet connection
- Verify the stock symbol is correct
- Some stocks may have limited data availability

**"Installation takes too long"**
- First installation includes Python (10-15 minutes)
- Subsequent installations are much faster (5-10 minutes)
- Check your internet speed

### Getting Support

1. **Check this guide** first
2. **Look at the logs** in the `logs/` folder
3. **Restart the tool** if it seems stuck
4. **Contact support** with specific error messages

## 🎉 You're All Set!

The Stock Analysis Tool is now ready to use. Start by analyzing a single stock to get familiar with the interface, then try mass analysis for multiple stocks.

**Happy Analyzing! 📈**
