"""
Start Backend Server

Starts the FastAPI backend server on port 8001.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set environment variables
os.environ.setdefault('USE_FAKEREDIS', 'true')  # Use fakeredis for development

if __name__ == "__main__":
    try:
        from backend.api.rest_api import RESTAPI
        from backend.integration.system_integrator import SystemIntegrator
        from utils.debug_utils import DebugUtils
        
        # Initialize system integrator
        DebugUtils.info("Initializing Stockport system...")
        system_integrator = SystemIntegrator()
        
        # Create REST API with system integrator
        api = RESTAPI(system_integrator=system_integrator)
        
        # Get host and port from environment or use defaults
        host = os.getenv("STOCKPORT_API_HOST", "0.0.0.0")
        port = int(os.getenv("STOCKPORT_API_PORT", "8001"))
        
        DebugUtils.info(f"Starting REST API server on {host}:{port}")
        DebugUtils.info(f"API documentation available at http://localhost:{port}/docs")
        DebugUtils.info("Press Ctrl+C to stop the server")
        
        # Run server using RESTAPI.run method
        api.run(host=host, port=port)
        
    except KeyboardInterrupt:
        print("\nShutting down backend server...")
    except Exception as e:
        print(f"Error starting backend server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
