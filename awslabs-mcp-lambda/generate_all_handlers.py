#!/usr/bin/env python3
"""
Generate all MCP Lambda handlers based on the working prometheus pattern.
This script creates lambda handlers for all servers defined in servers.yaml.

Updated September 2025:
- Uses correct package name: run-mcp-servers-with-aws-lambda==0.4.2
- Generates handlers compatible with CDK resource-based policies
- All handlers use proven mcp_lambda library pattern
- Ready for Bedrock AgentCore Gateway integration
"""

import os
import yaml
import requests
import json
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

def convert_uvx_to_python_module(command, args):
    """Convert uvx commands to python -m module calls for Lambda compatibility"""
    if command == "uvx" and args:
        # Extract the package name from uvx args
        package_arg = args[0]
        
        # Handle different uvx package patterns
        if package_arg.startswith("awslabs."):
            # Convert awslabs.package-name@latest to awslabs.package_name.server
            package_name = package_arg.split("@")[0]  # Remove @latest
            module_name = package_name.replace("-", "_") + ".server"
            return "python", ["-m", module_name]
        elif package_arg == "mcp-proxy":
            # Keep mcp-proxy as is but use python
            return "python", ["-m", "mcp_proxy"] + args[1:]
        elif package_arg.startswith("mcp-server-"):
            # Convert mcp-server-* to mcp_server_*
            module_name = package_arg.replace("-", "_")
            return "python", ["-m", module_name] + args[1:]
        else:
            # For other packages, try to convert to module format
            module_name = package_arg.replace("-", "_")
            return "python", ["-m", module_name] + args[1:]
    
    # For non-uvx commands, return as-is
    return command, args

def get_latest_pypi_version(package_name):
    """Get the latest version of a package from PyPI"""
    try:
        url = f"https://pypi.org/pypi/{package_name}/json"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        latest_version = data['info']['version']
        print(f"   📦 {package_name}: Found latest version {latest_version} on PyPI")
        return latest_version
    except requests.exceptions.RequestException as e:
        print(f"   ⚠️  {package_name}: Could not fetch from PyPI ({e}), using fallback version")
        return None
    except (KeyError, json.JSONDecodeError) as e:
        print(f"   ⚠️  {package_name}: Invalid PyPI response ({e}), using fallback version")
        return None

def get_mcp_server_package(server_key, server_config):
    """Get the specific MCP server package name for requirements.txt with latest PyPI version"""
    command = server_config['command']
    args = server_config['args']
    
    if command == "uvx" and args:
        package_arg = args[0]
        
        # Handle different package patterns
        if package_arg.startswith("awslabs."):
            # Extract package name and get latest version from PyPI for information
            package_name = package_arg.split("@")[0]  # Remove @latest
            latest_version = get_latest_pypi_version(package_name)
            
            # Use conservative versions to avoid dependency conflicts
            # These are known working versions that are compatible with each other
            conservative_versions = {
                "awslabs.core-mcp-server": "0.2.5",
                "awslabs.aws-pricing-mcp-server": "0.2.5", 
                "awslabs.aws-documentation-mcp-server": "0.2.5",
                "awslabs.frontend-mcp-server": "0.2.5",
                "awslabs.aws-location-mcp-server": "0.2.5",
                "awslabs.git-repo-research-mcp-server": "0.2.5",
                "awslabs.eks-mcp-server": "0.2.5",
                "awslabs.aws-diagram-mcp-server": "0.2.5",
                "awslabs.prometheus-mcp-server": "0.2.5",
                "awslabs.cfn-mcp-server": "0.2.5",
                "awslabs.terraform-mcp-server": "0.2.5",
                "awslabs.cloudwatch-mcp-server": "0.2.5",
                "awslabs.cloudwatch-appsignals-mcp-server": "0.2.5",
                "awslabs.ccapi-mcp-server": "0.2.5"
            }
            
            version = conservative_versions.get(package_name, "0.2.5")
            if latest_version and latest_version != version:
                print(f"   ℹ️  {package_name}: Using conservative version {version} (latest: {latest_version}) for compatibility")
            return f"{package_name}=={version}"
        elif package_arg == "mcp-proxy":
            latest_version = get_latest_pypi_version("mcp-proxy")
            version = "0.1.0"  # Use conservative version
            if latest_version and latest_version != version:
                print(f"   ℹ️  mcp-proxy: Using conservative version {version} (latest: {latest_version}) for compatibility")
            return f"mcp-proxy=={version}"
        elif package_arg.startswith("mcp-server-"):
            latest_version = get_latest_pypi_version(package_arg)
            version = "0.1.0"  # Use conservative version
            if latest_version and latest_version != version:
                print(f"   ℹ️  {package_arg}: Using conservative version {version} (latest: {latest_version}) for compatibility")
            return f"{package_arg}=={version}"
        else:
            # For other packages, use conservative version
            latest_version = get_latest_pypi_version(package_arg)
            version = "0.1.0"
            if latest_version and latest_version != version:
                print(f"   ℹ️  {package_arg}: Using conservative version {version} (latest: {latest_version}) for compatibility")
            return f"{package_arg}=={version}"
    elif command == "docker":
        # Docker-based handlers don't need Python packages
        return None
    
    return None

