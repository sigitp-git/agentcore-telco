"""
Multi-Lambda CDK Stack for MCP Servers

Creates one Lambda function per MCP server for 1:1 mapping.
"""

from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda,
    aws_lambda_python_alpha as lambda_python,
    aws_apigateway as apigateway,
    aws_iam as iam,
)
from constructs import Construct
from typing import Dict, Any
import json
import os


class MultiMcpLambdaStack(Stack):
    """CDK Stack that creates multiple Lambda functions, one per MCP server."""

    def __init__(self, scope: Construct, construct_id: str, servers: Dict[str, Any], **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.servers = servers
        self.lambda_functions = {}
        self.lambda_arns = {}
        self.api_gateways = {}
        self.api_urls = {}

        # Create a Lambda function for each MCP server
        for server_id, server_config in servers.items():
            self._create_lambda_for_server(server_id, server_config)

    def _create_lambda_for_server(self, server_id: str, config: Dict[str, Any]):
        """Create a Lambda function for a specific MCP server."""
        
        # Create a unique directory for this server's Lambda code
        lambda_dir = f"lambda-{server_id}"
        self._prepare_lambda_code(lambda_dir, server_id, config)

        # Filter out reserved environment variables
        env_vars = config.get('env', {}).copy()
        reserved_vars = ['AWS_REGION', 'AWS_DEFAULT_REGION', 'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_SESSION_TOKEN']
        for var in reserved_vars:
            if var in env_vars:
                del env_vars[var]

        # Create the Lambda function
        lambda_function = lambda_python.PythonFunction(
            self,
            f"McpServer{server_id.replace('-', '').title()}Function",
            entry=lambda_dir,
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="handler.lambda_handler",
            timeout=Duration.seconds(config.get('timeout', 60)),
            memory_size=config.get('memory', 1024),
            environment={
                "LOG_LEVEL": "INFO",
                "PYTHONUNBUFFERED": "1",
                "MCP_SERVER_ID": server_id,
                **env_vars
            },
            description=f"MCP Server: {config['name']}",
            function_name=f"mcp-server-{server_id}",
        )

        # Add basic IAM permissions
        lambda_function.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                ],
                resources=["*"],
            )
        )

        # Add server-specific permissions if needed
        self._add_server_specific_permissions(lambda_function, server_id, config)

        # Create API Gateway for testing
        api = apigateway.LambdaRestApi(
            self,
            f"McpServer{server_id.replace('-', '').title()}Api",
            handler=lambda_function,
            description=f"API Gateway for {config['name']} (testing only)",
            rest_api_name=f"mcp-server-{server_id}-api",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
            ),
        )

        # Store references
        self.lambda_functions[server_id] = lambda_function
        self.lambda_arns[server_id] = lambda_function.function_arn
        self.api_gateways[server_id] = api
        self.api_urls[server_id] = api.url

    def _prepare_lambda_code(self, lambda_dir: str, server_id: str, config: Dict[str, Any]):
        """Prepare Lambda code directory for a specific server."""
        import shutil
        
        # Create the lambda directory
        os.makedirs(lambda_dir, exist_ok=True)
        
        # Copy base Lambda files
        base_files = [
            "lambda/handler.py",
            "lambda/mcp_wrapper.py",
            "lambda/requirements.txt"
        ]
        
        for file_path in base_files:
            if os.path.exists(file_path):
                shutil.copy2(file_path, lambda_dir)
        
        # Create server-specific config.py
        config_content = f"""'''
MCP Server Configuration for {server_id}

Auto-generated configuration for {config['name']}.
'''

# Configuration for the MCP server to wrap
MCP_SERVER_CONFIG = {json.dumps({
    "command": config["command"],
    "args": config["args"],
    "env": config.get("env", {})
}, indent=4)}
"""
        
        with open(f"{lambda_dir}/config.py", "w") as f:
            f.write(config_content)

    def _add_server_specific_permissions(self, lambda_function: _lambda.Function, server_id: str, config: Dict[str, Any]):
        """Add server-specific IAM permissions."""
        
        # EKS MCP Server - needs EKS and CloudWatch permissions
        if server_id == "eks-mcp":
            lambda_function.add_to_role_policy(
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "eks:DescribeCluster",
                        "eks:ListClusters",
                        "eks:DescribeNodegroup",
                        "eks:ListNodegroups",
                        "logs:DescribeLogGroups",
                        "logs:DescribeLogStreams",
                        "logs:GetLogEvents",
                        "logs:FilterLogEvents",
                        "logs:StartQuery",
                        "logs:StopQuery",
                        "logs:GetQueryResults",
                    ],
                    resources=["*"],
                )
            )
            
        # CloudWatch MCP Server - needs CloudWatch permissions
        elif server_id == "cloudwatch-mcp":
            lambda_function.add_to_role_policy(
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "logs:DescribeLogGroups",
                        "logs:DescribeLogStreams",
                        "logs:GetLogEvents",
                        "logs:FilterLogEvents",
                        "logs:StartQuery",
                        "logs:StopQuery",
                        "logs:GetQueryResults",
                        "cloudwatch:GetMetricData",
                        "cloudwatch:GetMetricStatistics",
                        "cloudwatch:ListMetrics",
                    ],
                    resources=["*"],
                )
            )
            
        # CloudWatch Application Signals - needs Application Signals permissions
        elif server_id == "cloudwatch-appsignals":
            lambda_function.add_to_role_policy(
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "application-signals:GetService",
                        "application-signals:ListServices",
                        "application-signals:GetServiceLevelObjective",
                        "application-signals:ListServiceLevelObjectives",
                        "cloudwatch:GetMetricData",
                        "xray:GetTraceSummaries",
                        "xray:BatchGetTraces",
                    ],
                    resources=["*"],
                )
            )
            
        # Prometheus server - needs AMP permissions
        elif server_id == "prometheus":
            lambda_function.add_to_role_policy(
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "aps:QueryMetrics",
                        "aps:GetSeries",
                        "aps:GetLabels",
                        "aps:GetMetricMetadata",
                        "aps:DescribeWorkspace",
                        "aps:ListWorkspaces",
                    ],
                    resources=["*"],
                )
            )
            
        # CloudFormation MCP Server - needs CloudFormation permissions
        elif server_id == "cfn-mcp":
            lambda_function.add_to_role_policy(
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "cloudformation:DescribeStacks",
                        "cloudformation:DescribeStackResources",
                        "cloudformation:DescribeStackEvents",
                        "cloudformation:GetTemplate",
                        "cloudformation:ListStacks",
                        "cloudformation:ValidateTemplate",
                    ],
                    resources=["*"],
                )
            )
            
        # Terraform MCP Server - might need S3 for state files
        elif server_id == "terraform-mcp":
            lambda_function.add_to_role_policy(
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "s3:GetObject",
                        "s3:PutObject",
                        "s3:ListBucket",
                        "dynamodb:GetItem",
                        "dynamodb:PutItem",
                        "dynamodb:DeleteItem",
                    ],
                    resources=["*"],  # Should be restricted to specific buckets/tables
                )
            )
            
        # AWS Location MCP Server - needs Location Service permissions
        elif server_id == "aws-location":
            lambda_function.add_to_role_policy(
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "geo:SearchPlaceIndexForText",
                        "geo:SearchPlaceIndexForPosition",
                        "geo:GetPlace",
                        "geo:CalculateRoute",
                        "geo:CalculateRouteMatrix",
                    ],
                    resources=["*"],
                )
            )
            
        # Cloud Control API MCP Server - needs broad AWS permissions
        elif server_id == "ccapi-mcp":
            lambda_function.add_to_role_policy(
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "cloudcontrol:CreateResource",
                        "cloudcontrol:DeleteResource",
                        "cloudcontrol:GetResource",
                        "cloudcontrol:ListResources",
                        "cloudcontrol:UpdateResource",
                        "cloudcontrol:GetResourceRequestStatus",
                    ],
                    resources=["*"],
                )
            )
            
        # AWS Pricing server - no additional permissions needed
        elif server_id == "aws-pricing":
            pass
            
        # AWS Documentation server - no additional permissions needed
        elif server_id == "aws-docs":
            pass
            
        # Core MCP server - no additional permissions needed
        elif server_id == "core-mcp":
            pass
            
        # Frontend MCP server - no additional permissions needed
        elif server_id == "frontend-mcp":
            pass
            
        # Git servers - no AWS permissions needed
        elif server_id in ["git-repo", "git-repo-research"]:
            pass
            
        # GitHub server - no AWS permissions needed
        elif server_id == "github":
            pass
            
        # AWS Knowledge server - no additional permissions needed (uses proxy)
        elif server_id == "aws-knowledge":
            pass
            
        # AWS Diagram server - no additional permissions needed
        elif server_id == "aws-diagram":
            pass
            
        # Filesystem server - limited to /tmp in Lambda
        elif server_id == "filesystem":
            pass