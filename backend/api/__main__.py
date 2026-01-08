"""
REST API Entry Point

Run with: python -m backend.api.rest_api
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.api.rest_api import RESTAPI
from backend.integration.system_integrator import SystemIntegrator
from utils.debug_utils import DebugUtils


def main():
    """Main entry point for REST API server."""
    try:
        # Initialize system integrator
        DebugUtils.info("Initializing Stockport v4 system...")
        system_integrator = SystemIntegrator()
        
        # Create REST API with system integrator
        api = RESTAPI(system_integrator=system_integrator)
        
        # Get host and port from environment or use defaults
        host = os.getenv("STOCKPORT_API_HOST", "0.0.0.0")
        port = int(os.getenv("STOCKPORT_API_PORT", "8001"))
        
        DebugUtils.info(f"Starting REST API server on {host}:{port}")
        DebugUtils.info(f"API documentation available at http://{host}:{port}/docs")
        
        # Run server
        api.run(host=host, port=port)
        
    except KeyboardInterrupt:
        DebugUtils.info("REST API server stopped by user")
    except Exception as e:
        DebugUtils.log_error(e, "Error starting REST API server")
        sys.exit(1)


if __name__ == "__main__":
    main()

