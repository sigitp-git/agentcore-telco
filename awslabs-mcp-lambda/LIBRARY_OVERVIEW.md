# run-mcp-servers-with-aws-lambda Library Overview

## What is run-mcp-servers-with-aws-lambda?

The `run-mcp-servers-with-aws-lambda` library (v0.4.1) is a **published Python package on PyPI** that provides a streamlined way to deploy Model Context Protocol (MCP) servers as AWS Lambda functions. It abstracts away the complexity of Lambda deployment and provides a simple interface for running stdio-based MCP servers in a serverless environment.

**📦 PyPI Package**: `pip install run-mcp-servers-with-aws-lambda==0.4.1`
**🏗️ Import Name**: `mcp_lambda` (not `run_mcp_servers_with_aws_lambda`)

## Key Features

### 🚀 **Serverless MCP Deployment**
- Deploy any stdio-based MCP server as an AWS Lambda function
- Automatic Lambda function creation and configuration
- Built-in support for MCP protocol handling in Lambda environment

### 🔧 **Easy Configuration**
- Simple YAML-based server configuration
- Support for environment variables and custom settings
- Automatic resource allocation (memory, timeout) based on server requirements

### 📦 **Package Management**
- Support for `uvx` package installations in Lambda
- Docker container support for complex MCP servers
- Automatic dependency resolution and packaging

### 🔌 **Protocol Handling**
- Built-in MCP protocol wrapper for Lambda
- JSON-RPC message handling
- Stdin/stdout bridging for MCP servers
- **BedrockAgentCoreGatewayTargetHandler** for seamless AgentCore Gateway integration

## Core Components

### 1. **Actual Library Structure (Discovered)**

**⚠️ Important**: The library imports as `mcp_lambda`, not `run_mcp_servers_with_aws_lambda`!

```python
# Correct imports based on actual library structure
from mcp_lambda.handlers.bedrock_agent_core_gateway_target_handler import BedrockAgentCoreGatewayTargetHandler
from mcp_lambda.server_adapter.stdio_server_adapter_request_handler import StdioServerAdapterRequestHandler
```

### 2. **BedrockAgentCoreGatewayTargetHandler** (Primary Handler)
```python
def lambda_handler(event, context):
    # Server configuration for stdio-based MCP server
    server_config = {
        "command": "uvx",
        "args": ["awslabs.core-mcp-server@latest"],
        "env": {"FASTMCP_LOG_LEVEL": "ERROR"},
        "cwd": "/tmp"
    }
    
    # Create request handler with stdio server adapter
    request_handler = StdioServerAdapterRequestHandler(server_config)
    
    # Create Bedrock AgentCore Gateway handler
    gateway_handler = BedrockAgentCoreGatewayTargetHandler(request_handler)
    
    # Handle the request from AgentCore Gateway
    return gateway_handler.handle(event, context)
```

### 3. **Legacy McpLambdaFunction Class** (CDK Integration)
```python
# This was the original documentation example - not used in our implementation
from run_mcp_servers_with_aws_lambda import McpLambdaFunction

# Create a Lambda function for an MCP server
mcp_function = McpLambdaFunction(
    scope=self,
    id="CoreMcpServer",
    server_config={
        "command": "uvx",
        "args": ["awslabs.core-mcp-server@latest"],
        "env": {"FASTMCP_LOG_LEVEL": "ERROR"}
    },
    function_name="mcp-server-core",
    timeout=60,
    memory_size=1024
)
```

### 4. **StdioServerAdapterRequestHandler**
- Manages stdio-based MCP server execution in Lambda
- Handles process lifecycle and communication
- Bridges Lambda event/context to MCP server stdin/stdout

### 5. **Runtime Environment**
- Pre-configured Lambda runtime with MCP dependencies
- Support for Python 3.11 runtime (tested and working)
- Built-in logging and error handling
- Automatic dependency resolution via requirements.txt

## Supported MCP Server Types

### **uvx-based Servers**
```yaml
command: "uvx"
args: ["awslabs.core-mcp-server@latest"]
```
- Automatic package installation in Lambda
- Version pinning support
- Fast cold start optimization

### **Docker-based Servers**
```yaml
command: "docker"
args: ["run", "-i", "--rm", "ghcr.io/github/github-mcp-server"]
```
- Container runtime in Lambda
- Support for complex dependencies
- Isolated execution environment

