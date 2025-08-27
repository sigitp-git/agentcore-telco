"""
AWS Lambda handler for MCP server wrapper

This module provides the Lambda function handler that wraps
stdio-based MCP servers for AgentCore Gateway integration.
"""

import json
import logging
import os
from typing import Any, Dict

from mcp_wrapper import McpServerWrapper
from config import MCP_SERVER_CONFIG

# Configure logging
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

# Initialize MCP server wrapper
mcp_wrapper = McpServerWrapper(MCP_SERVER_CONFIG)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler function for MCP requests.
    
    This handler wraps stdio-based MCP servers to work with AgentCore Gateway.
    
    Args:
        event: Lambda event containing the MCP request
        context: Lambda context object
        
    Returns:
        Dict containing the MCP response
    """
    try:
        logger.info(f"Received event: {json.dumps(event, default=str)}")
        
        # Extract the MCP request from the event
        if "body" in event:
            # API Gateway request
            body = event["body"]
            if isinstance(body, str):
                request_data = json.loads(body)
            else:
                request_data = body
        else:
            # Direct Lambda invocation (AgentCore Gateway format)
            request_data = event
            
        # Process the MCP request through the wrapper
        response = mcp_wrapper.handle_request(request_data)
        
        logger.info(f"Sending response: {json.dumps(response, default=str)}")
        
        # Return response in appropriate format
        if "body" in event:
            # API Gateway response format
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type",
                },
                "body": json.dumps(response),
            }
        else:
            # Direct Lambda response (AgentCore Gateway format)
            return response
            
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        
        error_response = {
            "jsonrpc": "2.0",
            "id": request_data.get("id") if 'request_data' in locals() else None,
            "error": {
                "code": -32603,
                "message": "Internal error",
                "data": str(e),
            }
        }
        
        if "body" in event:
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(error_response),
            }
        else:
            return error_response