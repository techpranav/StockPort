# 🌐 Server Deployment Guide

This guide helps you deploy the Stock Analysis Tool on a server so multiple users can access it through their web browsers.

## 🎯 Deployment Options

### Option 1: Local Network Server (Recommended for Teams)
- **Users access via**: `http://YOUR_SERVER_IP:8501`
- **Best for**: Office teams, small organizations
- **Security**: Only accessible within your network

### Option 2: Internet Server (Advanced)
- **Users access via**: `http://YOUR_DOMAIN.com:8501`
- **Best for**: Remote teams, public access
- **Security**: Requires proper firewall and SSL setup

## 🖥️ Server Requirements

- **OS**: Windows Server, Linux (Ubuntu/CentOS), or macOS
- **Python**: 3.8 or higher
- **RAM**: Minimum 4GB, recommended 8GB+
- **Storage**: 10GB+ free space
- **Network**: Stable internet connection

## 🚀 Quick Server Setup

### Step 1: Prepare the Server

1. **Download** the tool to your server
2. **Install Python** if not already installed
3. **Open terminal/command prompt** in the tool folder

### Step 2: Install Dependencies

**Windows Server:**
```cmd
install_and_run.bat
```

**Linux/macOS Server:**
```bash
chmod +x install_and_run.sh
./install_and_run.sh
```

### Step 3: Configure for Server Use

1. **Stop the tool** (Ctrl+C)
2. **Edit the launch command** to bind to all network interfaces

**Windows Server:**
```cmd
streamlit run ui/pages/main_page.py --server.address 0.0.0.0 --server.port 8501
```

**Linux/macOS Server:**
```bash
streamlit run ui/pages/main_page.py --server.address 0.0.0.0 --server.port 8501
```

### Step 4: Start the Server

**Windows Server:**
```cmd
start_server.bat
```

**Linux/macOS Server:**
```bash
./start_server.sh
```

## 🔧 Advanced Server Configuration

### Create a Server Launch Script

**Windows Server (`start_server.bat`):**
```batch
@echo off
title Stock Analysis Tool - Server Mode
color 0C

echo ========================================
echo    Stock Analysis Tool - SERVER MODE
echo ========================================
echo.
echo 🌐 Server will be accessible at:
echo    http://YOUR_SERVER_IP:8501
echo.
echo 🔒 Make sure your firewall allows port 8501
echo.
echo 🚀 Starting server...
echo.

call venv\Scripts\activate.bat
streamlit run ui/pages/main_page.py --server.address 0.0.0.0 --server.port 8501

echo.
echo Server stopped. Press any key to exit...
pause >nul
```

**Linux/macOS Server (`start_server.sh`):**
```bash
#!/bin/bash

echo "========================================"
echo "   Stock Analysis Tool - SERVER MODE"
echo "========================================"
echo
echo "🌐 Server will be accessible at:"
echo "   http://YOUR_SERVER_IP:8501"
echo
echo "🔒 Make sure your firewall allows port 8501"
echo
echo "🚀 Starting server..."
echo

source venv/bin/activate
streamlit run ui/pages/main_page.py --server.address 0.0.0.0 --server.port 8501

echo
echo "Server stopped."
```

### Configure Firewall

**Windows Server:**
1. **Open Windows Defender Firewall**
2. **Add new rule** for port 8501
3. **Allow TCP connections** on port 8501

**Linux Server (Ubuntu):**
```bash
sudo ufw allow 8501
sudo ufw enable
```

**macOS Server:**
1. **System Preferences** → **Security & Privacy** → **Firewall**
2. **Add application** and allow incoming connections

### Find Your Server IP

**Windows Server:**
```cmd
ipconfig
```

**Linux/macOS Server:**
```bash
ifconfig
# or
ip addr show
```

## 👥 User Access Instructions

### For Your Users

1. **Users open their web browser**
2. **Navigate to**: `http://YOUR_SERVER_IP:8501`
3. **Start analyzing stocks!**

### Example URLs

- **Local network**: `http://192.168.1.100:8501`
- **Office server**: `http://10.0.0.50:8501`
- **Cloud server**: `http://YOUR_PUBLIC_IP:8501`

## 🔒 Security Considerations

### Network Security
- **Use VPN** for remote access
- **Restrict access** to specific IP ranges
- **Monitor access logs**

### Application Security
- **Regular updates** of Python packages
- **Monitor tool logs** for unusual activity
- **Backup reports** regularly

## 📊 Performance Optimization

### For Multiple Users
- **Increase server resources** (RAM, CPU)
- **Use SSD storage** for faster report generation
- **Monitor server performance** during peak usage

### Recommended Server Specs
- **CPU**: 4+ cores
- **RAM**: 16GB+
- **Storage**: 50GB+ SSD
- **Network**: 100Mbps+ connection

## 🆘 Troubleshooting

### Common Server Issues

**"Can't access from other computers"**
- Check firewall settings
- Verify server IP address
- Ensure Streamlit is bound to `0.0.0.0`

**"Tool is slow with multiple users"**
- Increase server resources
- Check network bandwidth
- Monitor server performance

**"Port 8501 is blocked"**
- Configure firewall to allow the port
- Check if another service is using the port
- Try a different port (e.g., 8502)

### Server Maintenance

1. **Regular restarts** (weekly recommended)
2. **Update Python packages** monthly
3. **Monitor disk space** and logs
4. **Backup important reports**

## 🎉 You're Ready!

Your Stock Analysis Tool is now accessible to your team via the server. Users can simply open their browsers and start analyzing stocks without installing anything on their local machines.

**Happy Server Deployment! 🌐**