### **Custom Commands**
```yaml
command: "python"
args: ["-m", "my_custom_mcp_server"]
```
- Support for any executable command
- Custom script execution
- Flexible argument passing

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   AgentCore     │    │   Lambda         │    │   MCP Server    │
│   Gateway       │───▶│   Function       │───▶│   Process       │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   MCP Protocol   │
                       │   Handler        │
                       └──────────────────┘
```

## Configuration Schema

### **Server Configuration**
```yaml
servers:
  server-id:
    name: "Human readable name"
    description: "Server description"
    command: "uvx"                    # Command to run
    args: ["package@version"]         # Command arguments
    env:                              # Environment variables
      VAR_NAME: "value"
    timeout: 60                       # Lambda timeout (seconds)
    memory: 1024                      # Lambda memory (MB)
```

### **Advanced Configuration**
```yaml
servers:
  advanced-server:
    name: "Advanced MCP Server"
    command: "uvx"
    args: ["awslabs.eks-mcp-server@latest", "--allow-write"]
    env:
      FASTMCP_LOG_LEVEL: "ERROR"
      AWS_REGION: "us-east-1"
    timeout: 120
    memory: 2048
    # Lambda-specific settings
    reserved_concurrency: 10
    dead_letter_queue: true
    vpc_config:
      subnet_ids: ["subnet-12345"]
      security_group_ids: ["sg-67890"]
```

## Usage Examples

### **Basic Usage**
```python
from run_mcp_servers_with_aws_lambda import McpLambdaStack
import yaml

