#!/bin/bash

# Deploy script for MCP Lambda functions using run-mcp-servers-with-aws-lambda pattern

set -e

echo "🚀 Deploying MCP Lambda functions..."

# Check if CDK is installed
if ! command -v cdk &> /dev/null; then
    echo "❌ AWS CDK is not installed. Please install it first:"
    echo "npm install -g aws-cdk"
    exit 1
fi

# Check if Python dependencies are installed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "📦 Installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt

# Create lambda_handlers directory if it doesn't exist
mkdir -p lambda_handlers

# Bootstrap CDK if needed
echo "🔧 Checking CDK bootstrap..."
cdk bootstrap

# Deploy the stack
echo "🚀 Deploying MCP Lambda stack..."
cdk deploy --require-approval never

echo "✅ Deployment complete!"
echo ""
echo "📋 Lambda Functions Created:"

# Read servers.yaml and list all servers
python3 -c "
import yaml
with open('servers.yaml', 'r') as f:
    config = yaml.safe_load(f)
    servers = config.get('servers', {})
    for server_id, server_config in servers.items():
        print(f'  - {server_config[\"name\"]}: mcp-server-{server_id}')
"

echo ""
echo "📋 Next steps:"
echo "1. Copy the Lambda ARNs from the CDK output above"
echo "2. Configure your AgentCore Gateway to use these Lambda functions"
echo "3. Each MCP server now has its own dedicated Lambda function"
echo ""
echo "💡 Integration example for AgentCore Gateway:"
echo '{'
echo '  "mcpServers": {'
echo '    "core-mcp": {'
echo '      "type": "lambda",'
echo '      "arn": "arn:aws:lambda:REGION:ACCOUNT:function:mcp-server-core-mcp"'
echo '    }'
echo '  }'
echo '}'