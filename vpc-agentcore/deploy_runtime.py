#!/usr/bin/env python3
"""
Deployment script for VPC Agent to Amazon Bedrock AgentCore Runtime.
"""

import boto3
import json
import time
import subprocess
import sys
import os
import argparse
from datetime import datetime
from utils import get_ssm_parameter, put_ssm_parameter

# Set default AWS region
DEFAULT_REGION = 'us-east-1'

def setup_aws_region():
    """Setup AWS region configuration."""
    # Check for region in environment variables
    region = os.environ.get('AWS_DEFAULT_REGION') or os.environ.get('AWS_REGION')
    
    if not region:
        # Try to get region from AWS config
        try:
            session = boto3.Session()
            region = session.region_name
        except Exception:
            region = None
    
    if not region:
        region = DEFAULT_REGION
        print(f"⚠️  No AWS region configured, using default: {region}")
    
    # Validate region format (basic check)
    if not region or len(region) < 3 or '-' not in region:
        print(f"⚠️  Invalid region format: {region}, using default: {DEFAULT_REGION}")
        region = DEFAULT_REGION
    
    # Set environment variables to ensure consistency
    os.environ['AWS_DEFAULT_REGION'] = region
    os.environ['AWS_REGION'] = region
    
    print(f"🌍 AWS region configured: {region}")
    return region

def print_usage_help():
    """Print usage help and examples."""
    print("\n💡 Usage Examples:")
    print("   python3 deploy_runtime.py                    # Deploy with auto-detected region")
    print("   python3 deploy_runtime.py --region us-west-2 # Deploy to specific region")
    print("   python3 deploy_runtime.py --skip-build       # Skip Docker build (use existing image)")
    print("   python3 deploy_runtime.py --test-only        # Test existing deployment only")
    print("\n📋 Prerequisites:")
    print("   - Docker installed and running")
    print("   - AWS CLI configured with appropriate permissions")
    print("   - AWS credentials configured (via AWS CLI, environment, or IAM role)")
    print("\n🔑 Required AWS Permissions:")
    print("   - ECR: CreateRepository, DescribeRepositories, GetAuthorizationToken")
    print("   - Bedrock AgentCore: CreateAgentRuntime, UpdateAgentRuntime, ListAgentRuntimes")
    print("   - SSM: GetParameter, PutParameter")
    print("   - STS: GetCallerIdentity")

