#!/usr/bin/env python3
"""
AWS Labs MCP Lambda CDK Application

This creates multiple Lambda functions, one for each MCP server,
providing 1:1 mapping for better isolation and scaling.
"""

import aws_cdk as cdk
import yaml
import os
from infrastructure.multi_lambda_stack import MultiMcpLambdaStack


def load_server_configs():
    """Load server configurations from servers.yaml"""
    config_path = os.path.join(os.path.dirname(__file__), 'servers.yaml')
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


app = cdk.App()

# Load server configurations
config = load_server_configs()
servers = config.get('servers', {})

# Create the multi-MCP Lambda stack
stack = MultiMcpLambdaStack(
    app, 
    "MultiMcpLambdaStack",
    servers=servers,
    description="AWS Labs MCP Servers - One Lambda per MCP Server"
)

# Output Lambda ARNs for each server
for server_id in servers.keys():
    cdk.CfnOutput(
        stack,
        f"Mcp{server_id.replace('-', '').title()}LambdaArn",
        value=stack.lambda_arns[server_id],
        description=f"Lambda ARN for {servers[server_id]['name']}"
    )

# Output API Gateway URLs for testing
for server_id in servers.keys():
    cdk.CfnOutput(
        stack,
        f"Mcp{server_id.replace('-', '').title()}ApiUrl",
        value=stack.api_urls[server_id],
        description=f"API Gateway URL for {servers[server_id]['name']} (testing only)"
    )

app.synth()