"""
MCP Server for integrating with CrewAI tools.
"""
import os
import json
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any, List, Optional
import importlib
import sys

# Import CrewAI tools
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mcp.tools import MCP_TOOLS

# Try to import custom tool, but continue if it doesn't exist
try:
    from src.crewai.tools.custom_tool import MyCustomTool
    custom_tool = MyCustomTool()
    ALL_TOOLS = [custom_tool] + MCP_TOOLS
except ImportError:
    print("Warning: Custom tool not found. Continuing with standard tools only.")
    ALL_TOOLS = MCP_TOOLS

app = FastAPI(title="CrewAI MCP Server")

# Create a lookup dictionary for easier access
TOOL_MAP = {tool.name: tool for tool in ALL_TOOLS}

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "CrewAI MCP Server is running"}

@app.post("/mcp/tools")
async def list_tools():
    """List all available tools"""
    tools_list = []
    
    for tool in ALL_TOOLS:
        # Extract schema information from the tool
        properties = {}
        required = []
        
        if hasattr(tool, 'args_schema'):
            schema_model = tool.args_schema
            
            # Handle both Pydantic v1 and v2
            try:
                # Pydantic v1 approach
                if hasattr(schema_model, '__fields__'):
                    for field_name, field in schema_model.__fields__.items():
                        field_info = field.field_info
                        properties[field_name] = {
                            "type": "string",  # Simplified for the example
                            "description": field_info.description or ""
                        }
                        if field_info.default == ...:  # Means it's required
                            required.append(field_name)
                # Pydantic v2 approach
                else:
                    model_schema = schema_model.model_json_schema()
                    properties = model_schema.get("properties", {})
                    required = model_schema.get("required", [])
            except Exception as e:
                print(f"Warning: Could not parse schema for tool {tool.name}: {str(e)}")
        
        tools_list.append({
            "name": tool.name,
            "description": tool.description,
            "input_schema": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        })
    
    return {"tools": tools_list}

@app.post("/mcp/execute")
async def execute_tool(request: Request):
    """Execute a tool with the given parameters"""
    try:
        data = await request.json()
        tool_name = data.get("tool_name")
        parameters = data.get("parameters", {})
        
        if tool_name in TOOL_MAP:
            tool = TOOL_MAP[tool_name]
            result = tool._run(**parameters)
            return {"result": result}
        else:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

def start_server(host: str = "0.0.0.0", port: int = 8000):
    """Start the MCP server"""
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    start_server()
