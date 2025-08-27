"""
CDK Stack for MCP Lambda Server

Defines the AWS infrastructure needed to run the MCP server on Lambda.
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


class McpLambdaStack(Stack):
    """CDK Stack for the MCP Lambda server."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create the Lambda function for MCP server wrapper
        self.mcp_lambda = lambda_python.PythonFunction(
            self,
            "McpServerFunction",
            entry="lambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="handler.lambda_handler",
            timeout=Duration.seconds(60),  # Increased timeout for MCP server startup
            memory_size=1024,  # Increased memory for running subprocess
            environment={
                "LOG_LEVEL": "INFO",
                "PYTHONUNBUFFERED": "1",  # Ensure logs are flushed immediately
            },
            description="MCP Server Wrapper running on AWS Lambda",
        )

        # Add necessary IAM permissions for AWS service access
        # These permissions depend on which MCP server you're wrapping
        self.mcp_lambda.add_to_role_policy(
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
        
        # Add permissions for AWS Documentation MCP server (if using that server)
        self.mcp_lambda.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    # Add specific permissions based on your MCP server needs
                    # For AWS Documentation server, no additional permissions needed
                ],
                resources=["*"],
            )
        )

        # Create API Gateway for HTTP access (optional - mainly for testing)
        # AgentCore Gateway will invoke the Lambda directly
        self.api = apigateway.LambdaRestApi(
            self,
            "McpServerApi",
            handler=self.mcp_lambda,
            description="API Gateway for MCP Lambda server (testing only)",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
            ),
        )

        # Output the Lambda function ARN for AgentCore Gateway configuration
        self.lambda_arn = self.mcp_lambda.function_arn
        self.api_url = self.api.url