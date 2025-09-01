#!/usr/bin/env python3
"""
Generate all MCP Lambda handlers based on the working prometheus pattern.
This script creates lambda handlers for all servers defined in servers.yaml.
"""

import os
import yaml
from pathlib import Path

def create_lambda_handler_code(command, args, env_vars):
    """Create lambda handler code with proper formatting"""
    return f'''import os
import boto3
from mcp_lambda.handlers.bedrock_agent_core_gateway_target_handler import BedrockAgentCoreGatewayTargetHandler
from mcp_lambda.server_adapter.stdio_server_adapter_request_handler import StdioServerAdapterRequestHandler
from mcp.client.stdio import StdioServerParameters

class MockClientContext:
    def __init__(self, tool_name):
        self.custom = {{"bedrockAgentCoreToolName": tool_name}}

def lambda_handler(event, context):
    # Get AWS credentials from Lambda execution role
    session = boto3.Session()
    credentials = session.get_credentials()

    # Server configuration with proper StdioServerParameters
    server_params = StdioServerParameters(
        command="{command}",
        args={args},
        env={{
{env_vars}
            "AWS_DEFAULT_REGION": "us-east-1",
            "AWS_ACCESS_KEY_ID": credentials.access_key,
            "AWS_SECRET_ACCESS_KEY": credentials.secret_key,
            "AWS_SESSION_TOKEN": credentials.token
        }}
    )

    # Extract tool name from event if not in context
    if not (context.client_context and hasattr(context.client_context, "custom") and
            context.client_context.custom.get("bedrockAgentCoreToolName")):
        tool_name = None
        if isinstance(event, dict):
            tool_name = (event.get("toolName") or
                        event.get("tool_name") or
                        event.get("bedrockAgentCoreToolName"))
            headers = event.get("headers", {{}})
            if headers:
                tool_name = tool_name or headers.get("bedrockAgentCoreToolName")

        if tool_name:
            context.client_context = MockClientContext(tool_name)

    # Create request handler with proper StdioServerParameters
    request_handler = StdioServerAdapterRequestHandler(server_params)

    # Create Bedrock AgentCore Gateway handler
    gateway_handler = BedrockAgentCoreGatewayTargetHandler(request_handler)

    return gateway_handler.handle(event, context)
'''

def load_servers_config():
    """Load servers configuration from servers.yaml"""
    with open('servers.yaml', 'r') as f:
        config = yaml.safe_load(f)
    return config['servers']

def format_args_list(args):
    """Format args list for Python code"""
    formatted_args = []
    for arg in args:
        formatted_args.append(f'"{arg}"')
    return '[' + ', '.join(formatted_args) + ']'

def format_env_vars(env_dict):
    """Format environment variables for Python code"""
    env_lines = []
    for key, value in env_dict.items():
        # Skip AWS credentials as they're handled separately
        if key not in ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_SESSION_TOKEN']:
            env_lines.append(f'            "{key}": "{value}",')
    return '\n'.join(env_lines)

def create_handler_directory(server_key, server_config):
    """Create lambda handler directory and files for a server"""
    handler_dir = Path(f"lambda_handlers_q/{server_key}")
    handler_dir.mkdir(parents=True, exist_ok=True)
    
    # Format the lambda handler code
    env_vars = format_env_vars(server_config.get('env', {}))
    
    handler_code = create_lambda_handler_code(
        command=server_config['command'],
        args=format_args_list(server_config['args']),
        env_vars=env_vars
    )
    
    # Write lambda_function.py
    lambda_file = handler_dir / "lambda_function.py"
    with open(lambda_file, 'w') as f:
        f.write(handler_code)
    
    # Create requirements.txt
    requirements_file = handler_dir / "requirements.txt"
    with open(requirements_file, 'w') as f:
        f.write("""boto3>=1.34.0
mcp-lambda>=0.1.0
mcp>=1.0.0
""")
    
    print(f"✅ Created handler for {server_key} ({server_config['name']})")

def main():
    """Generate all lambda handlers"""
    print("🚀 Generating all MCP Lambda handlers based on working prometheus pattern...")
    
    # Load servers configuration
    servers = load_servers_config()
    
    # Create handlers for all servers
    for server_key, server_config in servers.items():
        create_handler_directory(server_key, server_config)
    
    print(f"\n✅ Successfully generated {len(servers)} lambda handlers!")
    print("\nAll handlers are now using the working mcp_lambda library pattern:")
    print("- BedrockAgentCoreGatewayTargetHandler")
    print("- StdioServerAdapterRequestHandler") 
    print("- Proper AWS credentials extraction from Lambda execution role")
    print("- MockClientContext for missing bedrockAgentCoreToolName")

if __name__ == "__main__":
    main()