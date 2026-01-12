#!/bin/bash

# Stock Analysis Tool - Complete Installation Script
# For macOS and Linux users

echo "========================================"
echo "   Stock Analysis Tool Setup"
echo "========================================"
echo

# Function to detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    else
        echo "unknown"
    fi
}

# Function to install Python on Linux
install_python_linux() {
    echo "🔧 Installing Python on Linux..."
    
    # Try different package managers
    if command -v apt-get &> /dev/null; then
        echo "📦 Using apt-get (Ubuntu/Debian)..."
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip python3-venv python3-dev build-essential
    elif command -v yum &> /dev/null; then
        echo "📦 Using yum (CentOS/RHEL)..."
        sudo yum install -y python3 python3-pip python3-devel gcc
    elif command -v dnf &> /dev/null; then
        echo "📦 Using dnf (Fedora)..."
        sudo dnf install -y python3 python3-pip python3-devel gcc
    elif command -v pacman &> /dev/null; then
        echo "📦 Using pacman (Arch Linux)..."
        sudo pacman -S --noconfirm python python-pip python-virtualenv base-devel
    else
        echo "❌ No supported package manager found"
        echo "Please install Python 3.8+ manually from: https://www.python.org/downloads/"
        exit 1
    fi
}

# Function to install Python on macOS
install_python_macos() {
    echo "🔧 Installing Python on macOS..."
    
    if command -v brew &> /dev/null; then
        echo "📦 Using Homebrew..."
        brew install python3
    else
        echo "📦 Installing Homebrew first..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        echo "📦 Installing Python via Homebrew..."
        brew install python3
    fi
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo
    echo "🔧 Automatically installing Python..."
    echo
    
    OS_TYPE=$(detect_os)
    
    if [[ "$OS_TYPE" == "linux" ]]; then
        install_python_linux
    elif [[ "$OS_TYPE" == "macos" ]]; then
        install_python_macos
    else
        echo "❌ Unsupported operating system"
        echo "Please install Python 3.8+ manually from: https://www.python.org/downloads/"
        exit 1
    fi
    
    # Verify installation
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python installation failed"
        echo "Please install Python manually and try again"
        exit 1
    fi
    
    echo "✅ Python installed successfully!"
else
    echo "✅ Python found:"
    python3 --version
fi

echo

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not available"
    echo
    echo "🔧 Installing pip..."
    python3 -m ensurepip --upgrade
    if ! command -v pip3 &> /dev/null; then
        echo "❌ Failed to install pip"
        echo "Please reinstall Python and ensure pip is included"
        exit 1
    fi
    echo "✅ pip installed"
else
    echo "✅ pip3 found"
fi

echo

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

echo

# Activate virtual environment and install dependencies
echo "🔧 Installing dependencies..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

echo "✅ Virtual environment activated"
echo

# Upgrade pip
echo "🔧 Upgrading pip..."
python -m pip install --upgrade pip

# Install requirements
echo "🔧 Installing required packages..."
echo "⏳ This may take 5-10 minutes on first run..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    echo
    echo "Trying alternative installation method..."
    pip install --user -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Installation failed completely"
        echo
        echo "Common solutions:"
        echo "1. Check your internet connection"
        echo "2. Try running with sudo (Linux)"
        echo "3. Update your system packages"
        echo
        exit 1
    fi
fi

echo "✅ Dependencies installed successfully"
echo

# Launch the application
echo "🚀 Launching Stock Analysis Tool..."
echo
echo "The tool will open in your default web browser."
echo "If it doesn't open automatically, go to: http://localhost:8501"
echo
echo "To stop the tool, press Ctrl+C"
echo

# Launch Streamlit
streamlit run ui/pages/main_page.py

echo
echo "Tool stopped."
