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
