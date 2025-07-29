class GlobalConfig:
    """Global configuration for the application."""
    
    _instance = None
    _debug_mode = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GlobalConfig, cls).__new__(cls)
        return cls._instance
    
    @classmethod
    def set_debug_mode(cls, enabled: bool):
        """Enable or disable debug mode globally.
        
        Args:
            enabled: Whether to enable debug mode
        """
        cls._debug_mode = enabled
        if enabled:
            print("Debug mode enabled globally")
        else:
            print("Debug mode disabled globally")
    
    @classmethod
    def is_debug_mode(cls) -> bool:
        """Check if debug mode is enabled.
        
        Returns:
            bool: True if debug mode is enabled, False otherwise
        """
        return cls._debug_mode
    
    @classmethod
    def debug_print(cls, *args, **kwargs):
        """Print debug messages only if debug mode is enabled.
        
        Args:
            *args: Arguments to print
            **kwargs: Keyword arguments to print
        """
        if cls._debug_mode:
            print(*args, **kwargs)

