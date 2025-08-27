#!/usr/bin/env python3
"""
Create proper Lambda handlers using the mcp_lambda library from run-mcp-servers-with-aws-lambda
"""

import os
import yaml
from typing import Dict, Any

def create_handler(server_id: str, config: Dict[str, Any]) -> str:
    """Create a Lambda handler for a specific MCP server using mcp_lambda library"""
    
    handler_name = f"{server_id.replace('-', '')}function_handler"
    server_name = config['name']
    command = config['command']
    args = config['args']
    env_vars = config.get('env', {})
    
    # Create environment variables string
    env_vars_str = ""
    if env_vars:
        env_items = [f'            "{k}": "{v}"' for k, v in env_vars.items()]
        env_vars_content = ',\n'.join(env_items)
        env_vars_str = f"""
            "env": {{
{env_vars_content}
            }},"""
    
    handler_content = f'''"""
Lambda handler for {server_name} using mcp_lambda library
"""

import json
import os
from typing import Dict, Any
from aws_lambda_powertools.utilities.typing import LambdaContext


def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    """
    Lambda handler for {server_name}
    
    This handler uses the mcp_lambda library to run stdio-based MCP servers
    in the Lambda environment with Bedrock AgentCore Gateway integration.
    """
    
    try:
        # Import the mcp_lambda library components
        from mcp_lambda.handlers.bedrock_agent_core_gateway_target_handler import BedrockAgentCoreGatewayTargetHandler
        from mcp_lambda.server_adapter.stdio_server_adapter_request_handler import StdioServerAdapterRequestHandler
        
        # Server configuration
        server_config = {{
            "command": "{command}",
            "args": {args},{env_vars_str}
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
                    "server_name": "{server_name}",
                    "suggestion": "The mcp_lambda library needs to be properly configured"
                }}
            }}
        }}
        
    except Exception as e:
        # General error handling
        return {{
            "error": {{
                "code": -32603,
                "message": f"Internal error: {{str(e)}}",
                "data": {{
                    "server_id": "{server_id}",
                    "server_name": "{server_name}"
                }}
            }}
        }}
'''
    
    return handler_content

def main():
    """Generate all Lambda handlers"""
    
    # Load server configurations
    with open('servers.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    servers = config['servers']
    
    # Create handlers directory if it doesn't exist
    os.makedirs('lambda_handlers', exist_ok=True)
    
    print(f"🚀 Creating proper Lambda handlers using mcp_lambda library")
    print("=" * 60)
    
    for server_id, server_config in servers.items():
        handler_name = f"{server_id.replace('-', '')}function_handler"
        handler_file = f"lambda_handlers/{handler_name}.py"
        
        print(f"📝 Creating {handler_file}...")
        
        # Generate handler content
        handler_content = create_handler(server_id, server_config)
        
        # Write handler file
        with open(handler_file, 'w') as f:
            f.write(handler_content)
        
        print(f"   ✅ Created handler for {server_config['name']}")
    
    print("=" * 60)
    print(f"✨ Successfully created {len(servers)} Lambda handlers!")
    print()
    print("📋 Next steps:")
    print("1. Deploy with: cdk deploy --require-approval never")
    print("2. Test with: python3 test_lambda_functions.py")
    print("3. Configure AgentCore Gateway with the Lambda ARNs")

if __name__ == "__main__":
    main()