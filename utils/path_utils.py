"""
Path Utilities

This module contains utility functions for managing file and directory paths.
"""

import os
from pathlib import Path
from datetime import datetime
from config.constants.StringConstants import output_dir

def get_symbol_output_directory(stock_symbol: str) -> str:
    """
    Create and return the output directory path for a specific stock symbol.
    
    Args:
        stock_symbol: The stock symbol to create directory for
        
    Returns:
        str: Path to the symbol's output directory
    """
    ticker_dir = Path(output_dir) / stock_symbol
    ticker_dir.mkdir(parents=True, exist_ok=True)
    return str(ticker_dir)

def get_output_directory() -> str:
    """
    Create and return the main output directory path.
    
    Returns:
        str: Path to the output directory
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    return str(output_path)

def ensure_directory_exists(directory_path: str) -> None:
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to the directory to create
    """
    Path(directory_path).mkdir(parents=True, exist_ok=True)

def get_file_size(file_path: str) -> int:
    """
    Get the size of a file in bytes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        int: File size in bytes, or 0 if file doesn't exist
    """
    try:
        return os.path.getsize(file_path)
    except (OSError, FileNotFoundError):
        return 0

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format.
    
    Args:
        size_bytes: File size in bytes
        
    Returns:
        str: Formatted file size (e.g., "1.5 MB")
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"

def get_file_extension(file_path: str) -> str:
    """
    Get the file extension from a file path.
    
    Args:
        file_path: Path to the file
        
    Returns:
        str: File extension (without the dot)
    """
    return Path(file_path).suffix.lstrip('.')

def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing invalid characters.
    
    Args:
        filename: The filename to sanitize
        
    Returns:
        str: Sanitized filename
    """
    # Remove invalid characters for Windows/Unix filesystems
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    
    # Ensure filename is not empty
    if not filename:
        filename = f"unnamed_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    return filename

# Legacy function aliases for backward compatibility
getSymbolOutputDirectory = get_symbol_output_directory
getOutputDirectory = get_output_directory 