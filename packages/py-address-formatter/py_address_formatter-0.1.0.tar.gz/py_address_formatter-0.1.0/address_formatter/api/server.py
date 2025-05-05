"""
Server module for running the address formatter API.

This module provides a function to start the API server
using Uvicorn.
"""

import uvicorn
from .main import app
from ..config import settings

def run_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """
    Run the address formatter API server.
    
    Args:
        host: Host to bind to.
        port: Port to bind to.
        reload: Whether to enable auto-reload.
    """
    uvicorn.run(
        "address_formatter.api.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

if __name__ == "__main__":
    run_server() 