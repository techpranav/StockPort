import streamlit as st
from ui.pages.main_page import main
import os
import socket
import sys
from pathlib import Path

def get_local_ip():
    """Get the local IP address of the computer."""
    try:
        # Get the hostname
        hostname = socket.gethostname()
        # Get the IP address
        ip_address = socket.gethostbyname(hostname)
        return ip_address
    except:
        return "Could not determine IP address"

if __name__ == "__main__":
    # Add the project root directory to Python path
    project_root = Path(__file__).parent
    sys.path.append(str(project_root))
    
    # Get the local IP address
    ip_address = get_local_ip()
    print(f"\n{'='*60}")
    print(f"Stock Analysis Tool - Starting Server")
    print(f"{'='*60}")
    print(f"\nLocal access:    http://localhost:8501")
    print(f"Network access:  http://{ip_address}:8501")
    print(f"\n{'='*60}\n")
    
    # Use localhost for local access, but still allow network access via 0.0.0.0
    # This makes it accessible from other machines while showing localhost in the URL
    os.system('streamlit run app.py --server.address 0.0.0.0 --server.port 8501') 