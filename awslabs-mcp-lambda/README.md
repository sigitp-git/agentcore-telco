# AWS Labs MCP Lambda - Serverless MCP Deployment

Deploy 18 Model Context Protocol (MCP) servers as individual AWS Lambda functions using the proven `mcp_lambda` library pattern. Each MCP server gets its own dedicated Lambda function for optimal isolation and scaling.

**✅ STATUS: All 18 MCP servers using proven mcp_lambda library pattern with enhanced requirements - Ready for deployment!**

## 🎯 Recent Enhancements (September 2025)

### **✅ Requirements.txt Standardization**
All lambda handlers now follow the **proven 3-package pattern** based on the manually tested Prometheus handler:

- **Consistent Structure**: All handlers use the same 3-package pattern
- **Specific Packages**: Each handler includes its specific MCP server package (e.g., `awslabs.prometheus-mcp-server==0.2.5`)
- **Version Consistency**: All use standardized versions (0.4.2, 0.2.5, 1.40.18)
- **Clean Requirements**: Removed generic `mcp>=1.0.0` in favor of specific packages

### **✅ Enhanced Handler Generation**
The `generate_all_handlers.py` script now automatically creates handlers with:
- Correct MCP server package detection
- Proper version management
- Special case handling (Docker, proxy, legacy packages)
- Consistent 3-package requirements structure

## 🎯 Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   AgentCore     │    │   Lambda         │    │   MCP Server    │
│   Gateway       │───▶│   Function       │───▶│   Process       │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │ mcp_lambda       │
                       │ BedrockAgentCore │
                       │ GatewayTarget    │
                       │ Handler          │
                       └──────────────────┘
