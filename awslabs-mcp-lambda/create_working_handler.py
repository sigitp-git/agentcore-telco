#!/usr/bin/env python3
"""
Create a working Lambda handler that properly uses the mcp_lambda library
"""

import os
import yaml


def create_working_handler(server_id: str, config: dict) -> str:
    """Create a working Lambda handler"""
    
    handler_name = f"{server_id.replace('-', '')}function_handler"
    
    return f'''"""
Lambda handler for {config['name']} using mcp_lambda library
"""

import json
import os
import asyncio
from typing import Dict, Any


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for {config['name']}
    
    This handler uses the mcp_lambda library to run stdio-based MCP servers
    in the Lambda environment.
    """
    
    try:
        # Import the mcp_lambda library components
        from mcp_lambda.server_adapter.stdio_server_adapter import StdioServerAdapter
        from mcp_lambda.handlers.request_handler import handle_request
        
        # Server configuration
        server_config = {{
            "command": "{config['command']}",
            "args": {config['args']},
            "env": {config.get('env', {})},
            "cwd": "/tmp"
        }}
        
        # Create server adapter
        adapter = StdioServerAdapter(server_config)
        
        # Handle the request
        return handle_request(event, context, adapter)
        
    except ImportError as e:
        # Fallback if mcp_lambda library has issues
        return {{
            "jsonrpc": "2.0",
            "id": event.get("id", 1),
            "error": {{
                "code": -32603,
                "message": f"MCP Lambda library not available: {{str(e)}}",
                "data": {{
                    "server_id": "{server_id}",
                    "server_name": "{config['name']}",
                    "suggestion": "The mcp_lambda library needs to be properly configured"
                }}
            }}
        }}
        
    except Exception as e:
        # General error handling
        return {{
            "jsonrpc": "2.0",
            "id": event.get("id", 1),
            "error": {{
                "code": -32603,
                "message": f"Internal error: {{str(e)}}",
                "data": {{
                    "server_id": "{server_id}",
                    "server_name": "{config['name']}"
                }}
            }}
        }}
'''


def main():
    """Create working handlers for all servers"""
    
    print("🔧 Creating working Lambda handlers...")
    
    # Load server configurations
    with open('servers.yaml', 'r') as f:
        config = yaml.safe_load(f)
    servers = config.get('servers', {})
    
    # Create handlers directory
    handlers_dir = 'lambda_handlers'
    os.makedirs(handlers_dir, exist_ok=True)
    
    # Create working handler for each server
    for server_id, server_config in servers.items():
        handler_name = f"{server_id.replace('-', '')}function_handler"
        handler_file = os.path.join(handlers_dir, f"{handler_name}.py")
        
        # Create working handler code
        handler_code = create_working_handler(server_id, server_config)
        
        # Write handler file
        with open(handler_file, 'w') as f:
            f.write(handler_code)
        
        print(f"✅ Created working handler: {handler_file}")
    
    print(f"\\n🎉 Created {len(servers)} working Lambda handlers!")
    print("\\nNext steps:")
    print("1. Deploy with: cdk deploy")
    print("2. Test the functions")
    print("3. The handlers now have proper error handling and fallbacks")


if __name__ == "__main__":
    main()