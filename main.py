#!/usr/bin/env python3
"""
Memorix - Multi-Agent Memory & Coordination Platform
Track 02: Agent Memory and Coordination
Powered by FalkorDB Graph Database

Start the server on port 8000.
Open http://localhost:8000 in your browser to use the interactive dashboard.
"""

import sys
import os

# Ensure we're using Python 3.10+
if sys.version_info < (3, 10):
    print("ERROR: Python 3.10+ is required")
    sys.exit(1)

# Add the project root and backend directory to Python path
project_root = os.path.abspath(os.path.dirname(__file__))
backend_path = os.path.join(project_root, 'backend')
if project_root not in sys.path:
    sys.path.insert(0, project_root)
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

if __name__ == "__main__":
    print("=" * 80)
    print("Memorix - Multi-Agent Memory & Coordination Platform")
    print("=" * 80)
    print("Track 02: Agent Memory and Coordination")
    print("Powered by FalkorDB Graph Database")
    print("=" * 80)
    print("")
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8000))
    print(f"Starting server on port {port}...")
    print(f"Dashboard: http://localhost:{port}")
    print(f"API Documentation: http://localhost:{port}/docs")
    print(f"OpenAPI Swagger: http://localhost:{port}/openapi.json")
    print("=" * 80)
    print("")
    print(f"Python Version: {sys.version.split()[0]}")
    print(f"Working Directory: {os.getcwd()}")
    print("")
    print("Starting FastAPI server...")
    print("")
    
    # Import and run the server
    from backend.api.api import app
    
    import uvicorn
    uvicorn.run(app, host=host, port=port)