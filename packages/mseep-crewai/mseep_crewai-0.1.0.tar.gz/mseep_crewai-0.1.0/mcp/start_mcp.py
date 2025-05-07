#!/usr/bin/env python
"""
Script to start the CrewAI MCP server.
"""
import argparse
import sys
import os

# Adiciona o diretório pai ao caminho para poder importar o módulo mcp
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server import start_server

def main():
    parser = argparse.ArgumentParser(description="Start the CrewAI MCP Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host address to bind the server to")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    
    args = parser.parse_args()
    
    print(f"Starting CrewAI MCP Server on {args.host}:{args.port}")
    print("Available endpoints:")
    print("  - GET  /             : Root endpoint")
    print("  - POST /mcp/tools    : List all available tools")
    print("  - POST /mcp/execute  : Execute a tool")
    print("\nPress Ctrl+C to stop the server")
    
    start_server(host=args.host, port=args.port)

if __name__ == "__main__":
    main()