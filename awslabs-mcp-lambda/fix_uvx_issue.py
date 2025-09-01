#!/usr/bin/env python3
"""
Fix the uvx issue in all Lambda handlers by adding uv installation logic
"""

import os
import yaml
from typing import Dict, Any


def create_fixed_lambda_handler(server_id: str, config: Dict[str, Any]) -> str:
    """Create a Lambda handler with uvx installation fix"""
    
    handler_name = f"{server_id.replace('-', '')}function_handler"
    
    return f'''"""
Lambda handler for {config['name']} using mcp_lambda library
"""

import json
import os
import subprocess
import sys
from typing import Dict, Any
from aws_lambda_powertools.utilities.typing import LambdaContext


def install_uv_if_needed():
    """Install uv if not available in the Lambda environment"""
    try:
        # Check if uvx is available
        subprocess.run(['uvx', '--version'], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        try:
            # Try to install uv using pip
            print("Installing uv in Lambda environment...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'uv'], check=True)
            
            # Add uv to PATH
            uv_bin = os.path.expanduser('~/.local/bin')
            if uv_bin not in os.environ.get('PATH', ''):
                os.environ['PATH'] = f"{{uv_bin}}:{{os.environ.get('PATH', '')}}"
            
            # Test if uvx is now available
            subprocess.run(['uvx', '--version'], check=True, capture_output=True)
            print("✅ Successfully installed uv in Lambda environment")
            return True
        except Exception as e:
            print(f"❌ Failed to install uv: {{e}}")
            return False


def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    """
    Lambda handler for {config['name']}
    
    This handler uses the mcp_lambda library to run stdio-based MCP servers
    in the Lambda environment with Bedrock AgentCore Gateway integration.
    """
    
    try:
        # Try to ensure uv is available (only for uvx-based servers)
        if "{config['command']}" == "uvx":
            if not install_uv_if_needed():
                return {{
                    "error": {{
                        "code": -32603,
                        "message": "Lambda handler error: uvx not available and could not be installed",
                        "data": {{
                            "server_id": "{server_id}",
                            "server_name": "{config['name']}",
                            "suggestion": "The Lambda environment needs uv/uvx to run MCP servers. Consider using a Lambda layer with uv pre-installed."
                        }}
                    }}
                }}
        
        # Import the mcp_lambda library components
        from mcp_lambda.handlers.bedrock_agent_core_gateway_target_handler import BedrockAgentCoreGatewayTargetHandler
        from mcp_lambda.server_adapter.stdio_server_adapter_request_handler import StdioServerAdapterRequestHandler
        
        # Server configuration
        server_config = {{
            "command": "{config['command']}",
            "args": {config['args']},
            "env": {{
                **{config.get('env', {})},
                "PATH": os.environ.get('PATH', '')
            }},
            "cwd": "/tmp"
        }}
        
        # Create request handler with stdio server adapter
        request_handler = StdioServerAdapterRequestHandler(server_config)
        
        # Create Bedrock AgentCore Gateway handler
        gateway_handler = BedrockAgentCoreGatewayTargetHandler(request_handler)
        
        # Handle the request
        return gateway_handler.handle(event, context)
        
    except ImportError as e:
        # Fallback if mcp_lambda library has issues
        return {{
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
            "error": {{
                "code": -32603,
                "message": f"Lambda handler error: {{str(e)}}",
                "data": {{
                    "server_id": "{server_id}",
                    "server_name": "{config['name']}"
                }}
            }}
        }}
'''


def main():
    """Fix all Lambda handlers to handle uvx installation"""
    
    print("🔧 Fixing uvx issue in all Lambda handlers...")
    
    # Load server configurations
    with open('servers.yaml', 'r') as f:
        config = yaml.safe_load(f)
    servers = config.get('servers', {})
    
    # Create handlers directory
    handlers_dir = 'lambda_handlers'
    os.makedirs(handlers_dir, exist_ok=True)
    
    # Fix handler for each server
    for server_id, server_config in servers.items():
        handler_name = f"{server_id.replace('-', '')}function_handler"
        handler_file = os.path.join(handlers_dir, f"{handler_name}.py")
        
        # Create fixed handler code
        handler_code = create_fixed_lambda_handler(server_id, server_config)
        
        # Write handler file
        with open(handler_file, 'w') as f:
            f.write(handler_code)
        
        print(f"✅ Fixed handler: {handler_file}")
    
    print(f"\\n🎉 Fixed {len(servers)} Lambda handlers!")
    print("\\nChanges made:")
    print("1. Added uv installation logic for uvx-based servers")
    print("2. Enhanced error handling with better messages")
    print("3. Added PATH management for uv binary")
    print("4. Conditional uv installation only for uvx servers")
    print("\\nNext steps:")
    print("1. Redeploy the Lambda functions: cdk deploy")
    print("2. Test the functions - they should now handle uvx installation")
    print("3. Monitor CloudWatch logs for installation success/failure")


if __name__ == "__main__":
    main()