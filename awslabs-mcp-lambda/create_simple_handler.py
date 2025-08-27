#!/usr/bin/env python3
"""
Create a simple working MCP Lambda handler without external dependencies
"""

import os

def create_simple_handler():
    """Create a simple MCP handler that works without mcp_lambda library"""
    
    handler_content = '''"""
Simple Lambda handler for MCP Server without external dependencies
"""

import json
import os
import subprocess
import tempfile
from typing import Dict, Any


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Simple Lambda handler for MCP Server
    
    This handler demonstrates basic MCP protocol handling without external dependencies.
    It provides a basic MCP server response for testing purposes.
    """
    
    try:
        # Extract request details
        request_id = event.get("id", 1)
        method = event.get("method", "unknown")
        
        # Handle different MCP methods
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "resources": {},
                        "prompts": {},
                        "logging": {}
                    },
                    "serverInfo": {
                        "name": "AWS Labs Core MCP Server",
                        "version": "1.0.0"
                    },
                    "instructions": "This is a simple MCP server running on AWS Lambda"
                }
            }
        
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": [
                        {
                            "name": "echo",
                            "description": "Echo back the input",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "message": {
                                        "type": "string",
                                        "description": "Message to echo back"
                                    }
                                },
                                "required": ["message"]
                            }
                        }
                    ]
                }
            }
        
        elif method == "tools/call":
            params = event.get("params", {})
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})
            
            if tool_name == "echo":
                message = arguments.get("message", "Hello from Lambda!")
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Echo: {message}"
                            }
                        ]
                    }
                }
        
        # Default response for unknown methods
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "message": f"Method '{method}' received but not implemented",
                "available_methods": ["initialize", "tools/list", "tools/call"],
                "server_info": {
                    "name": "AWS Labs Core MCP Server",
                    "version": "1.0.0",
                    "environment": "AWS Lambda"
                }
            }
        }
        
    except Exception as e:
        # Error handling
        return {
            "jsonrpc": "2.0",
            "id": event.get("id", 1),
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}",
                "data": {
                    "server_id": "core-mcp",
                    "server_name": "AWS Labs Core MCP Server"
                }
            }
        }
'''
    
    # Write the simple handler
    handler_path = "lambda_handlers/simple_coremcpfunction_handler.py"
    with open(handler_path, 'w') as f:
        f.write(handler_content)
    
    print(f"✅ Created simple handler: {handler_path}")
    return handler_path

if __name__ == "__main__":
    create_simple_handler()