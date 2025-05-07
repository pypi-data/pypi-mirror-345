#!/usr/bin/env python
"""
Simplified script to run the MCP server.
"""
import os
import sys
import importlib.util

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Check if we're in a virtual environment
in_venv = sys.prefix != sys.base_prefix
if not in_venv:
    print("Warning: Not running in a virtual environment!")
    print("It's recommended to use the virtual environment to run this script.")
    print("Try: source venv/bin/activate && python mcp/run_server.py")

# Check for required dependencies
requirements = ["fastapi", "uvicorn", "pydantic"]
missing = []

for package in requirements:
    if importlib.util.find_spec(package) is None:
        missing.append(package)

if missing:
    print(f"Error: Missing dependencies: {', '.join(missing)}")
    print("Please install them with:")
    print(f"pip install {' '.join(missing)}")
    sys.exit(1)

# Import server module
try:
    from mcp.server import start_server
    
    print("Starting CrewAI MCP Server on 0.0.0.0:8000")
    print("Available endpoints:")
    print("  - GET  /             : Root endpoint")
    print("  - POST /mcp/tools    : List all available tools")
    print("  - POST /mcp/execute  : Execute a tool")
    print("\nPress Ctrl+C to stop the server")
    
    start_server(host="0.0.0.0", port=8000)
except ModuleNotFoundError as e:
    print(f"Error: {e}")
    print("Make sure you're running this script from the project root directory.")
    sys.exit(1)
except Exception as e:
    print(f"Error starting server: {e}")
    sys.exit(1)