import os
import boto3
from mcp_lambda.handlers.bedrock_agent_core_gateway_target_handler import BedrockAgentCoreGatewayTargetHandler
from mcp_lambda.server_adapter.stdio_server_adapter_request_handler import StdioServerAdapterRequestHandler
from mcp.client.stdio import StdioServerParameters

class MockClientContext:
    def __init__(self, tool_name):
        self.custom = {"bedrockAgentCoreToolName": tool_name}

def lambda_handler(event, context):
    # Get AWS credentials from Lambda execution role
    session = boto3.Session()
    credentials = session.get_credentials()

    # Server configuration with proper StdioServerParameters
    server_params = StdioServerParameters(
        command="uvx",
        args=["awslabs.prometheus-mcp-server@latest", "--region", "us-east-1"],
        env={
            "FASTMCP_LOG_LEVEL": "DEBUG",
            "AWS_DEFAULT_REGION": "us-east-1",
            "AWS_ACCESS_KEY_ID": credentials.access_key,
            "AWS_SECRET_ACCESS_KEY": credentials.secret_key,
            "AWS_SESSION_TOKEN": credentials.token
        }
    )

    # Extract tool name from event if not in context
    if not (context.client_context and hasattr(context.client_context, "custom") and
            context.client_context.custom.get("bedrockAgentCoreToolName")):
        tool_name = None
        if isinstance(event, dict):
            tool_name = (event.get("toolName") or
                        event.get("tool_name") or
                        event.get("bedrockAgentCoreToolName"))
            headers = event.get("headers", {})
            if headers:
                tool_name = tool_name or headers.get("bedrockAgentCoreToolName")

        if tool_name:
            context.client_context = MockClientContext(tool_name)

    # Create request handler with proper StdioServerParameters
    request_handler = StdioServerAdapterRequestHandler(server_params)

    # Create Bedrock AgentCore Gateway handler
    gateway_handler = BedrockAgentCoreGatewayTargetHandler(request_handler)

    return gateway_handler.handle(event, context)