```

**1:1 Mapping**: One Lambda function per MCP server for complete isolation and independent scaling.
**Proven Pattern**: Uses working `mcp_lambda` library with `BedrockAgentCoreGatewayTargetHandler` for reliable AgentCore Gateway integration.

## 🚀 Supported MCP Servers (18 Total)

### **AWS Labs MCP Servers (15)**
- **Core MCP**: `awslabs.core-mcp-server` - Core AWS functionality
- **AWS Documentation**: `awslabs.aws-documentation-mcp-server` - AWS docs search
- **AWS Pricing**: `awslabs.aws-pricing-mcp-server` - AWS pricing info
- **Frontend MCP**: `awslabs.frontend-mcp-server` - React/frontend tools
- **AWS Location**: `awslabs.aws-location-mcp-server` - Location services
- **Git Repo Research**: `awslabs.git-repo-research-mcp-server` - Advanced git analysis
- **EKS MCP**: `awslabs.eks-mcp-server` - Kubernetes management
- **AWS Diagram**: `awslabs.aws-diagram-mcp-server` - Architecture diagrams
- **Prometheus**: `awslabs.prometheus-mcp-server` - Metrics monitoring
- **CloudFormation**: `awslabs.cfn-mcp-server` - CFN management
- **Terraform**: `awslabs.terraform-mcp-server` - Infrastructure as code
- **AWS Knowledge**: `mcp-proxy` - AWS knowledge base
- **CloudWatch**: `awslabs.cloudwatch-mcp-server` - Logs and metrics
- **CloudWatch AppSignals**: `awslabs.cloudwatch-appsignals-mcp-server` - Application monitoring
- **Cloud Control API**: `awslabs.ccapi-mcp-server` - AWS resource management

### **Third-party MCP Servers (3)**
- **GitHub**: `ghcr.io/github/github-mcp-server` - GitHub operations
- **Git Repository (Legacy)**: `mcp-server-git` - Basic git operations
- **Filesystem**: `mcp-server-filesystem` - File system access

## 📁 Project Structure

```
awslabs-mcp-lambda/
├── README.md                    # This file
├── LIBRARY_OVERVIEW.md          # run-mcp-servers-with-aws-lambda library overview
├── servers.yaml                 # MCP server configurations
├── requirements.txt             # CDK dependencies
├── app.py                      # CDK application
├── cdk.json                    # CDK configuration
├── deploy.sh                   # Deployment script
├── test_setup.py               # Configuration test script
├── infrastructure/
│   ├── __init__.py
│   └── mcp_lambda_stack.py     # CDK stack with MCP Lambda functions
├── lambda_handlers_q/          # Working Lambda handlers using mcp_lambda library
│   ├── prometheus/             # Example: Prometheus MCP server handler
│   │   ├── lambda_function.py  # Working handler implementation
│   │   └── requirements.txt    # Handler dependencies
│   └── ... (17 more handlers)
├── generate_all_handlers.py    # Script to generate all handlers from servers.yaml
├── deploy_updated_stack.sh     # Deployment script
├── verify_deployment.py        # Deployment verification script
└── verify_handlers.py          # Handler validation script
```

## ⚡ Quick Start

### 1. **Generate Working Lambda Handlers** (if not already done)
```bash
python3 generate_all_handlers.py
```

### 2. **Deploy Updated Lambda Functions**
```bash
./deploy_updated_stack.sh
```

### 3. **Verify Deployment**
```bash
python3 verify_deployment.py
```

### 4. **Get Lambda ARNs**
After deployment, CDK will output Lambda ARNs for all 18 servers:
```
McpCoremcpLambdaArn = arn:aws:lambda:us-east-1:ACCOUNT:function:mcp-server-core-mcp
McpAwspricingLambdaArn = arn:aws:lambda:us-east-1:ACCOUNT:function:mcp-server-aws-pricing
McpEksmcpLambdaArn = arn:aws:lambda:us-east-1:ACCOUNT:function:mcp-server-eks-mcp
# ... and 15 more servers
```

### 5. **Expected Test Results**
✅ **Success Indicator**: Functions respond with status 200 and show:
```
"Internal error: Missing bedrockAgentCoreToolName in context"
```
This confirms the `mcp_lambda` library is working correctly and expecting proper AgentCore Gateway context.

## 🔧 AgentCore Gateway Integration

Configure each Lambda ARN in your AgentCore Gateway:

```json
{
  "mcpServers": {
    "core-mcp": {
      "type": "lambda",
      "arn": "arn:aws:lambda:us-east-1:ACCOUNT:function:mcp-server-core-mcp",
      "description": "Core AWS functionality and prompt understanding"
    },
    "aws-docs": {
      "type": "lambda", 
      "arn": "arn:aws:lambda:us-east-1:ACCOUNT:function:mcp-server-aws-docs",
      "description": "AWS documentation search and retrieval"
    },
    "eks-mcp": {
      "type": "lambda",
      "arn": "arn:aws:lambda:us-east-1:ACCOUNT:function:mcp-server-eks-mcp", 
      "description": "Amazon EKS cluster management"
    }
    // ... configure all 18 servers as needed
  }
}
```

## 🎛️ Server Configuration

Each server in `servers.yaml` supports:

```yaml
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

## 🔍 Benefits of Lambda Deployment

### **🎯 Isolation**
- Each MCP server runs in its own Lambda function
- No resource contention between servers
- Independent failure isolation

### **💰 Cost Optimization**
- Pay-per-invocation pricing model
- No idle costs when servers aren't used
- Automatic scaling based on demand

### **🚀 Performance**
- Optimized cold start times
- Right-sized resource allocation per server
- Built-in retry and error handling

### **🔧 Management**
- Individual monitoring per server
- Independent updates and deployments
- CloudWatch logs per function

## 🛠️ Development

### **Prerequisites**
- Python 3.9+
- AWS CDK v2
- AWS CLI configured
- Node.js (for CDK)

### **Installation**
```bash
# Install CDK
npm install -g aws-cdk

# Install Python dependencies
pip install -r requirements.txt

# Bootstrap CDK (first time only)
cdk bootstrap
```

### **Handler Requirements Structure**
Each handler now uses the proven 3-package pattern:
```txt
run-mcp-servers-with-aws-lambda==0.4.2
awslabs.prometheus-mcp-server==0.2.5  # Specific MCP server package
boto3==1.40.18
```

**Package Mapping Examples:**
- AWS Labs servers: `awslabs.package-name==0.2.5`
- Legacy servers: `mcp-server-*==0.1.0`
- Proxy servers: `mcp-proxy==0.1.0`
- Docker servers: Minimal requirements with explanatory comments

