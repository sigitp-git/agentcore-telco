#!/bin/bash

# Deploy script for MCP Lambda wrapper

set -e

echo "🚀 Deploying MCP Lambda Wrapper..."

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

# Bootstrap CDK if needed
echo "🔧 Checking CDK bootstrap..."
cdk bootstrap

# Deploy the stack
echo "🚀 Deploying stack..."
cdk deploy --require-approval never

echo "✅ Deployment complete!"
echo ""
echo "📋 Next steps:"
echo "1. Copy the Lambda ARN from the output above"
echo "2. Configure your AgentCore Gateway to use this Lambda function"
echo "3. Test the integration with your MCP client"
echo ""
echo "🧪 To test the API Gateway endpoint:"
echo "curl -X POST [API_URL] -H 'Content-Type: application/json' -d '{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"initialize\",\"params\":{}}'"