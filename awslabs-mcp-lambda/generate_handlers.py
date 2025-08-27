#!/usr/bin/env python3
"""
Generate Lambda handler files for each MCP server

This script creates individual Lambda handler files for each server defined in servers.yaml
following the run-mcp-servers-with-aws-lambda library pattern.
"""

import os
import yaml
from typing import Dict, Any


def load_server_configs() -> Dict[str, Any]:
    """Load server configurations from servers.yaml"""
    config_path = os.path.join(os.path.dirname(__file__), 'servers.yaml')
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def generate_handler_code(server_id: str, config: Dict[str, Any]) -> str:
    """Generate Lambda handler code for a specific MCP server"""
    
    handler_name = f"{server_id.replace('-', '')}function_handler"
    
    return f'''"""
Lambda handler for {config['name']}
Generated automatically - do not edit manually
"""

import json
import os
import subprocess
import logging
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for {config['name']}
    
    Processes MCP protocol messages by running the MCP server as a subprocess
    and forwarding JSON-RPC messages.
    """
    try:
        # Log the incoming event (without sensitive data)
        logger.info(f"Processing MCP request: {{event.get('method', 'unknown')}}")
        
        # Get MCP server configuration from environment
        mcp_command = os.environ.get('MCP_COMMAND', '{config['command']}')
        mcp_args = os.environ.get('MCP_ARGS', '{','.join(config['args'])}').split(',')
        
        # Prepare the command
        cmd = [mcp_command] + mcp_args
        
        # Set up environment variables
        env = os.environ.copy()
        
        # Run the MCP server process
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env
        )
        
        # Send the JSON-RPC request to the MCP server
        request_json = json.dumps(event)
        stdout, stderr = process.communicate(input=request_json)
        
        if process.returncode != 0:
            logger.error(f"MCP server process failed: {{stderr}}")
            return {{
                "jsonrpc": "2.0",
                "id": event.get("id"),
                "error": {{
                    "code": -32603,
                    "message": f"Internal error: MCP server process failed",
                    "data": stderr
                }}
            }}
        
        # Parse and return the response
        try:
            response = json.loads(stdout)
            logger.info(f"MCP response successful for method: {{event.get('method', 'unknown')}}")
            return response
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse MCP server response: {{e}}")
            return {{
                "jsonrpc": "2.0",
                "id": event.get("id"),
                "error": {{
                    "code": -32700,
                    "message": "Parse error: Invalid JSON response from MCP server",
                    "data": str(e)
                }}
            }}
            
    except Exception as e:
        logger.error(f"Lambda handler error: {{str(e)}}")
        return {{
            "jsonrpc": "2.0",
            "id": event.get("id"),
            "error": {{
                "code": -32603,
                "message": f"Internal error: {{str(e)}}",
                "data": {{
                    "server_id": "{server_id}",
                    "server_name": "{config['name']}"
                }}
            }}
        }}


def health_check() -> Dict[str, Any]:
    """Health check endpoint for the Lambda function"""
    return {{
        "statusCode": 200,
        "body": json.dumps({{
            "status": "healthy",
            "server_id": "{server_id}",
            "server_name": "{config['name']}",
            "description": "{config.get('description', '')}"
        }})
    }}
'''


def main():
    """Generate handler files for all MCP servers"""
    
    # Load server configurations
    config = load_server_configs()
    servers = config.get('servers', {})
    
    # Create lambda_handlers directory if it doesn't exist
    handlers_dir = os.path.join(os.path.dirname(__file__), 'lambda_handlers')
    os.makedirs(handlers_dir, exist_ok=True)
    
    # Generate handler for each server
    for server_id, server_config in servers.items():
        handler_name = f"{server_id.replace('-', '')}function_handler"
        handler_file = os.path.join(handlers_dir, f"{handler_name}.py")
        
        # Generate handler code
        handler_code = generate_handler_code(server_id, server_config)
        
        # Write handler file
        with open(handler_file, 'w') as f:
            f.write(handler_code)
        
        print(f"Generated handler: {handler_file}")
    
    print(f"\\nGenerated {len(servers)} Lambda handlers in {handlers_dir}")
    print("\\nNext steps:")
    print("1. Run 'cdk synth' to synthesize the CloudFormation template")
    print("2. Run 'cdk deploy' to deploy the Lambda functions")
    print("3. Configure the Lambda ARNs in your AgentCore Gateway")


if __name__ == "__main__":
    main()