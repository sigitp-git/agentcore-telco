"""
Lambda handler for AWS Location MCP Server using mcp_lambda library
"""

import json
import os
from typing import Dict, Any
from aws_lambda_powertools.utilities.typing import LambdaContext


def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    """
    Lambda handler for AWS Location MCP Server
    
    This handler uses the mcp_lambda library to run stdio-based MCP servers
    in the Lambda environment with Bedrock AgentCore Gateway integration.
    """
    
    try:
        # Import the mcp_lambda library components
        from mcp_lambda.handlers.bedrock_agent_core_gateway_target_handler import BedrockAgentCoreGatewayTargetHandler
        from mcp_lambda.server_adapter.stdio_server_adapter_request_handler import StdioServerAdapterRequestHandler
        
        # Server configuration
        server_config = {
            "command": "uvx",
            "args": ['awslabs.aws-location-mcp-server@latest'],
            "env": {
            "AWS_REGION": "us-east-1",
            "FASTMCP_LOG_LEVEL": "ERROR"
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
                    "server_id": "aws-location",
                    "server_name": "AWS Location MCP Server",
                    "suggestion": "The mcp_lambda library needs to be properly configured"
                }
            }
        }
        
    except Exception as e:
        # General error handling
        return {
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}",
                "data": {
                    "server_id": "aws-location",
                    "server_name": "AWS Location MCP Server"
                }
            }
        }
