#!/usr/bin/env python3
"""
Example usage of the ccapi-mcp Lambda handler.

This file demonstrates how to use the AWS Cloud Control API MCP Server
through various integration methods.
"""

import json
import boto3

def example_direct_lambda_invocation():
    """Example of directly invoking the Lambda function."""
    
    # Initialize Lambda client
    lambda_client = boto3.client('lambda')
    
    # Example 1: List S3 buckets
    list_buckets_event = {
        "toolName": "list_resources",
        "parameters": {
            "resource_type": "AWS::S3::Bucket"
        }
    }
    
    print("Example 1: Listing S3 buckets")
    print(f"Event: {json.dumps(list_buckets_event, indent=2)}")
    
    # Example 2: Get specific S3 bucket details
    get_bucket_event = {
        "toolName": "get_resource", 
        "parameters": {
            "resource_type": "AWS::S3::Bucket",
            "identifier": "my-example-bucket"
        }
    }
    
    print("\nExample 2: Getting S3 bucket details")
    print(f"Event: {json.dumps(get_bucket_event, indent=2)}")
    
    # Example 3: Create a new S3 bucket
    create_bucket_event = {
        "toolName": "create_resource",
        "parameters": {
            "resource_type": "AWS::S3::Bucket",
            "properties": {
                "BucketName": "my-new-example-bucket",
                "PublicAccessBlockConfiguration": {
                    "BlockPublicAcls": True,
                    "BlockPublicPolicy": True,
                    "IgnorePublicAcls": True,
                    "RestrictPublicBuckets": True
                }
            }
        }
    }
    
    print("\nExample 3: Creating a new S3 bucket")
    print(f"Event: {json.dumps(create_bucket_event, indent=2)}")
    
    # Note: Uncomment the following lines to actually invoke the Lambda function
    # response = lambda_client.invoke(
    #     FunctionName='ccapi-mcp-function',
    #     Payload=json.dumps(list_buckets_event)
    # )
    # result = json.loads(response['Payload'].read())
    # print(f"Response: {json.dumps(result, indent=2)}")

def example_bedrock_agentcore_integration():
    """Example of using through Bedrock AgentCore Gateway."""
    
    print("\nBedrock AgentCore Gateway Integration:")
    print("=" * 50)
    
    # Example agent prompt that would use ccapi-mcp tools
    agent_prompts = [
        "List all S3 buckets in my AWS account",
        "Create a new S3 bucket with security best practices",
        "Show me the configuration of my RDS instances", 
        "Update the tags on my EC2 instances",
        "Get the schema information for AWS::Lambda::Function"
    ]
    
    print("Example agent prompts that would use ccapi-mcp tools:")
    for i, prompt in enumerate(agent_prompts, 1):
        print(f"{i}. {prompt}")
    
    print("\nThese prompts would be processed by the agent and converted to")
    print("appropriate ccapi-mcp tool calls through the Bedrock AgentCore Gateway.")

def example_resource_types():
    """Show examples of supported AWS resource types."""
    
    print("\nSupported AWS Resource Types (Examples):")
    print("=" * 50)
    
    resource_types = [
        "AWS::S3::Bucket",
        "AWS::EC2::Instance", 
        "AWS::RDS::DBInstance",
        "AWS::Lambda::Function",
        "AWS::IAM::Role",
        "AWS::CloudFormation::Stack",
        "AWS::EKS::Cluster",
        "AWS::VPC::VPC",
        "AWS::EC2::SecurityGroup",
        "AWS::Route53::HostedZone"
    ]
    
    for resource_type in resource_types:
        print(f"- {resource_type}")
    
    print("\nNote: The Cloud Control API supports many more resource types.")
    print("Use the get_resource_schema_information tool to explore available types.")

def example_security_features():
    """Demonstrate security features of the ccapi-mcp handler."""
    
    print("\nSecurity Features:")
    print("=" * 50)
    
    security_features = {
        "Default Tagging": "Automatically tags created resources for tracking",
        "Security Scanning": "Scans resource configurations for security issues",
        "IAM Integration": "Uses Lambda execution role for secure AWS access",
        "Audit Logging": "Logs all resource operations for compliance",
        "Error Handling": "Secure error messages without sensitive data exposure"
    }
    
    for feature, description in security_features.items():
        print(f"• {feature}: {description}")

def main():
    """Run all examples."""
    print("AWS Cloud Control API MCP Server - Usage Examples")
    print("=" * 60)
    
    example_direct_lambda_invocation()
    example_bedrock_agentcore_integration()
    example_resource_types()
    example_security_features()
    
    print("\n" + "=" * 60)
    print("For more information, see README.md")
    print("To test the implementation, run: python3 test_handler.py")
    print("To deploy, run: ./deploy.sh")

if __name__ == "__main__":
    main()