# Multi-MCP Lambda Deployment Guide

This guide walks you through deploying multiple MCP servers as individual Lambda functions for AgentCore Gateway integration.

## 🎯 Architecture Overview

```
AgentCore Gateway
├── AWS Labs MCP Servers (15)
│   ├── Core MCP → Lambda Function (core-mcp)
│   ├── AWS Documentation → Lambda Function (aws-docs)
│   ├── AWS Pricing → Lambda Function (aws-pricing)
│   ├── Frontend MCP → Lambda Function (frontend-mcp)
│   ├── AWS Location → Lambda Function (aws-location)
│   ├── Git Repo Research → Lambda Function (git-repo-research)
│   ├── EKS MCP → Lambda Function (eks-mcp)
│   ├── AWS Diagram → Lambda Function (aws-diagram)
│   ├── Prometheus → Lambda Function (prometheus)
│   ├── CloudFormation → Lambda Function (cfn-mcp)
│   ├── Terraform → Lambda Function (terraform-mcp)
│   ├── AWS Knowledge → Lambda Function (aws-knowledge)
│   ├── CloudWatch → Lambda Function (cloudwatch-mcp)
│   ├── CloudWatch AppSignals → Lambda Function (cloudwatch-appsignals)
│   └── Cloud Control API → Lambda Function (ccapi-mcp)
└── Third-party MCP Servers (3)
    ├── GitHub → Lambda Function (github)
    ├── Git Repository (Legacy) → Lambda Function (git-repo)
    └── Filesystem → Lambda Function (filesystem)
```

Each MCP server gets its own dedicated Lambda function for:
- **Isolation**: Independent scaling and failure isolation
- **Optimization**: Right-sized resources per server
- **Management**: Individual monitoring and updates

## 🚀 Quick Deployment

### 1. **Configure Servers**
The project comes pre-configured with 18 MCP servers in `servers.yaml`. You can customize which servers to deploy:

```yaml
servers:
  core-mcp:
    name: "AWS Labs Core MCP Server"
    command: "uvx"
    args: ["awslabs.core-mcp-server@latest"]
    timeout: 60
    memory: 1024

  eks-mcp:
    name: "AWS EKS MCP Server"
    command: "uvx"
    args: ["awslabs.eks-mcp-server@latest", "--allow-write", "--allow-sensitive-data-access"]
    timeout: 120
    memory: 2048
```

### 2. **Generate & Test**
```bash
# Generate Lambda configurations
python3 generate_configs.py

# Test all servers locally
python3 test_multi.py
```

### 3. **Deploy to AWS**
```bash
# Deploy all Lambda functions
./deploy_multi.sh
```

### 4. **Get Lambda ARNs**
After deployment, copy the Lambda ARNs from the CDK output (18 total):

```
# AWS Labs MCP Servers
McpCoremcpLambdaArn = arn:aws:lambda:us-east-1:ACCOUNT:function:mcp-server-core-mcp
McpAwspricingLambdaArn = arn:aws:lambda:us-east-1:ACCOUNT:function:mcp-server-aws-pricing
McpAwsdocsLambdaArn = arn:aws:lambda:us-east-1:ACCOUNT:function:mcp-server-aws-docs
McpFrontendmcpLambdaArn = arn:aws:lambda:us-east-1:ACCOUNT:function:mcp-server-frontend-mcp
McpAwslocationLambdaArn = arn:aws:lambda:us-east-1:ACCOUNT:function:mcp-server-aws-location
McpGitreporesearchLambdaArn = arn:aws:lambda:us-east-1:ACCOUNT:function:mcp-server-git-repo-research
McpEksmcpLambdaArn = arn:aws:lambda:us-east-1:ACCOUNT:function:mcp-server-eks-mcp
McpAwsdiagramLambdaArn = arn:aws:lambda:us-east-1:ACCOUNT:function:mcp-server-aws-diagram
McpPrometheusLambdaArn = arn:aws:lambda:us-east-1:ACCOUNT:function:mcp-server-prometheus
McpCfnmcpLambdaArn = arn:aws:lambda:us-east-1:ACCOUNT:function:mcp-server-cfn-mcp
McpTerraformmcpLambdaArn = arn:aws:lambda:us-east-1:ACCOUNT:function:mcp-server-terraform-mcp
McpAwsknowledgeLambdaArn = arn:aws:lambda:us-east-1:ACCOUNT:function:mcp-server-aws-knowledge
McpCloudwatchmcpLambdaArn = arn:aws:lambda:us-east-1:ACCOUNT:function:mcp-server-cloudwatch-mcp
McpCloudwatchappsignalsLambdaArn = arn:aws:lambda:us-east-1:ACCOUNT:function:mcp-server-cloudwatch-appsignals
McpCcapimcpLambdaArn = arn:aws:lambda:us-east-1:ACCOUNT:function:mcp-server-ccapi-mcp

# Third-party MCP Servers
McpGithubLambdaArn = arn:aws:lambda:us-east-1:ACCOUNT:function:mcp-server-github
McpGitrepoLambdaArn = arn:aws:lambda:us-east-1:ACCOUNT:function:mcp-server-git-repo
McpFilesystemLambdaArn = arn:aws:lambda:us-east-1:ACCOUNT:function:mcp-server-filesystem
```

