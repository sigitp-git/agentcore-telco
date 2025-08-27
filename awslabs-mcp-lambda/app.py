#!/usr/bin/env python3
"""
AWS Labs MCP Lambda CDK Application

Creates individual Lambda functions for each MCP server defined in servers.yaml
"""

import aws_cdk as cdk
import yaml
import os
from infrastructure.mcp_lambda_stack import McpLambdaStack


def load_server_configs():
    """Load server configurations from servers.yaml"""
    config_path = os.path.join(os.path.dirname(__file__), 'servers.yaml')
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


app = cdk.App()

# Load server configurations
config = load_server_configs()
servers = config.get('servers', {})

# Create the MCP Lambda stack
stack = McpLambdaStack(
    app, 
    "McpLambdaStack",
    servers=servers,
    description=f"AWS Labs MCP Servers - {len(servers)} Lambda Functions"
)

# Output Lambda ARNs for AgentCore Gateway integration
for server_id in servers.keys():
    function_name = f"mcp-server-{server_id}"
    output_name = f"Mcp{server_id.replace('-', '').title()}LambdaArn"
    
    cdk.CfnOutput(
        stack,
        output_name,
        value=stack.lambda_arns[server_id],
        description=f"Lambda ARN for {servers[server_id]['name']}"
    )

app.synth()