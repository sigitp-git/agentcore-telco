"""
Lambda handler for AWS CloudWatch MCP Server using mcp_lambda library
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
        result = subprocess.run(['uvx', '--version'], check=True, capture_output=True, text=True)
        print(f"✅ uvx is available: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        try:
            print("🔧 Installing uv in Lambda environment...")
            
            # Install uv to /tmp (writable in Lambda)
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', 'uv', 
                '--target', '/tmp/uv_install', '--quiet'
            ], check=True)
            
            # Add the installation directory to Python path
            sys.path.insert(0, '/tmp/uv_install')
            
            # Add potential uv locations to PATH
            potential_paths = [
                '/tmp/uv_install/bin',
                '/tmp/uv_install',
                os.path.expanduser('~/.local/bin'),
                '/var/runtime/.local/bin',
                '/opt/python/bin',
                '/usr/local/bin'
            ]
            
            current_path = os.environ.get('PATH', '')
            for path in potential_paths:
                if path not in current_path:
                    current_path = f"{path}:{current_path}"
            
            os.environ['PATH'] = current_path
            print(f"🔧 Updated PATH: {current_path}")
            
            # Try to find uvx executable
            uvx_paths = [
                '/tmp/uv_install/bin/uvx',
                '/tmp/uv_install/uvx',
                'uvx'
            ]
            
            for uvx_path in uvx_paths:
                try:
                    result = subprocess.run([uvx_path, '--version'], check=True, capture_output=True, text=True)
                    print(f"✅ Successfully found uvx at {uvx_path}: {result.stdout.strip()}")
                    return True
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
            
            print("❌ uvx not found after installation")
            return False
            
        except Exception as e:
            print(f"❌ Failed to install uv: {e}")
            # Try to find uvx in common locations
            for path in ['/var/runtime/.local/bin/uvx', '/opt/python/bin/uvx', '/usr/local/bin/uvx']:
                if os.path.exists(path):
                    print(f"🔍 Found uvx at: {path}")
                    return True
            return False


def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    """
    Lambda handler for AWS CloudWatch MCP Server
    
    This handler uses the mcp_lambda library to run stdio-based MCP servers
    in the Lambda environment with Bedrock AgentCore Gateway integration.
    """
    
    try:
        # Try to ensure uv is available (only for uvx-based servers)
        if "uvx" == "uvx":
            if not install_uv_if_needed():
                return {
                    "error": {
                        "code": -32603,
                        "message": "Lambda handler error: uvx not available and could not be installed",
                        "data": {
                            "server_id": "cloudwatch-mcp",
                            "server_name": "AWS CloudWatch MCP Server",
                            "suggestion": "The Lambda environment needs uv/uvx to run MCP servers. Consider using a Lambda layer with uv pre-installed."
                        }
                    }
                }
        
        # Import the mcp_lambda library components
        from mcp_lambda.handlers.bedrock_agent_core_gateway_target_handler import BedrockAgentCoreGatewayTargetHandler
        from mcp_lambda.server_adapter.stdio_server_adapter_request_handler import StdioServerAdapterRequestHandler
        
        # Server configuration
        server_config = {
            "command": "uvx",
            "args": ['awslabs.cloudwatch-mcp-server@latest'],
            "env": {
                **{'FASTMCP_LOG_LEVEL': 'ERROR'},
                "PATH": os.environ.get('PATH', '')
            },
            "cwd": "/tmp"
        }
        
        # Create request handler with stdio server adapter
        request_handler = StdioServerAdapterRequestHandler(server_config)
        
        # Create Bedrock AgentCore Gateway handler
        gateway_handler = BedrockAgentCoreGatewayTargetHandler(request_handler)
        
        # Handle the request
        return gateway_handler.handle(event, context)
        
    except ImportError as e:
        # Fallback if mcp_lambda library has issues
        return {
            "error": {
                "code": -32603,
                "message": f"MCP Lambda library not available: {str(e)}",
                "data": {
                    "server_id": "cloudwatch-mcp",
                    "server_name": "AWS CloudWatch MCP Server",
                    "suggestion": "The mcp_lambda library needs to be properly configured"
                }
            }
        }
        
    except Exception as e:
        # General error handling
        return {
            "error": {
                "code": -32603,
                "message": f"Lambda handler error: {str(e)}",
                "data": {
                    "server_id": "cloudwatch-mcp",
                    "server_name": "AWS CloudWatch MCP Server"
                }
            }
        }