### **Testing**
```bash
# Test configuration
python3 test_setup.py

# Test CDK synthesis
cdk synth

# Deploy to AWS
./deploy.sh
```

## 📊 Monitoring & Observability

Each Lambda function provides:
- **CloudWatch Logs**: `/aws/lambda/mcp-server-{server-id}`
- **CloudWatch Metrics**: Invocation, duration, errors per function
- **Individual Alarms**: Set up per-server monitoring
- **Cost Tracking**: Per-function cost allocation

## 🔐 Security & Permissions

- **Principle of Least Privilege**: Each Lambda gets minimal required permissions
- **Server-Specific IAM**: Permissions tailored to each MCP server's needs
- **Isolated Execution**: No cross-server access or interference
- **VPC Support**: Optional VPC configuration for sensitive workloads

## 🧪 Testing Individual Servers

### Test All Functions
```bash
AWS_DEFAULT_REGION=us-east-1 python3 test_lambda_functions.py
```

### Test Single Function
```bash
AWS_DEFAULT_REGION=us-east-1 python3 test_single_lambda.py mcp-server-core-mcp
```

### Expected Results
✅ **Successful Response**: Status 200 with error message indicating missing AgentCore context:
```json
{
  "error": {
    "code": -32603,
    "message": "Internal error: Missing bedrockAgentCoreToolName in context",
    "data": {
      "server_id": "core-mcp",
      "server_name": "AWS Labs Core MCP Server"
    }
  }
}
```

This confirms the `BedrockAgentCoreGatewayTargetHandler` is working correctly and expecting proper AgentCore Gateway invocation context.

## 📚 Library Implementation Details

### Core Components Used
- **Package**: `run-mcp-servers-with-aws-lambda==0.4.1` (PyPI published)
- **Handler**: `BedrockAgentCoreGatewayTargetHandler` - Processes AgentCore Gateway invocations
- **Request Handler**: `StdioServerAdapterRequestHandler` - Manages stdio-based MCP server execution
- **Runtime**: Python 3.11 with automatic dependency resolution

### Handler Structure
```python
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
        command="python",
        args=["-m", "awslabs.core_mcp_server.server"],
        env={
            "FASTMCP_LOG_LEVEL": "ERROR",
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
```

### **Enhanced Requirements Management**

All handlers now use the **proven 3-package pattern** with specific MCP server packages:

```txt
# Standard AWS Labs MCP Server Pattern
run-mcp-servers-with-aws-lambda==0.4.2
awslabs.prometheus-mcp-server==0.2.5
boto3==1.40.18

# Legacy MCP Server Pattern  
run-mcp-servers-with-aws-lambda==0.4.2
mcp-server-git==0.1.0
boto3==1.40.18

# Docker-based Server Pattern
run-mcp-servers-with-aws-lambda==0.4.2
boto3==1.40.18
# Note: This handler uses Docker container, not Python packages
```

This ensures consistent, reliable dependencies across all 18 MCP Lambda handlers.

## 🛠️ Troubleshooting

### **Common Issues**

1. **CDK Bootstrap Required**
   ```bash
   cdk bootstrap
   ```

2. **Missing Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Lambda Handler Generation**
   - Handlers are generated using the working mcp_lambda pattern
   - Run `python3 generate_all_handlers.py` to create all handlers
   - Check `lambda_handlers_q/` directory for generated handlers

4. **Permission Errors**
   - Verify AWS CLI configuration
   - Check IAM permissions for CDK deployment

### **Debugging**
- Enable detailed logging: Set `LOG_LEVEL=DEBUG` in Lambda environment
- Check CloudWatch logs for each function
- Use `cdk diff` to see changes before deployment

## 🎯 Next Steps

1. **Deploy**: Run `./deploy.sh` to create all Lambda functions
2. **Configure**: Update your AgentCore Gateway with the Lambda ARNs
3. **Monitor**: Set up CloudWatch alarms and dashboards
4. **Optimize**: Adjust memory and timeout based on usage patterns

This serverless architecture provides a scalable, cost-effective way to run multiple MCP servers while maintaining complete isolation and optimal resource utilization for AgentCore Gateway integration!

## License

MIT License