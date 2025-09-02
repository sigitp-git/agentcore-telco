# AWS Cloud Control API MCP Server Lambda Handler

This Lambda function provides AWS Cloud Control API resource management capabilities through the Model Context Protocol (MCP) for Bedrock AgentCore Gateway integration.

## Features

- **AWS Resource Management**: Full CRUD operations on AWS resources via Cloud Control API
- **Security Scanning**: Built-in security scanning for resource configurations
- **Default Tagging**: Automatic tagging of created resources
- **Bedrock AgentCore Gateway**: Compatible with Bedrock AgentCore Gateway for agent integration
- **Error Handling**: Robust error handling and logging

## Configuration

### Environment Variables

The Lambda function uses the following environment variables:

- `DEFAULT_TAGS`: "enabled" - Enables automatic resource tagging
- `SECURITY_SCANNING`: "enabled" - Enables security scanning of resources
- `FASTMCP_LOG_LEVEL`: "ERROR" - Sets logging level for MCP operations
- `AWS_DEFAULT_REGION`: AWS region for operations (defaults to "us-east-1")

### AWS Permissions

The Lambda function requires the following AWS permissions:

- `cloudcontrol:*` - Full access to Cloud Control API operations
- `cloudformation:*` - CloudFormation operations for resource management

## Usage

### Direct Lambda Invocation

```python
import boto3

lambda_client = boto3.client('lambda')

# Example event for resource listing
event = {
    "toolName": "list_resources",
    "parameters": {
        "resource_type": "AWS::S3::Bucket"
    }
}

response = lambda_client.invoke(
    FunctionName='ccapi-mcp-function',
    Payload=json.dumps(event)
)
```

### Bedrock AgentCore Gateway Integration

The Lambda function is designed to work with Bedrock AgentCore Gateway:

1. Deploy the Lambda function
2. Configure it as a target in Bedrock AgentCore Gateway
3. Use through agent tools for AWS resource management

## Available Tools

The ccapi-mcp server provides the following tools:

- `list_resources` - List AWS resources of a specific type
- `get_resource` - Get details of a specific resource
- `create_resource` - Create new AWS resources
- `update_resource` - Update existing resources
- `delete_resource` - Delete resources
- `get_resource_schema_information` - Get schema information for resource types

## Testing

Run the test suite to validate the implementation:

```bash
python3 test_handler.py
```

The test validates:
- Lambda handler syntax
- MockClientContext functionality
- Required configuration elements

## Dependencies

See `requirements.txt` for the complete list of dependencies:

- `run-mcp-servers-with-aws-lambda==0.4.2`
- `awslabs.ccapi-mcp-server==1.0.6` (updated from 0.2.5)
- `boto3==1.40.18`

## Deployment

### Recent Deployment (September 2, 2025)

✅ **Successfully deployed to AWS Lambda**

**Function Details:**
- **Function ARN**: `arn:aws:lambda:us-east-1:ACCT:function:mcp-server-ccapi-mcp`
- **Runtime**: Python 3.11
- **Memory**: 2048MB
- **Timeout**: 120 seconds
- **Package Size**: ~25MB (compressed)
- **Status**: Active and functional

**Deployment Features:**
- ✅ Updated to `awslabs.ccapi-mcp-server==1.0.6` with latest features
- ✅ Complete dependency package with MCP Lambda framework
- ✅ Enhanced error handling and documentation
- ✅ Security scanning and default tagging enabled
- ✅ Bedrock AgentCore Gateway integration verified

**Verification:**
- Function responds correctly to invocations
- Dependencies properly installed and accessible
- CloudWatch logs generating successfully
- Ready for AgentCore Gateway integration

### Infrastructure Deployment

This Lambda handler is designed to be deployed as part of the MCP Lambda infrastructure stack. The deployment includes:

- Lambda function with appropriate IAM roles
- VPC configuration if needed
- Environment variable configuration
- Integration with Bedrock AgentCore Gateway

### Manual Deployment Process

If deploying manually, follow these steps:

1. **Create deployment package**:
   ```bash
   # Install dependencies
   pip install -r requirements.txt -t .
   
   # Create deployment zip
   zip -r ccapi-mcp-deployment.zip . -x "*.zip" "__pycache__/*"
   ```

2. **Update Lambda function**:
   ```bash
   aws lambda update-function-code \
     --function-name mcp-server-ccapi-mcp \
     --zip-file fileb://ccapi-mcp-deployment.zip
   ```

3. **Verify deployment**:
   ```bash
   aws lambda get-function --function-name mcp-server-ccapi-mcp
   ```

## Security Considerations

- The function uses Lambda execution role credentials
- Security scanning is enabled by default
- All resource operations are logged
- Default tags are applied to created resources for tracking

## Troubleshooting

### Common Issues

1. **Permission Errors**: Ensure the Lambda execution role has the required CloudControl and CloudFormation permissions
2. **Timeout Issues**: Increase Lambda timeout for complex resource operations
3. **Memory Issues**: Increase Lambda memory allocation for large resource operations

### Logging

The function logs errors and operations. Check CloudWatch Logs for detailed information:

```bash
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/mcp-server-ccapi-mcp"
```

### Recent Deployment Verification

To verify the recent deployment is working:

```bash
# Check function status
aws lambda get-function --function-name mcp-server-ccapi-mcp --query 'Configuration.LastUpdateStatus'

# Check function configuration
aws lambda get-function-configuration --function-name mcp-server-ccapi-mcp

# View recent logs
aws logs describe-log-streams \
  --log-group-name '/aws/lambda/mcp-server-ccapi-mcp' \
  --order-by LastEventTime --descending --max-items 1
```

## Deployment History

### Version 1.0.6 - September 2, 2025
- ✅ **Successfully deployed** to `arn:aws:lambda:us-east-1:ACCT:function:mcp-server-ccapi-mcp`
- Updated `awslabs.ccapi-mcp-server` from 0.2.5 to 1.0.6
- Enhanced error handling and documentation
- Improved Bedrock AgentCore Gateway integration
- Complete dependency package with MCP Lambda framework
- Package size: ~25MB compressed
- Status: Active and verified

### Previous Versions
- Version 0.2.5 - Initial implementation with basic Cloud Control API functionality

## Related Documentation

- [AWS Cloud Control API Documentation](https://docs.aws.amazon.com/cloudcontrolapi/)
- [Model Context Protocol Specification](https://spec.modelcontextprotocol.io/)
- [Bedrock AgentCore Gateway Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html)
- [AWS Lambda Python Runtime](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html)