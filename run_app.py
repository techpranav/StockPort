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
    print(f"\nAccess the app from other computers using:")
    print(f"http://{ip_address}:8501\n")
    
    # Set the host to '0.0.0.0' to make it accessible from other machines
    # Set the port to 8501 (default Streamlit port)
    os.system('streamlit run app/main.py --server.address 0.0.0.0 --server.port 8501') 