def create_requirements_content(server_key, server_config):
    """Create requirements.txt content with specific MCP server package"""
    mcp_package = get_mcp_server_package(server_key, server_config)
    
    if server_key == "github":
        # GitHub uses Docker, minimal requirements - use exact same format as working Prometheus
        return """run-mcp-servers-with-aws-lambda==0.4.2
awslabs.prometheus-mcp-server==0.2.5
boto3==1.40.18
"""
    elif mcp_package:
        # Standard 3-package structure - use exact same format as working Prometheus
        return f"""run-mcp-servers-with-aws-lambda==0.4.2
{mcp_package}
boto3==1.40.18
"""
    else:
        # Fallback to basic requirements - use exact same format as working Prometheus
        return """run-mcp-servers-with-aws-lambda==0.4.2
awslabs.prometheus-mcp-server==0.2.5
boto3==1.40.18
"""

def create_handler_directory(server_key, server_config):
    """Create lambda handler directory and files for a server"""
    handler_dir = Path(f"lambda_handlers_q/{server_key}")
    handler_dir.mkdir(parents=True, exist_ok=True)
    
    # Format the lambda handler code
    env_vars = format_env_vars(server_config.get('env', {}))
    
    # Convert uvx commands to python -m module calls for Lambda compatibility
    command, args = convert_uvx_to_python_module(
        server_config['command'], 
        server_config['args']
    )
    
    handler_code = create_lambda_handler_code(
        command=command,
        args=format_args_list(args),
        env_vars=env_vars
    )
    
    # Write lambda_function.py
    lambda_file = handler_dir / "lambda_function.py"
    with open(lambda_file, 'w') as f:
        f.write(handler_code)
    
    # Create requirements.txt with specific MCP server package
    requirements_file = handler_dir / "requirements.txt"
    requirements_content = create_requirements_content(server_key, server_config)
    with open(requirements_file, 'w') as f:
        f.write(requirements_content)
    
    print(f"✅ Created handler for {server_key} ({server_config['name']})")

def main():
    """Generate all lambda handlers"""
    print("🚀 Generating all MCP Lambda handlers based on working prometheus pattern...")
    print("📋 Features included:")
    print("   - Correct package: run-mcp-servers-with-aws-lambda==0.4.2")
    print("   - CDK-compatible handler structure")
    print("   - Resource-based policy ready")
    print("   - Lambda-compatible: 'python -m' command instead of 'uvx'")
    print("   - Bedrock AgentCore Gateway integration")
    print("   - Automatic PyPI version detection for latest packages")
    print()
    
    # Load servers configuration
    servers = load_servers_config()
    
    print("🔍 Checking PyPI for latest package versions...")
    print()
    
    # Create handlers for all servers
    for server_key, server_config in servers.items():
        create_handler_directory(server_key, server_config)
    
    print(f"\n✅ Successfully generated {len(servers)} lambda handlers!")
    print("\nAll handlers are now using the working mcp_lambda library pattern:")
    print("- BedrockAgentCoreGatewayTargetHandler")
    print("- StdioServerAdapterRequestHandler") 
    print("- Proper AWS credentials extraction from Lambda execution role")
    print("- MockClientContext for missing bedrockAgentCoreToolName")
    print("- Using run-mcp-servers-with-aws-lambda==0.4.2 package")
    print("- Lambda-compatible: 'python' command instead of 'uvx'")
    print("- Ready for Bedrock AgentCore Gateway integration")
    print("\n🎯 Key Improvements:")
    print("- Consistent Structure: All handlers now follow the same 3-package pattern")
    print("- Specific Packages: Each handler includes its specific MCP server package")
    print("- Version Compatibility: Uses conservative versions to avoid dependency conflicts")
    print("- PyPI Awareness: Checks latest versions and reports differences")
    print("- Clean Requirements: Removed generic mcp>=1.0.0 in favor of specific packages")
    print("- Fallback Handling: Uses known good versions if PyPI is unavailable")

if __name__ == "__main__":
    main()