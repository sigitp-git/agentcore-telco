"""
AWS Labs MCP Lambda Stack

Creates individual Lambda functions for each MCP server defined in servers.yaml.
Uses the proven mcp_lambda library pattern with BedrockAgentCoreGatewayTargetHandler
for reliable serverless MCP deployment with AgentCore Gateway integration.

Each Lambda function:
- Uses the working mcp_lambda library pattern from lambda_handlers_q/
- Extracts AWS credentials from Lambda execution role automatically
- Implements MockClientContext for missing bedrockAgentCoreToolName
- Handles StdioServerParameters configuration for MCP servers
"""

import os
from typing import Dict, Any
from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda,
    aws_iam as iam,
)
from aws_cdk.aws_lambda_python_alpha import PythonFunction
from constructs import Construct


class McpLambdaStack(Stack):
    """CDK Stack that creates Lambda functions for MCP servers"""

    def __init__(self, scope: Construct, construct_id: str, servers: Dict[str, Any], **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        self.servers = servers
        self.lambda_functions = {}
        self.lambda_arns = {}
        
        # Create Lambda functions for each MCP server
        for server_id, config in servers.items():
            self._create_lambda_function(server_id, config)

    def _create_lambda_function(self, server_id: str, config: Dict[str, Any]) -> None:
        """Create a Lambda function for a specific MCP server"""
        
        function_name = f"mcp-server-{server_id}"
        
        # Create IAM role for the Lambda function
        lambda_role = self._create_lambda_role(server_id, config)
        
        # Prepare environment variables for the new mcp_lambda pattern
        # The new handlers extract AWS credentials from execution role automatically
        # and configure the MCP server parameters directly in the handler code
        env_vars = {}
        
        # Add server-specific env vars, but skip reserved Lambda variables
        reserved_vars = {'AWS_REGION', 'AWS_DEFAULT_REGION', 'AWS_LAMBDA_FUNCTION_NAME', 
                        'AWS_LAMBDA_FUNCTION_VERSION', 'AWS_LAMBDA_FUNCTION_MEMORY_SIZE',
                        'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_SESSION_TOKEN'}
        
        for key, value in config.get('env', {}).items():
            if key not in reserved_vars:
                env_vars[key] = value
        
        # Lambda will create log groups automatically
        
        # Create Lambda function with Python dependencies
        lambda_function = PythonFunction(
            self,
            f"McpLambda{server_id.replace('-', '').title()}",
            function_name=function_name,
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="lambda_function.lambda_handler",
            entry=f"lambda_handlers_q/{server_id}",
            role=lambda_role,
            timeout=Duration.seconds(config.get('timeout', 60)),
            memory_size=config.get('memory', 1024),
            environment=env_vars,
            description=config.get('description', f"MCP Server: {config['name']}"),
            # PythonFunction automatically handles requirements.txt from lambda_handlers_q/{server_id}/
        )
        
        self.lambda_functions[server_id] = lambda_function
        self.lambda_arns[server_id] = lambda_function.function_arn

    def _create_lambda_role(self, server_id: str, config: Dict[str, Any]) -> iam.Role:
        """Create IAM role with appropriate permissions for the MCP server"""
        
        role_name = f"mcp-lambda-{server_id}-role"
        
        # Base Lambda execution role
        lambda_role = iam.Role(
            self,
            f"McpLambdaRole{server_id.replace('-', '').title()}",
            role_name=role_name,
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ],
            description=f"IAM role for MCP Lambda function: {config['name']}"
        )
        
        # Add server-specific permissions
        self._add_server_permissions(lambda_role, server_id, config)
        
        return lambda_role

    def _add_server_permissions(self, role: iam.Role, server_id: str, config: Dict[str, Any]) -> None:
        """Add server-specific IAM permissions"""
        
        # Common AWS permissions that most MCP servers need
        common_permissions = [
            "sts:GetCallerIdentity",
            "sts:AssumeRole"
        ]
        
        # Server-specific permissions mapping
        server_permissions = {
            'core-mcp': [
                "bedrock:*",
                "ssm:GetParameter",
                "ssm:GetParameters"
            ],
            'aws-pricing': [
                "pricing:*",
                "ec2:DescribeRegions"
            ],
            'aws-docs': [
                "bedrock:InvokeModel"
            ],
            'aws-location': [
                "geo:*"
            ],
            'git-repo-research': [
                "bedrock:InvokeModel",
                "s3:GetObject",
                "s3:PutObject"
            ],
            'eks-mcp': [
                "eks:*",
                "ec2:Describe*",
                "iam:ListRoles",
                "iam:GetRole",
                "logs:*",
                "cloudformation:*"
            ],
            'aws-diagram': [
                "bedrock:InvokeModel"
            ],
            'prometheus': [
                "aps:*",
                "logs:*"
            ],
            'cfn-mcp': [
                "cloudformation:*",
                "s3:GetObject",
                "s3:PutObject"
            ],
            'terraform-mcp': [
                "s3:*",
                "dynamodb:*",
                "ec2:*",
                "iam:*"
            ],
            'cloudwatch-mcp': [
                "logs:*",
                "cloudwatch:*"
            ],
            'cloudwatch-appsignals': [
                "logs:*",
                "cloudwatch:*",
                "application-signals:*"
            ],
            'ccapi-mcp': [
                "cloudcontrol:*",
                "cloudformation:*"
            ],
            'github': [
                # GitHub MCP server - no AWS permissions needed
            ],
            'git-repo': [
                # Git repo MCP server - no AWS permissions needed  
            ],
            'filesystem': [
                # Filesystem MCP server - only needs /tmp access (built-in)
            ],
            'frontend-mcp': [
                "bedrock:InvokeModel"
            ]
        }
        
        # Get permissions for this server
        permissions = common_permissions + server_permissions.get(server_id, [])
        
        if permissions:
            role.add_to_policy(
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=permissions,
                    resources=["*"]
                )
            )