class AgentRuntimeDeployer:
    """Handles deployment of the agent to AgentCore Runtime."""
    
    def __init__(self, region=None):
        # Use provided region or setup from environment/config
        if region is None:
            region = setup_aws_region()
        
        self.region = region
        
        # Initialize AWS clients with explicit region
        try:
            self.ecr_client = boto3.client('ecr', region_name=region)
            self.agentcore_client = boto3.client('bedrock-agentcore-control', region_name=region)
            self.sts_client = boto3.client('sts', region_name=region)
            print(f"✅ AWS clients initialized for region: {region}")
        except Exception as e:
            print(f"❌ Failed to initialize AWS clients: {e}")
            print("💡 Please check your AWS credentials and region configuration")
            raise
        
        # Configuration
        self.repository_name = "vpc-agent-runtime"
        self.agent_runtime_name = "vpc_agent"
        self.image_tag = "latest"
        
        # Get account ID and validate AWS access
        try:
            identity = self.sts_client.get_caller_identity()
            self.account_id = identity['Account']
            print(f"✅ AWS Account ID: {self.account_id}")
            print(f"✅ AWS User/Role: {identity.get('Arn', 'Unknown')}")
        except Exception as e:
            print(f"❌ Failed to get AWS account identity: {e}")
            print("💡 Please check your AWS credentials")
            raise
        
        self.ecr_uri = f"{self.account_id}.dkr.ecr.{self.region}.amazonaws.com/{self.repository_name}"
        print(f"📦 ECR URI: {self.ecr_uri}")
        
    def create_ecr_repository(self):
        """Create ECR repository if it doesn't exist."""
        try:
            print(f"🔍 Checking ECR repository: {self.repository_name}")
            self.ecr_client.describe_repositories(repositoryNames=[self.repository_name])
            print(f"✅ ECR repository {self.repository_name} already exists")
        except self.ecr_client.exceptions.RepositoryNotFoundException:
            print(f"📦 Creating ECR repository: {self.repository_name}")
            self.ecr_client.create_repository(
                repositoryName=self.repository_name,
                imageScanningConfiguration={'scanOnPush': True}
            )
            print(f"✅ ECR repository created: {self.repository_name}")
    
    def build_and_push_image(self):
        """Build and push Docker image to ECR."""
        try:
            print("🔨 Building Docker image...")
            
            # Build the image for ARM64
            build_cmd = [
                "docker", "buildx", "build",
                "--platform", "linux/arm64",
                "-f", "Dockerfile.runtime",
                "-t", f"{self.ecr_uri}:{self.image_tag}",
                "--load",
                "."
            ]
            
            result = subprocess.run(build_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ Docker build failed: {result.stderr}")
                return False
            
            print("✅ Docker image built successfully")
            
            # Login to ECR
            print("🔐 Logging into ECR...")
            login_cmd = [
                "aws", "ecr", "get-login-password",
                "--region", self.region
            ]
            login_result = subprocess.run(login_cmd, capture_output=True, text=True)
            
            if login_result.returncode != 0:
                print(f"❌ ECR login failed: {login_result.stderr}")
                return False
            
            docker_login_cmd = [
                "docker", "login",
                "--username", "AWS",
                "--password-stdin",
                f"{self.account_id}.dkr.ecr.{self.region}.amazonaws.com"
            ]
            
            docker_result = subprocess.run(
                docker_login_cmd, 
                input=login_result.stdout, 
                text=True, 
                capture_output=True
            )
            
            if docker_result.returncode != 0:
                print(f"❌ Docker login failed: {docker_result.stderr}")
                return False
            
            # Push the image
            print("📤 Pushing image to ECR...")
            push_cmd = ["docker", "push", f"{self.ecr_uri}:{self.image_tag}"]
            push_result = subprocess.run(push_cmd, capture_output=True, text=True)
            
            if push_result.returncode != 0:
                print(f"❌ Docker push failed: {push_result.stderr}")
                return False
            
            print("✅ Image pushed to ECR successfully")
            return True
            
        except Exception as e:
            print(f"❌ Build and push failed: {e}")
            return False
    
    def get_execution_role_arn(self):
        """Get or create execution role ARN for AgentCore Runtime."""
        # Try to get from SSM first
        role_arn = get_ssm_parameter("/app/vpcagent/agentcore/execution_role_arn")
        
        if role_arn:
            print(f"✅ Using execution role from SSM: {role_arn}")
            return role_arn
        
        # Default role name pattern
        default_role_name = "AgentRuntimeExecutionRole"
        default_role_arn = f"arn:aws:iam::{self.account_id}:role/{default_role_name}"
        
        print(f"⚠️  No execution role found in SSM parameter: /app/vpcagent/agentcore/execution_role_arn")
        print(f"💡 Please create an IAM role with AgentCore Runtime permissions")
        print(f"   Suggested role name: {default_role_name}")
        print(f"   Required permissions: bedrock:*, logs:*, ecr:GetAuthorizationToken")
        
        # Ask user for role ARN
        role_arn = input(f"Enter execution role ARN (or press Enter for {default_role_arn}): ").strip()
        
        if not role_arn:
            role_arn = default_role_arn
        
        # Save to SSM for future use
        put_ssm_parameter("/app/vpcagent/agentcore/execution_role_arn", role_arn)
        print(f"✅ Saved execution role to SSM: {role_arn}")
        
        return role_arn
    
    def deploy_agent_runtime(self):
        """Deploy the agent to AgentCore Runtime."""
        try:
            print("🚀 Deploying agent to AgentCore Runtime...")
            
            execution_role_arn = self.get_execution_role_arn()
            
            # Check if agent runtime already exists
            # List all runtimes and find by name
            runtimes_response = self.agentcore_client.list_agent_runtimes()
            existing_runtime = None
            for runtime in runtimes_response.get('agentRuntimes', []):
                if runtime.get('agentRuntimeName') == self.agent_runtime_name:
                    existing_runtime = runtime
                    break
            
            if existing_runtime:
                print(f"⚠️  Agent runtime {self.agent_runtime_name} already exists")
                print(f"   Status: {existing_runtime.get('status', 'Unknown')}")
                
                update = input("Do you want to update the existing runtime? (y/N): ").strip().lower()
                if update != 'y':
                    print("❌ Deployment cancelled")
                    return None
                
                # Update existing runtime
                response = self.agentcore_client.update_agent_runtime(
                    agentRuntimeId=existing_runtime['agentRuntimeId'],
                    agentRuntimeArtifact={
                        'containerConfiguration': {
                            'containerUri': f"{self.ecr_uri}:{self.image_tag}"
                        }
                    },
                    roleArn=execution_role_arn,
                    networkConfiguration={"networkMode": "PUBLIC"}
                )
                print("✅ Agent runtime updated successfully")
            else:
                # Create new runtime
                response = self.agentcore_client.create_agent_runtime(
                    agentRuntimeName=self.agent_runtime_name,
                    agentRuntimeArtifact={
                        'containerConfiguration': {
                            'containerUri': f"{self.ecr_uri}:{self.image_tag}"
                        }
                    },
                    networkConfiguration={"networkMode": "PUBLIC"},
                    roleArn=execution_role_arn,
                    description="VPC Agent for AWS infrastructure and DevOps assistance"
                )
                print("✅ Agent runtime created successfully")
            
            agent_runtime_arn = response['agentRuntimeArn']
            
            # Save ARN to SSM
            put_ssm_parameter("/app/vpcagent/agentcore/runtime_arn", agent_runtime_arn)
            
            print(f"🎉 Deployment completed!")
            print(f"   Agent Runtime ARN: {agent_runtime_arn}")
            print(f"   Status: {response.get('status', 'Unknown')}")
            
            return agent_runtime_arn
            
        except Exception as e:
            print(f"❌ Deployment failed: {e}")
            return None
    
    def test_deployment(self, agent_runtime_arn):
        """Test the deployed agent."""
        try:
            print("🧪 Testing deployed agent...")
            
            # Create bedrock-agentcore client for invocation
            agentcore_runtime_client = boto3.client('bedrock-agentcore', region_name=self.region)
            
            # Test payload
            test_payload = {
                "prompt": "Hello! Can you help me with AWS best practices?",
                "session_id": f"test-{int(time.time())}"
            }
            
            # Invoke the agent (session ID must be at least 33 characters)
            session_id = f"test-session-{int(time.time())}-{hash(str(time.time()))}"[:50]
            if len(session_id) < 33:
                session_id = session_id + "0" * (33 - len(session_id))
            
            response = agentcore_runtime_client.invoke_agent_runtime(
                agentRuntimeArn=agent_runtime_arn,
                runtimeSessionId=session_id,
                payload=json.dumps(test_payload).encode('utf-8')
            )
            
            # Parse response
            response_body = response['response'].read()
            response_data = json.loads(response_body)
            
            print("✅ Test successful!")
            print(f"   Response: {response_data.get('message', 'No message')[:100]}...")
            
            return True
            
        except Exception as e:
            print(f"⚠️  Test failed: {e}")
            print("   The agent was deployed but testing failed.")
            print("   This might be due to initialization time or permissions.")
            return False

def main():
    """Main deployment function."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Deploy VPC Agent to Amazon Bedrock AgentCore Runtime')
    parser.add_argument('--region', '-r', 
                       help=f'AWS region for deployment (default: {DEFAULT_REGION})',
                       default=None)
    parser.add_argument('--skip-build', 
                       action='store_true',
                       help='Skip Docker build and push (use existing image)')
    parser.add_argument('--test-only', 
                       action='store_true',
                       help='Only test existing deployment without creating new resources')
    parser.add_argument('--help-extended', 
                       action='store_true',
                       help='Show extended help with examples and prerequisites')
    
    args = parser.parse_args()
    
    # Handle extended help
    if args.help_extended:
        print_usage_help()
        sys.exit(0)
    
    print("🚀 VPC Agent Runtime Deployment")
    print("=" * 50)
    
    # Setup AWS region first
    print("🌍 Setting up AWS configuration...")
    if args.region:
        os.environ['AWS_DEFAULT_REGION'] = args.region
        os.environ['AWS_REGION'] = args.region
        region = args.region
        print(f"🌍 Using specified region: {region}")
    else:
        region = setup_aws_region()
    
    # Check prerequisites
    print("\n🔍 Checking prerequisites...")
    
    # Check Docker
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, check=True, text=True)
        print(f"✅ Docker is available: {result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker is not available. Please install Docker.")
        sys.exit(1)
    
    # Check AWS CLI
    try:
        result = subprocess.run(["aws", "--version"], capture_output=True, check=True, text=True)
        print(f"✅ AWS CLI is available: {result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ AWS CLI is not available. Please install AWS CLI.")
        sys.exit(1)
    
    # Check Docker buildx
    try:
        result = subprocess.run(["docker", "buildx", "version"], capture_output=True, check=True, text=True)
        print(f"✅ Docker buildx is available")
    except subprocess.CalledProcessError:
        print("⚠️  Docker buildx not available. Creating buildx instance...")
        try:
            subprocess.run(["docker", "buildx", "create", "--use"], check=True)
            print("✅ Docker buildx configured")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to configure Docker buildx: {e}")
            sys.exit(1)
    
    # Start deployment with configured region
    print(f"\n🚀 Starting deployment in region: {region}")
    deployer = AgentRuntimeDeployer(region=region)
    
    # Handle test-only mode
    if args.test_only:
        print("🧪 Test-only mode: Testing existing deployment...")
        runtime_arn = get_ssm_parameter("/app/vpcagent/agentcore/runtime_arn")
        if runtime_arn:
            deployer.test_deployment(runtime_arn)
        else:
            print("❌ No existing runtime ARN found in SSM parameters")
            sys.exit(1)
        return
    
    # Step 1: Create ECR repository
    deployer.create_ecr_repository()
    
    # Step 2: Build and push image (unless skipped)
    if not args.skip_build:
        if not deployer.build_and_push_image():
            print("❌ Deployment failed at image build/push step")
            sys.exit(1)
    else:
        print("⏭️  Skipping Docker build and push (using existing image)")
    
    # Step 3: Deploy to AgentCore Runtime
    agent_runtime_arn = deployer.deploy_agent_runtime()
    if not agent_runtime_arn:
        print("❌ Deployment failed at runtime creation step")
        sys.exit(1)
    
    # Step 4: Test deployment
    deployer.test_deployment(agent_runtime_arn)
    
    print("\n🎉 Deployment process completed!")
    print(f"   Your agent is now available at: {agent_runtime_arn}")
    print("   You can invoke it using the AWS SDK or CLI")

if __name__ == "__main__":
    main()