## 🔧 Management Commands

Use the management script for common operations:

```bash
# List all configured servers
python3 manage.py list

# Check deployment status
python3 manage.py status

# Add a new server interactively
python3 manage.py add

# Remove a server
python3 manage.py remove

# Test specific server
python3 manage.py test aws-docs

# Deploy all servers
python3 manage.py deploy
```

## 🎛️ AgentCore Gateway Configuration

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
      "description": "AWS Documentation search and retrieval"
    },
    "aws-pricing": {
      "type": "lambda", 
      "arn": "arn:aws:lambda:us-east-1:ACCOUNT:function:mcp-server-aws-pricing",
      "description": "AWS service pricing information"
    },
    "eks-mcp": {
      "type": "lambda",
      "arn": "arn:aws:lambda:us-east-1:ACCOUNT:function:mcp-server-eks-mcp",
      "description": "Amazon EKS cluster management and troubleshooting"
    },
    "github": {
      "type": "lambda",
      "arn": "arn:aws:lambda:us-east-1:ACCOUNT:function:mcp-server-github",
      "description": "GitHub repository and issue management"
    },
    "cloudwatch-mcp": {
      "type": "lambda",
      "arn": "arn:aws:lambda:us-east-1:ACCOUNT:function:mcp-server-cloudwatch-mcp",
      "description": "CloudWatch logs and metrics analysis"
    },
    "terraform-mcp": {
      "type": "lambda",
      "arn": "arn:aws:lambda:us-east-1:ACCOUNT:function:mcp-server-terraform-mcp",
      "description": "Terraform infrastructure management"
    }
    // ... configure remaining 11 servers as needed
  }
}
```

## 📊 Monitoring & Observability

Each Lambda function provides:

### **CloudWatch Logs**
- Log Group: `/aws/lambda/mcp-server-{server-id}`
- Real-time debugging and error tracking

### **CloudWatch Metrics**
- Invocations, Duration, Errors per server
- Memory utilization per server
- Cold start metrics

### **Cost Tracking**
- Per-server cost breakdown
- Usage patterns per MCP server
- Right-sizing recommendations

## 🔐 Security & Permissions

### **IAM Roles**
Each Lambda gets a dedicated IAM role with:
- Basic Lambda execution permissions
- Server-specific AWS service permissions
- Principle of least privilege

### **Network Security**
- VPC isolation (optional)
- Security groups per function
- Private subnet deployment

## 🛠️ Customization

### **Adding New Servers**
1. Add to `servers.yaml`:
```yaml
my-custom-server:
  name: "My Custom MCP Server"
  command: "python"
  args: ["/path/to/my_server.py"]
  timeout: 45
  memory: 768
```

2. Generate configs: `python3 generate_configs.py`
3. Deploy: `./deploy_multi.sh`

### **Server-Specific Configuration**
Each server can have:
- Custom environment variables
- Different timeout/memory settings
- Specific IAM permissions
- Custom deployment parameters

## 🧪 Testing

### **Local Testing**
```bash
# Test all servers
python3 test_multi.py

# Test specific server
python3 manage.py test aws-docs
```

### **API Gateway Testing**
Each server gets a test API endpoint:
```bash
curl -X POST [SERVER_API_URL] \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

### **Lambda Console Testing**
Use AWS Lambda console to test individual functions with sample MCP requests.

## 🚨 Troubleshooting

### **Common Issues**

1. **Server startup timeout**
   - Increase timeout in `servers.yaml`
   - Check server dependencies

2. **Memory issues**
   - Increase memory allocation
   - Monitor CloudWatch metrics

3. **Permission errors**
   - Check IAM role permissions
   - Verify server-specific permissions

### **Debugging Steps**

1. Check CloudWatch logs: `/aws/lambda/mcp-server-{server-id}`
2. Test locally: `python3 manage.py test {server-id}`
3. Verify configuration: `python3 manage.py list`
4. Check deployment: `python3 manage.py status`

## 💰 Cost Optimization

### **Right-sizing**
- Monitor memory usage per server
- Adjust timeout based on actual needs
- Use provisioned concurrency for high-traffic servers

### **Usage Patterns**
- Track invocations per server
- Identify unused servers
- Optimize based on usage patterns

## 🔄 Updates & Maintenance

### **Updating Servers**
1. Modify `servers.yaml`
2. Run `python3 generate_configs.py`
3. Deploy: `./deploy_multi.sh`

### **Rolling Updates**
- Update servers individually
- Test before full deployment
- Monitor during rollout

This architecture provides maximum flexibility and isolation for running multiple MCP servers in a serverless environment!