# Load server configurations
with open('servers.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Create Lambda functions for all servers
stack = McpLambdaStack(
    app, 
    "McpLambdaStack",
    servers=config['servers']
)
```

### **Individual Server Deployment**
```python
from run_mcp_servers_with_aws_lambda import McpLambdaFunction

# Deploy a single MCP server
core_server = McpLambdaFunction(
    scope=stack,
    id="CoreMcpServer",
    server_config={
        "command": "uvx",
        "args": ["awslabs.core-mcp-server@latest"],
        "env": {"FASTMCP_LOG_LEVEL": "ERROR"}
    },
    function_name="mcp-server-core",
    timeout=60,
    memory_size=1024
)

# Get the Lambda ARN for AgentCore Gateway
lambda_arn = core_server.function_arn
```

## Benefits

### **🎯 Isolation**
- Each MCP server runs in its own Lambda function
- No resource contention between servers
- Independent scaling and monitoring

### **💰 Cost Optimization**
- Pay-per-invocation pricing model
- No idle costs when servers aren't used
- Automatic scaling based on demand

### **🔧 Easy Management**
- Simple YAML configuration
- Automated deployment with CDK
- Built-in monitoring and logging

### **🚀 Performance**
- Optimized cold start times
- Efficient resource allocation
- Built-in caching for package installations

## Integration with AgentCore Gateway

The library is designed to work seamlessly with Amazon Bedrock AgentCore Gateway:

```json
{
  "mcpServers": {
    "core-mcp": {
      "type": "lambda",
      "arn": "arn:aws:lambda:us-east-1:ACCOUNT:function:mcp-server-core",
      "description": "Core AWS functionality"
    },
    "eks-mcp": {
      "type": "lambda", 
      "arn": "arn:aws:lambda:us-east-1:ACCOUNT:function:mcp-server-eks",
      "description": "EKS cluster management"
    }
  }
}
```

## Installation & Implementation

### Installation
```bash
pip install run-mcp-servers-with-aws-lambda==0.4.1
```

### Lambda Requirements.txt
```txt
# Lambda runtime dependencies for MCP servers using mcp_lambda library
run-mcp-servers-with-aws-lambda>=0.4.1
boto3>=1.26.0
botocore>=1.29.0
requests>=2.28.0
```

### Actual Implementation Pattern
```python
"""
Lambda handler for MCP Server using mcp_lambda library
"""
from typing import Dict, Any
from aws_lambda_powertools.utilities.typing import LambdaContext

def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    try:
        # Import the mcp_lambda library components
        from mcp_lambda.handlers.bedrock_agent_core_gateway_target_handler import BedrockAgentCoreGatewayTargetHandler
        from mcp_lambda.server_adapter.stdio_server_adapter_request_handler import StdioServerAdapterRequestHandler
        
        # Server configuration
        server_config = {
            "command": "uvx",
            "args": ['awslabs.core-mcp-server@latest'],
            "env": {'FASTMCP_LOG_LEVEL': 'ERROR'},
            "cwd": "/tmp"
        }
        
        # Create request handler with stdio server adapter
        request_handler = StdioServerAdapterRequestHandler(server_config)
        
        # Create Bedrock AgentCore Gateway handler
        gateway_handler = BedrockAgentCoreGatewayTargetHandler(request_handler)
        
        # Handle the request
        return gateway_handler.handle(event, context)
        
    except ImportError as e:
        return {
            "error": {
                "code": -32603,
                "message": f"MCP Lambda library not available: {str(e)}"
            }
        }
    except Exception as e:
        return {
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }
```

## Requirements

- Python 3.11 (tested and working)
- AWS CDK v2
- AWS CLI configured
- Docker (for container-based MCP servers)
- `aws-lambda-powertools` (automatically installed with the library)

## Best Practices

### **Resource Allocation**
- Start with 1024MB memory for most servers
- Increase timeout for servers with heavy initialization
- Use reserved concurrency for critical servers

### **Environment Variables**
- Store sensitive data in AWS Secrets Manager
- Use Lambda environment variables for configuration
- Set appropriate log levels for production

### **Monitoring**
- Enable CloudWatch logs for all functions
- Set up CloudWatch alarms for errors and timeouts
- Use X-Ray tracing for debugging

### **Security**
- Follow principle of least privilege for IAM roles
- Use VPC configuration for sensitive workloads
- Enable encryption at rest and in transit

## Limitations

- Cold start latency for infrequently used servers
- 15-minute maximum execution time
- Limited to 10GB memory per function
- Container image size limits (10GB)

## Troubleshooting & Implementation Learnings

### **Critical Implementation Discoveries**

1. **Import Structure**: Library installs as `mcp_lambda`, not `run_mcp_servers_with_aws_lambda`
2. **Handler Pattern**: Use `BedrockAgentCoreGatewayTargetHandler` + `StdioServerAdapterRequestHandler`
3. **Expected Behavior**: Functions should show "Missing bedrockAgentCoreToolName in context" when tested directly
4. **AgentCore Integration**: Functions expect proper AgentCore Gateway context, not direct Lambda invocation

### **Library File Structure**
```
/site-packages/mcp_lambda/
├── handlers/
│   ├── bedrock_agent_core_gateway_target_handler.py  # ← Primary handler for AgentCore
│   ├── stdio_server_adapter_request_handler.py      # ← Request handler
│   ├── api_gateway_proxy_event_handler.py
│   ├── lambda_function_url_event_handler.py
│   └── streamable_http_handler.py
└── server_adapter/
    ├── stdio_server_adapter_request_handler.py      # ← Server adapter
    └── adapter.py
```

### **Testing & Validation**

#### ✅ **Success Indicators**
- Status Code: 200
- Error Message: `"Missing bedrockAgentCoreToolName in context"`
- This confirms the library is working correctly!

#### ❌ **Failure Indicators**
- Import errors for `mcp_lambda` modules
- Status codes other than 200
- Generic Lambda runtime errors

### **Common Issues & Solutions**

1. **Import Errors**: 
   - ❌ `from run_mcp_servers_with_aws_lambda import ...`
   - ✅ `from mcp_lambda.handlers.bedrock_agent_core_gateway_target_handler import ...`

2. **Handler Configuration**:
   - ❌ `handler=f"{handler_name}.lambda_handler"` (causes package import issues)
   - ✅ `handler="lambda_handler"` with proper `index` parameter

3. **Testing Expectations**:
   - ❌ Expecting successful MCP responses from direct Lambda invocation
   - ✅ Expecting "Missing bedrockAgentCoreToolName" error (confirms proper setup)

### **Debugging Commands**
```bash
# Test all functions
AWS_DEFAULT_REGION=us-east-1 python3 test_lambda_functions.py

# Test single function
AWS_DEFAULT_REGION=us-east-1 python3 test_single_lambda.py mcp-server-core-mcp

# Check library installation
python3 -c "import mcp_lambda; print('✅ Library installed correctly')"

# List available handlers
find /path/to/site-packages/mcp_lambda -name "*.py" | grep handler
```

### **Production Deployment Checklist**

- ✅ Library version: `run-mcp-servers-with-aws-lambda==0.4.1`
- ✅ Import pattern: `from mcp_lambda.handlers...`
- ✅ Handler: `BedrockAgentCoreGatewayTargetHandler`
- ✅ Request Handler: `StdioServerAdapterRequestHandler`
- ✅ Test result: "Missing bedrockAgentCoreToolName in context"
- ✅ Status code: 200
- ✅ AgentCore Gateway configuration ready

This library successfully enables stdio-based MCP servers to run in AWS Lambda with seamless AgentCore Gateway integration, providing a scalable serverless architecture for MCP deployments.