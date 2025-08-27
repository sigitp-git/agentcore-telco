#!/usr/bin/env python3
"""
Fix Lambda handlers to use the proper mcp_lambda library
"""

import os
import yaml
from typing import Dict, Any


def create_proper_lambda_handler(server_id: str, config: Dict[str, Any]) -> str:
    """Create a proper Lambda handler using the mcp_lambda library"""
    
    handler_name = f"{server_id.replace('-', '')}function_handler"
    
    return f'''"""
Lambda handler for {config['name']} using mcp_lambda library
"""

import os
from mcp_lambda.handlers.bedrock_agent_core_gateway_target_handler import bedrock_agent_core_gateway_target_handler


def lambda_handler(event, context):
    """
    Lambda handler for {config['name']}
    
    Uses the mcp_lambda library to properly handle MCP protocol messages
    for AgentCore Gateway integration.
    """
    
    # Server configuration
    server_config = {{
        "command": "{config['command']}",
        "args": {config['args']},
        "env": {config.get('env', {})},
        "cwd": "/tmp"
    }}
    
    # Use the bedrock_agent_core_gateway_target_handler from mcp_lambda library
    return bedrock_agent_core_gateway_target_handler(
        event=event,
        context=context,
        server_config=server_config
    )
'''


def load_server_configs() -> Dict[str, Any]:
    """Load server configurations from servers.yaml"""
    with open('servers.yaml', 'r') as f:
        return yaml.safe_load(f)


def main():
    """Fix all Lambda handlers to use the proper mcp_lambda library"""
    
    print("🔧 Fixing Lambda handlers to use mcp_lambda library...")
    
    # Load server configurations
    config = load_server_configs()
    servers = config.get('servers', {})
    
    # Create lambda_handlers directory if it doesn't exist
    handlers_dir = 'lambda_handlers'
    os.makedirs(handlers_dir, exist_ok=True)
    
    # Fix handler for each server
    for server_id, server_config in servers.items():
        handler_name = f"{server_id.replace('-', '')}function_handler"
        handler_file = os.path.join(handlers_dir, f"{handler_name}.py")
        
        # Create proper handler code
        handler_code = create_proper_lambda_handler(server_id, server_config)
        
        # Write handler file
        with open(handler_file, 'w') as f:
            f.write(handler_code)
        
        print(f"✅ Fixed handler: {handler_file}")
    
    # Update requirements.txt for Lambda runtime
    requirements_file = os.path.join(handlers_dir, 'requirements.txt')
    with open(requirements_file, 'w') as f:
        f.write("""# Lambda runtime dependencies for MCP servers using mcp_lambda library
run-mcp-servers-with-aws-lambda>=0.4.1
boto3>=1.26.0
botocore>=1.29.0
requests>=2.28.0
""")
    
    print(f"✅ Updated {requirements_file}")
    print(f"\\n🎉 Fixed {len(servers)} Lambda handlers!")
    print("\\nNext steps:")
    print("1. Redeploy the Lambda functions: cdk deploy")
    print("2. Test the functions with the new handlers")
    print("3. The handlers now use the proper mcp_lambda library for MCP protocol handling")


if __name__ == "__main__":
    main()