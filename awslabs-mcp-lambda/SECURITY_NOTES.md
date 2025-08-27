# Security Configuration Notes

## 🔐 Sensitive Environment Variables

Some MCP servers require sensitive credentials that should NOT be hardcoded in the configuration files. These should be set via AWS Lambda environment variables or AWS Secrets Manager.

### Servers Requiring Manual Security Configuration

#### 1. **Git Repository Research MCP Server** (`git-repo-research`)
- **Variable**: `GITHUB_TOKEN`
- **Current**: Removed from config for security
- **Action Required**: Set via Lambda environment variables
```bash
aws lambda update-function-configuration \
  --function-name mcp-server-git-repo-research \
  --environment Variables='{GITHUB_TOKEN=your_github_token_here}'
```

#### 2. **GitHub MCP Server** (`github`)
- **Variable**: `GITHUB_PERSONAL_ACCESS_TOKEN`
- **Current**: Removed from config for security
- **Action Required**: Set via Lambda environment variables
```bash
aws lambda update-function-configuration \
  --function-name mcp-server-github \
  --environment Variables='{GITHUB_PERSONAL_ACCESS_TOKEN=your_github_token_here}'
```

#### 3. **AWS Cloud Control API MCP Server** (`ccapi-mcp`)
- **Variable**: `AWS_PROFILE`
- **Current**: Removed (not applicable in Lambda)
- **Action Required**: Use Lambda execution role instead

## 🛡️ Security Best Practices

### 1. **Use AWS Secrets Manager**
For production deployments, store sensitive tokens in AWS Secrets Manager:

```python
# Example: Modify Lambda code to fetch from Secrets Manager
import boto3
import json

def get_secret(secret_name):
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

# In your Lambda function
github_token = get_secret('github-token')['token']
```

### 2. **Lambda Environment Variables**
Set sensitive variables via AWS CLI or CDK:

```typescript
// CDK Example
new lambda.Function(this, 'McpFunction', {
  // ... other config
  environment: {
    GITHUB_TOKEN: secretsManager.Secret.fromSecretNameV2(
      this, 'GitHubToken', 'github-token'
    ).secretValue.toString()
  }
});
```

### 3. **IAM Permissions**
Each Lambda function gets minimal required permissions:

- **EKS MCP**: EKS cluster access, CloudWatch logs
- **CloudWatch MCP**: CloudWatch read permissions
- **Terraform MCP**: S3 state bucket access (if needed)
- **GitHub MCP**: No AWS permissions needed

### 4. **Network Security**
Consider deploying Lambda functions in VPC for additional security:

```yaml
# In servers.yaml, add vpc configuration
servers:
  eks-mcp:
    # ... existing config
    vpc:
      subnet_ids: ["subnet-12345", "subnet-67890"]
      security_group_ids: ["sg-abcdef"]
```

## 🔧 Post-Deployment Security Setup

After deploying the Lambda functions, run these commands to set sensitive environment variables:

```bash
# Set GitHub token for git-repo-research server
aws lambda update-function-configuration \
  --function-name mcp-server-git-repo-research \
  --environment Variables='{
    "AWS_REGION":"us-east-1",
    "FASTMCP_LOG_LEVEL":"ERROR",
    "GITHUB_TOKEN":"your_github_token_here"
  }'

# Set GitHub token for github server
aws lambda update-function-configuration \
  --function-name mcp-server-github \
  --environment Variables='{
    "GITHUB_PERSONAL_ACCESS_TOKEN":"your_github_token_here",
    "FASTMCP_LOG_LEVEL":"ERROR"
  }'
```

## 🚨 Security Warnings

1. **Never commit tokens to version control**
2. **Rotate tokens regularly**
3. **Use least-privilege IAM roles**
4. **Monitor Lambda function logs for security events**
5. **Enable AWS CloudTrail for audit logging**

## 📋 Security Checklist

- [ ] Remove hardcoded tokens from configuration files
- [ ] Set up AWS Secrets Manager for sensitive values
- [ ] Configure Lambda environment variables securely
- [ ] Review IAM permissions for each function
- [ ] Enable CloudTrail logging
- [ ] Set up CloudWatch alarms for security events
- [ ] Test with minimal required permissions
- [ ] Document security procedures for your team