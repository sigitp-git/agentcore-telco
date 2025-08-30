#!/usr/bin/env python3
"""
Local agent connecting to Amazon Bedrock AgentCore Memory and Gateway
"""

import logging
import os
import uuid
import sys
import json
import requests
import atexit
import signal

# Load environment variables from .env.agents file
try:
    from dotenv import load_dotenv
    # Load from parent directory's .env.agents file
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env.agents')
    load_dotenv(env_path)
except ImportError:
    print("⚠️  python-dotenv not installed. Using system environment variables only.")
except Exception as e:
    print(f"⚠️  Could not load .env.agents file: {e}")

# Import boto libraries and AWS tools
import boto3
from boto3.session import Session
from utils import get_ssm_parameter, put_ssm_parameter, load_api_spec, get_cognito_client_secret

# Import DDGS
from ddgs import DDGS
from ddgs.exceptions import DDGSException, RatelimitException

# Import Strands, BedrockModel, MCP libraries
from strands.agent import Agent
from strands.tools import tool
from strands.hooks import AfterInvocationEvent, HookProvider, HookRegistry, MessageAddedEvent
from strands.models.bedrock import BedrockModel
from strands.tools.mcp import MCPClient
from mcp.client.streamable_http import streamablehttp_client
from mcp.client.stdio import stdio_client, StdioServerParameters
import subprocess
import asyncio

# Import AgentCore Memory
from bedrock_agentcore.memory import MemoryClient
from bedrock_agentcore.memory.constants import StrategyType

# Import AgentCore Identity
from bedrock_agentcore.identity.auth import requires_access_token

# STS client will be initialized after region setup

class AWSMCPManager:
    """Manages AWS MCP tools integration."""
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.mcp_clients = {}
        self.mcp_tools = []
        self._cleanup_registered = False
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.cleanup()
        
    def load_aws_mcp_config(self):
        """Load AWS MCP configuration."""
        try:
            if not os.path.exists(self.config_path):
                print(f"⚠️  AWS MCP config file not found at {self.config_path}")
                return None
                
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                return config.get('mcpServers', {})
                
        except Exception as e:
            print(f"❌ Error loading AWS MCP config: {e}")
            return None
    
    def initialize_aws_mcp_clients(self):
        """Initialize MCP clients for enabled AWS servers with aggressive timeouts."""
        servers = self.load_aws_mcp_config()
        if not servers:
            print("ℹ️  No AWS MCP servers found")
            return
        
        enabled_servers = {name: config for name, config in servers.items() 
                          if not config.get('disabled', False)}
        
        print(f"🔧 Initializing {len(enabled_servers)} AWS MCP servers...")
        
        # Known problematic servers that often hang
        problematic_servers = {
            'awslabs.prometheus-mcp-server',
            'aws-knowledge-mcp-server',
            'awslabs.cloudwatch-mcp-server'
        }
        
        for server_name, server_config in enabled_servers.items():
            try:
                # Use shorter timeout for known problematic servers
                if server_name in problematic_servers:
                    print(f"   ⚠️  {server_name} is known to be slow, using shorter timeout...")
                
                self._initialize_single_mcp_client(server_name, server_config)
            except Exception as e:
                print(f"⚠️  Failed to initialize {server_name}: {e}")
    
    def _initialize_single_mcp_client(self, server_name: str, server_config: dict):
        """Initialize a single MCP client with timeout."""
        command = server_config.get('command', '')
        args = server_config.get('args', [])
        env = server_config.get('env', {})
        
        if not command:
            print(f"⚠️  No command specified for {server_name}")
            return
        
        import threading
        import time
        
        def init_client_worker():
            """Worker function to initialize client."""
            try:
                # Create environment with current env + server env
                full_env = os.environ.copy()
                
                # Ensure AWS region is set for all AWS MCP servers
                if 'aws' in server_name.lower() or any('aws' in arg.lower() for arg in args):
                    full_env.setdefault('AWS_DEFAULT_REGION', os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))
                    full_env.setdefault('AWS_REGION', os.environ.get('AWS_REGION', 'us-east-1'))
                
                # Apply server-specific environment variables
                full_env.update(env)
                
                # Add additional logging suppression for all MCP servers
                full_env.setdefault('PYTHONWARNINGS', 'ignore')
                full_env.setdefault('LOGURU_LEVEL', 'ERROR')
                full_env.setdefault('LOG_LEVEL', 'ERROR')
                
                # Create MCP client using stdio
                server_params = StdioServerParameters(
                    command=command,
                    args=args,
                    env=full_env
                )
                client = MCPClient(
                    lambda: stdio_client(server_params)
                )
                
                print(f"   • Starting {server_name}...")
                
                # Start the client (this can hang)
                client.start()
                
                # Get tools from this client
                tools = self._get_tools_from_client(client, server_name)
                
                self.mcp_clients[server_name] = client
                self.mcp_tools.extend(tools)
                
                print(f"✅ Initialized {server_name} with {len(tools)} tools")
                return True
                
            except Exception as e:
                print(f"⚠️  Failed to start {server_name}: {e}")
                return False
        
        # Use different timeouts based on server type
        problematic_servers = {
            'awslabs.prometheus-mcp-server',
            'aws-knowledge-mcp-server', 
            'awslabs.cloudwatch-mcp-server'
        }
        
        timeout = 2.0 if server_name in problematic_servers else 5.0
        
        # Run initialization with timeout
        init_thread = threading.Thread(target=init_client_worker, daemon=True)
        init_thread.start()
        init_thread.join(timeout=timeout)
        
        if init_thread.is_alive():
            print(f"⚠️  {server_name} initialization timed out after {timeout}s, skipping...")
            return
    
    def _get_tools_from_client(self, client, server_name: str):
        """Get tools from an MCP client."""
        try:
            tools = client.list_tools_sync()
            
            # Handle different response formats
            if isinstance(tools, dict):
                # Check if it's a valid tools response with 'tools' field
                if 'tools' in tools and tools['tools']:
                    tools_list = tools['tools']
                else:
                    print(f"ℹ️  {server_name} returned empty tools dict")
                    return []
            elif isinstance(tools, list):
                tools_list = tools
            elif tools is None:
                print(f"ℹ️  {server_name} returned no tools")
                return []
            else:
                print(f"⚠️  {server_name} returned unexpected format: {type(tools)}")
                return []
            
            # Add server name prefix to tool names for identification
            if tools_list:
                for tool in tools_list:
                    if hasattr(tool, 'name'):
                        tool._original_name = tool.name
                        tool._server_name = server_name
                return tools_list
            return []
            
        except Exception as e:
            # Provide cleaner error messages for common MCP issues
            error_str = str(e).lower()
            if "validation error" in error_str and "tools" in error_str:
                print(f"ℹ️  {server_name}: No tools available")
            elif "connection" in error_str or "timeout" in error_str:
                print(f"ℹ️  {server_name}: Connection unavailable")
            else:
                print(f"ℹ️  {server_name}: Tools unavailable")
            return []
    
    def get_all_aws_tools(self):
        """Get all tools from AWS MCP clients."""
        return self.mcp_tools
    
    def cleanup(self):
        """Cleanup MCP clients and stdio resources with timeout."""
        if self._cleanup_registered:
            return  # Already cleaned up
        
        self._cleanup_registered = True
        print(f"🧹 Cleaning up {len(self.mcp_clients)} MCP clients...")
        
        import time
        import threading
        
        def cleanup_client_with_timeout(server_name, client, timeout=2.0):
            """Cleanup a single client with timeout."""
            def cleanup_worker():
                try:
                    print(f"   • Stopping {server_name}...")
                    
                    # For stdio clients, try to terminate the underlying process first
                    process = None
                    try:
                        if hasattr(client, '_client_session') and hasattr(client._client_session, '_process'):
                            process = client._client_session._process
                        elif hasattr(client, '_session') and hasattr(client._session, '_process'):
                            process = client._session._process
                        elif hasattr(client, '_process'):
                            process = client._process
                        
                        if process and hasattr(process, 'poll') and process.poll() is None:
                            print(f"   🔄 Terminating stdio process for {server_name}...")
                            process.terminate()
                            time.sleep(0.1)  # Very brief wait
                            if process.poll() is None:
                                process.kill()
                            print(f"   ✅ {server_name} stdio process terminated")
                        elif process:
                            print(f"   ℹ️  {server_name} process already terminated")
                    except Exception as process_error:
                        print(f"   ⚠️  Process termination failed for {server_name}: {process_error}")
                    
                    # Try client cleanup methods (but don't wait long)
                    try:
                        if hasattr(client, 'stop'):
                            client.stop(None, None, None)
                        elif hasattr(client, '__exit__'):
                            client.__exit__(None, None, None)
                        elif hasattr(client, 'close'):
                            client.close()
                        print(f"   ✅ {server_name} stopped successfully")
                    except Exception as cleanup_error:
                        print(f"   ⚠️  Client cleanup failed for {server_name}: {cleanup_error}")
                            
                except Exception as e:
                    print(f"   ❌ Complete cleanup failed for {server_name}: {e}")
            
            # Run cleanup in a thread with timeout
            cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
            cleanup_thread.start()
            cleanup_thread.join(timeout=timeout)
            
            if cleanup_thread.is_alive():
                print(f"   ⚠️  {server_name} cleanup timed out after {timeout}s")
                return False
            return True
        
        # Cleanup each client with timeout
        for server_name, client in list(self.mcp_clients.items()):
            cleanup_client_with_timeout(server_name, client)
        
        # Clear the clients dictionary
        self.mcp_clients.clear()
        self.mcp_tools.clear()
        print("✅ MCP cleanup completed")

class AgentConfig:
    """Configuration settings for the EKS Agent."""
    
    # AWS Settings
    DEFAULT_REGION = 'us-east-1'
    
    # MCP Configuration
    ENABLE_MCP_CONFIG = True  # Toggle to enable/disable MCP config loading
    MCP_CONFIG_PATH = '/home/ubuntu/agentcore-telco/awslabs-mcp-lambda/mcp/mcp.json'
    
    # AWS MCP Configuration
    ENABLE_AWS_MCP = True  # Toggle to enable/disable AWS MCP integration
    AWS_MCP_CONFIG_PATH = '/home/ubuntu/agentcore-telco/awslabs-mcp-lambda/mcp/mcp.json'  # Path to AWS MCP config file
    
    # Available Models
    AVAILABLE_MODELS = {
        'claude-sonnet-4': 'us.anthropic.claude-sonnet-4-20250514-v1:0',
        'claude-3-7-sonnet': 'us.anthropic.claude-3-7-sonnet-20250219-v1:0',
        'claude-3-5-sonnet-v2': 'us.anthropic.claude-3-5-sonnet-20241022-v2:0',
        'claude-3-5-sonnet-v1': 'us.anthropic.claude-3-5-sonnet-20240620-v1:0',
        'claude-3-5-haiku': 'us.anthropic.claude-3-5-haiku-20241022-v1:0'
    }
    
    # Default model selection
    SELECTED_MODEL = 'claude-3-5-haiku'
    
    @classmethod
    def get_model_id(cls):
        """Get the currently selected model ID."""
        return cls.AVAILABLE_MODELS.get(cls.SELECTED_MODEL, cls.AVAILABLE_MODELS['claude-3-5-sonnet-v2'])
    
    @classmethod
    def set_model(cls, model_key):
        """Set the model by key."""
        if model_key in cls.AVAILABLE_MODELS:
            cls.SELECTED_MODEL = model_key
            return True
        return False
    
    @classmethod
    def list_models(cls):
        """List available models with descriptions."""
        return {
            'claude-sonnet-4': 'Claude Sonnet 4 (Latest, Most Capable)',
            'claude-3-7-sonnet': 'Claude 3.7 Sonnet (Enhanced Reasoning)',
            'claude-3-5-sonnet-v2': 'Claude 3.5 Sonnet v2 (Balanced Performance)',
            'claude-3-5-sonnet-v1': 'Claude 3.5 Sonnet v1 (Stable)',
            'claude-3-5-haiku': 'Claude 3.5 Haiku (Fast & Efficient)'
        }
    
    # Model Settings
    MODEL_TEMPERATURE = 0.3  # Controls randomness in responses (0.3 is fairly deterministic, good for consistent outputs)
    MAX_TOKENS = 4096        # Model response limit, sufficient for detailed EKS troubleshooting and analysis
    TOP_P = 0.9              # Considering tokens that make up 90% of the probability mass, balances creativity for problem-solving while maintaining technical accuracy
    
    # Memory Settings
    MEMORY_NAME = "EKSAgentMemory"
    SSM_MEMORY_ID_PATH = "/app/eksagent/agentcore/memory_id"
    MEMORY_EXPIRY_DAYS = 90
    CONTEXT_RETRIEVAL_TOP_K = 3
    DEVOPS_USER_ID = "eks_001"
    
    # Search Settings
    SEARCH_REGION = "us-en"
    
    # System Prompt
    EKS_SYSTEM_PROMPT = """You are AWS EKS agent. Help with EKS cluster management, Kubernetes operations, and AWS infrastructure.

CRITICAL TOOL SELECTION RULES:
- Answer from knowledge FIRST before using tools
- Use tools ONLY when you need current/specific data
- MAXIMUM 1 tool call per response
- Keep responses under 300 words
- Be direct and actionable

EXPERTISE AREAS:
- EKS cluster creation, configuration, and management
- Kubernetes workload deployment and troubleshooting
- Node groups, Fargate profiles, and compute management
- EKS networking (VPC, subnets, security groups)
- IAM roles and service accounts (IRSA)
- EKS add-ons (AWS Load Balancer Controller, EBS CSI, etc.)
- Helm charts and Kubernetes manifests
- EKS monitoring and logging (CloudWatch, Prometheus)
- EKS security best practices
- kubectl and eksctl command usage
- Container image management and ECR integration
- EKS cost optimization
- Cluster autoscaling and HPA/VPA
- Service mesh integration (Istio, App Mesh)
- CI/CD pipelines with EKS

RESPONSE GUIDELINES:
- Provide specific kubectl/eksctl commands when applicable
- Include relevant YAML manifests for Kubernetes resources
- Suggest AWS best practices for EKS
- Recommend cost-effective and secure solutions
- Always consider high availability and scalability

NON-FUNCTIONAL RULES:
- Be friendly, patient, and understanding with users
- Always offer additional help after answering questions
- If you can't help with something, direct users to the appropriate contact

"""
    
    @classmethod
    def setup_aws_region(cls):
        """Setup AWS region configuration."""
        # Set environment variables for AWS region
        os.environ['AWS_DEFAULT_REGION'] = cls.DEFAULT_REGION
        os.environ['AWS_REGION'] = cls.DEFAULT_REGION
        
        # Create a new session to ensure region is properly set
        session = Session()
        actual_region = session.region_name or cls.DEFAULT_REGION
        
        # Verify the region is set correctly
        if actual_region != cls.DEFAULT_REGION:
            print(f"⚠️  Region mismatch: expected {cls.DEFAULT_REGION}, got {actual_region}")
            # Force the region in the session
            session = Session(region_name=cls.DEFAULT_REGION)
            actual_region = cls.DEFAULT_REGION
        
        print(f"🌍 AWS region configured: {actual_region}")
        return actual_region
    
    @classmethod
    def load_mcp_config(cls):
        """Load MCP configuration from the specified file path."""
        if not cls.ENABLE_MCP_CONFIG:
            return None
            
        try:
            if not os.path.exists(cls.MCP_CONFIG_PATH):
                print(f"⚠️  MCP config file not found")
                return None
                
            with open(cls.MCP_CONFIG_PATH, 'r') as f:
                mcp_config = json.load(f)
                return mcp_config
                
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in MCP config file: {e}")
            return None
        except Exception as e:
            print(f"❌ Error loading MCP config: {e}")
            return None
    
    @classmethod
    def get_mcp_servers(cls):
        """Get MCP servers configuration."""
        mcp_config = cls.load_mcp_config()
        if mcp_config and 'mcpServers' in mcp_config:
            return mcp_config['mcpServers']
        return {}
    
    @classmethod
    def is_mcp_server_enabled(cls, server_name: str):
        """Check if a specific MCP server is enabled."""
        servers = cls.get_mcp_servers()
        if server_name in servers:
            return not servers[server_name].get('disabled', False)
        return False
    
    @classmethod
    def toggle_mcp_config(cls, enabled: bool = None):
        """Toggle MCP configuration loading on/off."""
        if enabled is None:
            cls.ENABLE_MCP_CONFIG = not cls.ENABLE_MCP_CONFIG
        else:
            cls.ENABLE_MCP_CONFIG = enabled
        
        status = "enabled" if cls.ENABLE_MCP_CONFIG else "disabled"
        return cls.ENABLE_MCP_CONFIG

def select_model_interactive():
    """Interactive model selection for CLI usage."""
    print("\n🤖 Available Claude Models:")
    print("=" * 50)
    
    models = AgentConfig.list_models()
    model_keys = list(models.keys())
    
    for i, (key, description) in enumerate(models.items(), 1):
        current = " (CURRENT)" if key == AgentConfig.SELECTED_MODEL else ""
        print(f"{i}. {description}{current}")
    
    print(f"\n0. Use current selection: {models[AgentConfig.SELECTED_MODEL]}")
    
    try:
        choice = input("\nSelect model (0-5): ").strip()
        
        if choice == '0' or choice == '':
            print(f"✅ Using current model: {models[AgentConfig.SELECTED_MODEL]}")
            return
        
        choice_idx = int(choice) - 1
        if 0 <= choice_idx < len(model_keys):
            selected_key = model_keys[choice_idx]
            AgentConfig.set_model(selected_key)
            print(f"✅ Selected model: {models[selected_key]}")
        else:
            print("❌ Invalid selection. Using current model.")
    except (ValueError, KeyboardInterrupt):
        print(f"✅ Using current model: {models[AgentConfig.SELECTED_MODEL]}")

def handle_command_line_args():
    """Handle command line arguments - only called when running as main script."""
    if len(sys.argv) > 1:
        if sys.argv[1] == '--select-model':
            select_model_interactive()
            sys.exit(0)
        elif sys.argv[1] in ['--help', '-h']:
            print("\n🤖 AWS EKS Agent - Usage")
            print("=" * 40)
            print("python3 agent.py                 # Run agent with current model")
            print("python3 agent.py --select-model  # Interactive model selection")
            print("python3 select_model.py          # Standalone model selector")
            print("\nAvailable Models:")
            for key, desc in AgentConfig.list_models().items():
                current = " (CURRENT)" if key == AgentConfig.SELECTED_MODEL else ""
                print(f"  • {desc}{current}")
            print("\nMCP Configuration Tools:")
            print("  • list_mcp_server_names()       # Quick list of server names")
            print("  • list_mcp_servers_from_config() # Detailed server information")
            print("  • manage_mcp_config()           # Manage MCP configuration")
            print("  • show_available_mcp_servers()  # Show servers with details")
            print()
            sys.exit(0)

# Global variables that will be initialized in main()
REGION = None
sts_client = None
gateway = None
gateway_id = None
mcp_client = None
aws_mcp_manager = None
memory_id = None
memory_client = None

def validate_discovery_url(url):
    """Validate that the discovery URL is accessible and returns valid OIDC configuration."""
    try:
        import requests
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            config = response.json()
            required_fields = ['issuer', 'authorization_endpoint', 'token_endpoint', 'jwks_uri']
            if all(field in config for field in required_fields):
                return True, "Valid OIDC configuration"
            else:
                return False, f"Missing required OIDC fields: {[f for f in required_fields if f not in config]}"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:100]}"
    except Exception as e:
        return False, f"Connection error: {str(e)}"

def validate_gateway_configuration():
    """Validate gateway configuration parameters before creation."""
    required_params = {
        "/app/eksagent/agentcore/machine_client_id": "Machine Client ID",
        "/app/eksagent/agentcore/cognito_discovery_url": "Cognito Discovery URL",
        "/app/eksagent/agentcore/gateway_iam_role": "Gateway IAM Role"
    }
    
    missing_params = []
    invalid_params = []
    
    for param_path, param_name in required_params.items():
        value = get_ssm_parameter(param_path)
        if not value:
            missing_params.append(f"{param_name} ({param_path})")
        elif param_path.endswith("cognito_discovery_url"):
            # Validate discovery URL format and accessibility
            if not value.endswith("/.well-known/openid_configuration"):
                invalid_params.append(f"{param_name}: Must end with '/.well-known/openid_configuration'")
            elif "example.com" in value:
                invalid_params.append(f"{param_name}: Appears to be a placeholder")
            else:
                # Test if the URL is accessible and returns valid OIDC config
                is_valid, message = validate_discovery_url(value)
                if not is_valid:
                    invalid_params.append(f"{param_name}: {message}")
                    print(f"💡 The discovery URL {value} is not accessible or doesn't return valid OIDC configuration")
                    print("   This might be because:")
                    print("   1. Cognito User Pool doesn't have a domain configured")
                    print("   2. The domain is not set up for OIDC discovery")
                    print("   3. You need to use a different OIDC provider")
    
    if missing_params:
        print(f"❌ Missing required SSM parameters: {', '.join(missing_params)}")
        return False
    
    if invalid_params:
        print(f"❌ Invalid SSM parameters:")
        for param in invalid_params:
            print(f"   • {param}")
        return False
    
    return True

def use_manual_gateway(region=None):
    """Use manually created gateway from AWS Management Console."""
    # Get gateway ID from environment variable
    manual_gateway_id = os.getenv("EKS_AGENT_GATEWAY_ID", "eks-agent-agentcore-gw-7uxdeftskt")
    
    print(f"🔍 Using manually created gateway: {manual_gateway_id}")
    
    # Use provided region or fall back to global REGION or default
    if region is None:
        region = globals().get('REGION', 'us-east-1')
    
    gateway_client = boto3.client("bedrock-agentcore-control", region_name=region)
    
    try:
        # Get gateway details
        gateway_response = gateway_client.get_gateway(gatewayIdentifier=manual_gateway_id)
        gateway = {
            "id": manual_gateway_id,
            "name": gateway_response["name"],
            "gateway_url": gateway_response["gatewayUrl"],
            "gateway_arn": gateway_response["gatewayArn"],
        }
        
        # Store gateway ID in SSM for reference
        put_ssm_parameter("/app/eksagent/agentcore/gateway_id", manual_gateway_id)
        
        print(f"✅ Successfully connected to manual gateway: {manual_gateway_id}")
        print(f"   Gateway URL: {gateway['gateway_url']}")
        return gateway, manual_gateway_id
        
    except Exception as e:
        print(f"⚠️  Could not connect to manual gateway {manual_gateway_id}: {e}")
        print("🔄 Continuing without gateway functionality...")
        return None, None

# Commented out automatic gateway creation - using manually created gateway instead
# def create_gateway_if_configured():
#     """Create gateway only if properly configured."""
#     print("🔍 Checking gateway configuration...")
#     
#     if not validate_gateway_configuration():
#         print("🔄 Gateway functionality disabled due to configuration issues")
#         print("💡 The agent will continue to work without gateway functionality")
#         print("   Gateway is only needed for advanced MCP integrations")
#         return None, None
#     
#     gateway_client = boto3.client("bedrock-agentcore-control", region_name=REGION)
#     gateway_name = "eksagent-agentcore-gw"
#     
#     # Get configuration
#     discovery_url = get_ssm_parameter("/app/devopsagent/agentcore/cognito_discovery_url")
#     client_id = get_ssm_parameter("/app/devopsagent/agentcore/machine_client_id")
#     
#     auth_config = {
#         "customJWTAuthorizer": {
#             "allowedClients": [client_id],
#             "discoveryUrl": discovery_url
#         }
#     }
#     
#     try:
#         print(f"✅ Configuration valid - creating gateway in region {REGION}")
#         
#         create_response = gateway_client.create_gateway(
#             name=gateway_name,
#             roleArn=get_ssm_parameter("/app/eksagent/agentcore/gateway_iam_role"),
#             protocolType="MCP",
#             authorizerType="CUSTOM_JWT",
#             authorizerConfiguration=auth_config,
#             description="EKS Agent AgentCore Gateway",
#         )
#         
#         gateway_id = create_response["gatewayId"]
#         gateway = {
#             "id": gateway_id,
#             "name": gateway_name,
#             "gateway_url": create_response["gatewayUrl"],
#             "gateway_arn": create_response["gatewayArn"],
#         }
#         put_ssm_parameter("/app/eksagent/agentcore/gateway_id", gateway_id)
#         print(f"✅ Gateway created successfully with ID: {gateway_id}")
#         return gateway, gateway_id
#         
#     except Exception as e:
#         print(f"⚠️  Gateway creation failed: {e}")
#         return try_existing_gateway(gateway_client)

def try_existing_gateway(gateway_client):
    """Try to use existing gateway if available."""
    existing_gateway_id = get_ssm_parameter("/app/eksagent/agentcore/gateway_id")
    
    if existing_gateway_id:
        print(f"Found existing gateway with ID: {existing_gateway_id}")
        try:
            gateway_response = gateway_client.get_gateway(gatewayIdentifier=existing_gateway_id)
            gateway = {
                "id": existing_gateway_id,
                "name": gateway_response["name"],
                "gateway_url": gateway_response["gatewayUrl"],
                "gateway_arn": gateway_response["gatewayArn"],
            }
            print(f"✅ Using existing gateway: {existing_gateway_id}")
            return gateway, existing_gateway_id
        except Exception as get_error:
            print(f"⚠️  Could not retrieve existing gateway: {get_error}")
    
    print("🔄 Continuing without gateway functionality...")
    return None, None

# Gateway initialization will be done in main()

# Using the AgentCore Gateway for MCP server (only if gateway is available)
def get_token(client_id: str, client_secret: str, scope_string: str = None, url: str = None) -> dict:
    try:
        # Use default values if not provided
        if scope_string is None:
            scope_string = get_ssm_parameter("/app/eksagent/agentcore/cognito_auth_scope") or "openid"
        if url is None:
            url = get_ssm_parameter("/app/eksagent/agentcore/cognito_token_url")
            if not url or "REDACTED_COGNITO_ID" in url:
                # Skip token request if no valid URL is configured
                return {"error": "Cognito token URL not configured. Please set /app/eksagent/agentcore/cognito_token_url SSM parameter."}
            
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": scope_string,

        }
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as err:
        return {"error": str(err)}

# MCP client initialization will be done in main()

# AWS MCP Manager initialization will be done in main()

# Global cleanup state
_cleanup_done = False

# Define cleanup functions
def cleanup_all_resources():
    """Cleanup all MCP resources and connections with timeout."""
    global _cleanup_done
    
    if _cleanup_done:
        return  # Already cleaned up
    
    _cleanup_done = True
    print("\n🧹 Cleaning up resources...")
    
    import threading
    import time
    import os
    
    def cleanup_with_timeout():
        """Perform cleanup operations."""
        try:
            # Cleanup AWS MCP clients
            if aws_mcp_manager:
                print("🔄 Cleaning up AWS MCP clients...")
                aws_mcp_manager.cleanup()
            
            # Cleanup main MCP client (gateway connection)
            if mcp_client:
                try:
                    print("🔄 Cleaning up main MCP client...")
                    if hasattr(mcp_client, 'stop'):
                        mcp_client.stop(None, None, None)
                    elif hasattr(mcp_client, '__exit__'):
                        mcp_client.__exit__(None, None, None)
                    elif hasattr(mcp_client, 'close'):
                        mcp_client.close()
                    print("✅ Main MCP client cleanup completed")
                except Exception as e:
                    print(f"⚠️  Main MCP client cleanup failed: {e}")
        except Exception as e:
            print(f"⚠️  Cleanup error: {e}")
    
    # Run cleanup with timeout to prevent hanging
    cleanup_thread = threading.Thread(target=cleanup_with_timeout, daemon=True)
    cleanup_thread.start()
    cleanup_thread.join(timeout=3.0)  # 3 second timeout
    
    if cleanup_thread.is_alive():
        print("⚠️  Cleanup timed out, forcing exit...")
        # Force exit if cleanup hangs
        os._exit(0)
    else:
        print("✅ All resources cleaned up")

def emergency_cleanup():
    """Emergency cleanup function for unexpected exits."""
    try:
        cleanup_all_resources()
    except:
        pass  # Ignore errors during emergency cleanup

# Note: atexit cleanup removed to prevent double cleanup
# Cleanup is handled by the main() function's finally block

# Configure logging to reduce verbose output
logging.getLogger("strands").setLevel(logging.WARNING)  # Reduce strands logging to prevent duplicate output
logging.getLogger("mcp").setLevel(logging.WARNING)  # Reduce MCP logging
logging.getLogger("httpx").setLevel(logging.WARNING)  # Reduce HTTP request logging
logging.getLogger("awslabs.prometheus_mcp_server").setLevel(logging.WARNING)  # Reduce Prometheus MCP server logging
logging.getLogger("awslabs.cloudwatch_mcp_server").setLevel(logging.WARNING)  # Reduce CloudWatch MCP server logging
logging.getLogger("awslabs.eks_mcp_server").setLevel(logging.WARNING)  # Reduce EKS MCP server logging
logging.getLogger("boto3").setLevel(logging.WARNING)  # Reduce boto3 logging
logging.getLogger("botocore").setLevel(logging.WARNING)  # Reduce botocore logging
logging.getLogger("urllib3").setLevel(logging.WARNING)  # Reduce urllib3 logging

# Set root logger to WARNING to catch any other verbose loggers
logging.getLogger().setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# Define a websearch tool
@tool
def list_mcp_server_names() -> str:
    """Get a quick list of all MCP server names from the configuration file.
    
    Returns:
        Simple list of MCP server names with their status
    """
    if not AgentConfig.ENABLE_MCP_CONFIG:
        return "❌ MCP configuration loading is disabled."
    
    servers = AgentConfig.get_mcp_servers()
    if not servers:
        return "ℹ️  No MCP servers found in configuration file."
    
    enabled_servers = []
    disabled_servers = []
    
    for name, config in servers.items():
        if config.get('disabled', False):
            disabled_servers.append(name)
        else:
            enabled_servers.append(name)
    
    result = f"📋 **MCP Server Names ({len(servers)} total):**\n\n"
    
    if enabled_servers:
        result += f"🟢 **Enabled ({len(enabled_servers)}):**\n"
        for i, name in enumerate(enabled_servers, 1):
            result += f"{i:2d}. {name}\n"
        result += "\n"
    
    if disabled_servers:
        result += f"🔴 **Disabled ({len(disabled_servers)}):**\n"
        for i, name in enumerate(disabled_servers, 1):
            result += f"{i:2d}. {name}\n"
    
    return result

@tool
def manage_mcp_config(action: str = "status", server_name: str = None) -> str:
    """Manage MCP configuration settings.
    
    Args:
        action: Action to perform - 'status', 'enable', 'disable', 'list_servers', 'server_status', 'aws_status'
        server_name: Name of specific MCP server (for server_status action)
        
    Returns:
        Status information or configuration details
    """
    if action == "status":
        status = "enabled" if AgentConfig.ENABLE_MCP_CONFIG else "disabled"
        config_path = AgentConfig.MCP_CONFIG_PATH
        config_exists = os.path.exists(config_path)
        
        result = f"🔧 **MCP Configuration Status:**\n\n"
        result += f"• AgentCore Gateway: {'🟢 Connected' if mcp_client else '🔴 Disconnected'}\n"
        result += f"• AWS MCP Integration: {'🟢 Active' if aws_mcp_manager else '🔴 Inactive'}\n"
        result += f"• Configuration Loading: {status}\n"
        result += f"• Config File Path: {config_path}\n"
        result += f"• Config File Exists: {'✅ Yes' if config_exists else '❌ No'}\n"
        
        if config_exists and AgentConfig.ENABLE_MCP_CONFIG:
            servers = AgentConfig.get_mcp_servers()
            enabled_count = sum(1 for s in servers.values() if not s.get('disabled', False))
            result += f"• Total MCP Servers: {len(servers)}\n"
            result += f"• Enabled Servers: {enabled_count}\n"
        
        if aws_mcp_manager:
            aws_tools_count = len(aws_mcp_manager.get_all_aws_tools())
            result += f"• AWS MCP Tools Available: {aws_tools_count}\n"
        
        return result
    
    elif action == "aws_status":
        if not aws_mcp_manager:
            return "❌ AWS MCP integration is not active"
        
        aws_tools = aws_mcp_manager.get_all_aws_tools()
        active_clients = len(aws_mcp_manager.mcp_clients)
        
        result = f"🔧 **AWS MCP Integration Status:**\n\n"
        result += f"• Status: 🟢 Active\n"
        result += f"• Active Clients: {active_clients}\n"
        result += f"• Available Tools: {len(aws_tools)}\n"
        result += f"• Config Path: {AgentConfig.AWS_MCP_CONFIG_PATH}\n\n"
        
        if active_clients > 0:
            result += "**Active Servers:**\n"
            for server_name in aws_mcp_manager.mcp_clients.keys():
                clean_name = server_name.replace('awslabs.', '').replace('-mcp-server', '')
                server_tools = [t for t in aws_tools if getattr(t, '_server_name', '') == server_name]
                result += f"• {clean_name}: {len(server_tools)} tools\n"
        
        return result
    
    elif action == "enable":
        AgentConfig.toggle_mcp_config(True)
        return "✅ MCP configuration loading enabled"
    
    elif action == "disable":
        AgentConfig.toggle_mcp_config(False)
        return "❌ MCP configuration loading disabled"
    
    elif action == "list_servers":
        if not AgentConfig.ENABLE_MCP_CONFIG:
            return "❌ MCP configuration loading is disabled. Enable it first with action='enable'"
        
        servers = AgentConfig.get_mcp_servers()
        if not servers:
            return "ℹ️  No MCP servers found in configuration"
        
        result = f"🔧 **MCP Servers ({len(servers)} total):**\n\n"
        for name, config in servers.items():
            status = "🟢 Enabled" if not config.get('disabled', False) else "🔴 Disabled"
            command = config.get('command', 'Unknown')
            args = config.get('args', [])
            result += f"• **{name}**: {status}\n"
            result += f"  Command: {command} {' '.join(args)}\n\n"
        
        return result
    
    elif action == "server_status":
        if not server_name:
            return "❌ server_name parameter required for server_status action"
        
        if not AgentConfig.ENABLE_MCP_CONFIG:
            return "❌ MCP configuration loading is disabled"
        
        servers = AgentConfig.get_mcp_servers()
        if server_name not in servers:
            return f"❌ Server '{server_name}' not found in configuration"
        
        server_config = servers[server_name]
        enabled = not server_config.get('disabled', False)
        
        result = f"🔧 **MCP Server: {server_name}**\n\n"
        result += f"• Status: {'🟢 Enabled' if enabled else '🔴 Disabled'}\n"
        result += f"• Command: {server_config.get('command', 'Unknown')}\n"
        result += f"• Args: {' '.join(server_config.get('args', []))}\n"
        
        env_vars = server_config.get('env', {})
        if env_vars:
            result += f"• Environment Variables:\n"
            for key, value in env_vars.items():
                result += f"  - {key}: {value}\n"
        
        auto_approve = server_config.get('autoApprove', [])
        if auto_approve:
            result += f"• Auto-approved Tools: {', '.join(auto_approve)}\n"
        
        return result
    
    else:
        return f"❌ Unknown action: {action}. Available actions: status, enable, disable, list_servers, server_status, aws_status"

@tool
def list_mcp_tools() -> str:
    """List all available AgentCore Gateway MCP tools and their descriptions.
    
    Returns:
        Formatted list of AgentCore Gateway MCP tools with descriptions
    """
    if not mcp_client:
        return "❌ AgentCore Gateway MCP client is not available. No gateway MCP tools are currently accessible."
    
    try:
        mcp_tools = get_full_tools_list(mcp_client)
        
        if not mcp_tools:
            return "ℹ️  No AgentCore Gateway MCP tools are currently available."
        
        result = f"🔧 **Available AgentCore Gateway MCP Tools ({len(mcp_tools)} total):**\n\n"
        
        for i, tool in enumerate(mcp_tools, 1):
            tool_name = getattr(tool, 'name', 'Unknown')
            tool_description = getattr(tool, 'description', 'No description available')
            
            # Try to get input schema if available
            input_schema = getattr(tool, 'inputSchema', None)
            parameters = ""
            if input_schema and hasattr(input_schema, 'properties'):
                param_names = list(input_schema.properties.keys()) if input_schema.properties else []
                if param_names:
                    parameters = f" (Parameters: {', '.join(param_names)})"
            
            result += f"{i}. **{tool_name}**{parameters}\n"
            result += f"   {tool_description}\n\n"
        
        result += "💡 These tools are available through the AgentCore Gateway integration."
        return result
        
    except Exception as e:
        return f"❌ Error retrieving AgentCore Gateway MCP tools: {str(e)}"

@tool
def list_aws_mcp_tools() -> str:
    """List all available AWS MCP tools and their descriptions.
    
    Returns:
        Formatted list of AWS MCP tools with descriptions
    """
    if not aws_mcp_manager:
        return "❌ AWS MCP manager is not available. No AWS MCP tools are currently accessible."
    
    try:
        aws_tools = aws_mcp_manager.get_all_aws_tools()
        
        if not aws_tools:
            return "ℹ️  No AWS MCP tools are currently available."
        
        result = f"🔧 **Available AWS MCP Tools ({len(aws_tools)} total):**\n\n"
        
        # Group tools by server
        tools_by_server = {}
        for tool in aws_tools:
            server_name = getattr(tool, '_server_name', 'Unknown')
            if server_name not in tools_by_server:
                tools_by_server[server_name] = []
            tools_by_server[server_name].append(tool)
        
        for server_name, tools in tools_by_server.items():
            clean_server_name = server_name.replace('awslabs.', '').replace('-mcp-server', '')
            result += f"**{clean_server_name.upper()} ({len(tools)} tools):**\n"
            
            for i, tool in enumerate(tools, 1):
                tool_name = getattr(tool, 'name', 'Unknown')
                tool_description = getattr(tool, 'description', 'No description available')
                
                # Truncate long descriptions
                if len(tool_description) > 100:
                    tool_description = tool_description[:97] + "..."
                
                result += f"{i:2d}. {tool_name}\n"
                result += f"    {tool_description}\n"
            
            result += "\n"
        
        result += "💡 These tools are available through AWS MCP integration and provide direct access to AWS services."
        return result
        
    except Exception as e:
        return f"❌ Error retrieving AWS MCP tools: {str(e)}"

@tool
def list_mcp_servers_from_config() -> str:
    """List all MCP servers loaded from the configuration file with their details.
    
    Returns:
        Comprehensive list of all MCP servers from the config file
    """
    if not AgentConfig.ENABLE_MCP_CONFIG:
        return "❌ MCP configuration loading is disabled. Use manage_mcp_config(action='enable') to enable it."
    
    servers = AgentConfig.get_mcp_servers()
    if not servers:
        return "ℹ️  No MCP servers found in configuration file."
    
    result = f"📋 **All MCP Servers from Configuration ({len(servers)} total):**\n\n"
    
    enabled_count = 0
    disabled_count = 0
    
    for name, config in servers.items():
        is_enabled = not config.get('disabled', False)
        status_icon = "🟢" if is_enabled else "🔴"
        status_text = "Enabled" if is_enabled else "Disabled"
        
        if is_enabled:
            enabled_count += 1
        else:
            disabled_count += 1
        
        result += f"{status_icon} **{name}** ({status_text})\n"
        result += f"   Command: `{config.get('command', 'Unknown')}`\n"
        
        args = config.get('args', [])
        if args:
            args_str = ' '.join(args)
            # Truncate very long args for readability
            if len(args_str) > 80:
                args_str = args_str[:77] + "..."
            result += f"   Args: {args_str}\n"
        
        env_vars = config.get('env', {})
        if env_vars:
            env_list = [f"{k}={v}" for k, v in env_vars.items()]
            env_str = ', '.join(env_list)
            if len(env_str) > 60:
                env_str = env_str[:57] + "..."
            result += f"   Environment: {env_str}\n"
        
        auto_approve = config.get('autoApprove', [])
        if auto_approve:
            auto_str = ', '.join(auto_approve[:3])
            if len(auto_approve) > 3:
                auto_str += f" (+{len(auto_approve)-3} more)"
            result += f"   Auto-approved: {auto_str}\n"
        
        result += "\n"
    
    # Summary
    result += f"📊 **Summary:**\n"
    result += f"• Total Servers: {len(servers)}\n"
    result += f"• Enabled: {enabled_count}\n"
    result += f"• Disabled: {disabled_count}\n"
    
    return result

@tool
def show_available_mcp_servers() -> str:
    """Show all MCP servers available from the loaded configuration file.
    
    Returns:
        Detailed list of MCP servers from the configuration file
    """
    if not AgentConfig.ENABLE_MCP_CONFIG:
        return "❌ MCP configuration loading is disabled. Use manage_mcp_config(action='enable') to enable it."
    
    servers = AgentConfig.get_mcp_servers()
    if not servers:
        return "ℹ️  No MCP servers found in configuration file."
    
    result = f"🔧 **MCP Servers from Configuration File ({len(servers)} total):**\n\n"
    result += f"📁 **Config Path:** {AgentConfig.MCP_CONFIG_PATH}\n\n"
    
    enabled_servers = []
    disabled_servers = []
    
    for name, config in servers.items():
        server_info = {
            'name': name,
            'command': config.get('command', 'Unknown'),
            'args': config.get('args', []),
            'env': config.get('env', {}),
            'disabled': config.get('disabled', False),
            'autoApprove': config.get('autoApprove', [])
        }
        
        if server_info['disabled']:
            disabled_servers.append(server_info)
        else:
            enabled_servers.append(server_info)
    
    # Show enabled servers first
    if enabled_servers:
        result += f"🟢 **Enabled Servers ({len(enabled_servers)}):**\n\n"
        for server in enabled_servers:
            result += f"• **{server['name']}**\n"
            result += f"  Command: `{server['command']} {' '.join(server['args'])}`\n"
            
            if server['env']:
                env_summary = ', '.join([f"{k}={v}" for k, v in list(server['env'].items())[:2]])
                if len(server['env']) > 2:
                    env_summary += f" (+{len(server['env'])-2} more)"
                result += f"  Environment: {env_summary}\n"
            
            if server['autoApprove']:
                auto_approve_summary = ', '.join(server['autoApprove'][:3])
                if len(server['autoApprove']) > 3:
                    auto_approve_summary += f" (+{len(server['autoApprove'])-3} more)"
                result += f"  Auto-approved: {auto_approve_summary}\n"
            
            result += "\n"
    
    # Show disabled servers
    if disabled_servers:
        result += f"🔴 **Disabled Servers ({len(disabled_servers)}):**\n\n"
        for server in disabled_servers:
            result += f"• **{server['name']}** (disabled)\n"
            result += f"  Command: `{server['command']} {' '.join(server['args'])}`\n\n"
    
    result += f"💡 Use `manage_mcp_config(action='server_status', server_name='<name>')` for detailed server info."
    return result

@tool
def list_eks_clusters() -> str:
    """List all EKS clusters in the current AWS account and region.
    
    Returns:
        str: A formatted list of EKS clusters with their status and versions
    """
    try:
        import boto3
        
        # Use the configured region
        eks_client = boto3.client('eks', region_name=REGION)
        
        # List clusters
        response = eks_client.list_clusters()
        clusters = response.get('clusters', [])
        
        if not clusters:
            return "No EKS clusters found in the current region."
        
        result = f"Found {len(clusters)} EKS clusters in region {REGION}:\n\n"
        
        # Get details for each cluster
        for cluster_name in clusters:
            try:
                cluster_info = eks_client.describe_cluster(name=cluster_name)
                cluster = cluster_info['cluster']
                
                status = cluster.get('status', 'Unknown')
                version = cluster.get('version', 'Unknown')
                created = cluster.get('createdAt', 'Unknown')
                endpoint = cluster.get('endpoint', 'N/A')
                
                result += f"• {cluster_name}\n"
                result += f"  Status: {status}\n"
                result += f"  Version: {version}\n"
                result += f"  Created: {created}\n"
                result += f"  Endpoint: {endpoint}\n\n"
                
            except Exception as e:
                result += f"• {cluster_name}\n"
                result += f"  Error getting details: {str(e)}\n\n"
        
        return result
        
    except Exception as e:
        logger.error(f"Error listing EKS clusters: {e}")
        return f"Error listing EKS clusters: {str(e)}"

@tool
def aws_resource_guidance() -> str:
    """Get guidance on which tools to use for different AWS resource operations.
    
    This tool provides guidance on choosing the correct MCP tools for AWS operations.
    Use this when you need to understand which tool to use for specific AWS tasks.
    
    Returns:
        str: Detailed guidance on AWS tool usage
    """
    guidance = """🔧 **AWS Resource Tool Usage Guide**

**For EKS Cluster Operations:**

1. **List EKS Clusters** (AWS Account Level):
   ✅ USE: `list_eks_clusters()` - Lists all EKS clusters in your account
   ✅ USE: `list_resources` (CCAPI) with resource_type="AWS::EKS::Cluster"
   ❌ DON'T USE: `list_k8s_resources` (EKS MCP) - This is for resources WITHIN clusters

2. **Manage Kubernetes Resources** (Within a Cluster):
   ✅ USE: `list_k8s_resources` (EKS MCP) - Lists pods, services, etc. within a specific cluster
   ✅ USE: `get_k8s_events` (EKS MCP) - Gets events for specific resources
   ✅ USE: `get_pod_logs` (EKS MCP) - Gets logs from pods

**For Other AWS Resources:**

3. **List AWS Resources** (Account Level):
   ✅ USE: `list_resources` (CCAPI) - Lists any AWS resource type (S3, RDS, etc.)
   ✅ USE: `get_resource` (CCAPI) - Gets details of specific resources

4. **CloudWatch Operations:**
   ✅ USE: CloudWatch MCP tools for metrics, logs, and alarms

**Key Rule:**
- EKS MCP tools work WITHIN clusters (need cluster_name parameter)
- CCAPI/Core MCP tools work at AWS account level (list clusters, buckets, etc.)
"""
    return guidance

@tool
def eks_tool_guidance() -> str:
    """Get specific guidance for EKS-related operations and tool selection.
    
    Use this tool when you need to understand which EKS tools to use for specific tasks.
    
    Returns:
        str: Detailed EKS tool usage guidance
    """
    guidance = """🚀 **EKS Tool Selection Guide**

**IMPORTANT: Choose the RIGHT tool for your EKS task!**

**❓ User asks: "List all my EKS clusters"**
✅ CORRECT: Use `list_eks_clusters()` or `list_resources` with resource_type="AWS::EKS::Cluster"
❌ WRONG: Don't use `list_k8s_resources` - this needs a cluster name!

**❓ User asks: "List pods in my cluster"**
✅ CORRECT: Use `list_k8s_resources` with cluster_name="your-cluster" and kind="Pod"
❌ WRONG: Don't use `list_eks_clusters()` - this only lists clusters, not pods

**❓ User asks: "Show me cluster details"**
✅ CORRECT: Use `get_resource` with resource_type="AWS::EKS::Cluster" and identifier="cluster-name"
✅ ALSO CORRECT: Use `list_eks_clusters()` for basic info

**❓ User asks: "Get pod logs"**
✅ CORRECT: Use `get_pod_logs` with cluster_name, namespace, and pod_name

**Tool Categories:**
1. **Cluster Management** (AWS Level): list_eks_clusters, get_resource, create_resource
2. **Kubernetes Resources** (Within Cluster): list_k8s_resources, get_k8s_events, get_pod_logs
3. **Monitoring** (CloudWatch): get_cloudwatch_logs, get_cloudwatch_metrics

**Remember:** EKS clusters are AWS resources. Pods/Services are Kubernetes resources within clusters.
"""
    return guidance

@tool
def websearch(
    keywords: str, region: str = AgentConfig.SEARCH_REGION, max_results: int | None = None
) -> str:
    """Search the web to get updated information using DuckDuckGo.
    
    Args:
        keywords: The search query keywords
        region: The search region (wt-wt, us-en, uk-en, ru-ru, etc.)
        max_results: The maximum number of results to return
        
    Returns:
        Search results as formatted string or error message
    """
    if not keywords or not keywords.strip():
        return "Error: Search keywords cannot be empty."
    
    try:
        logger.info(f"Performing web search for: '{keywords}' in region: {region}")
        results = DDGS().text(keywords, region=region, max_results=max_results)
        
        if not results:
            logger.warning(f"No search results found for: {keywords}")
            return "No results found."
        
        logger.info(f"Found {len(results)} search results")
        return _format_search_results(results)
        
    except RatelimitException:
        logger.warning("DuckDuckGo rate limit exceeded")
        return "Rate limit exceeded. Please try again after a short delay."
    except DDGSException as e:
        logger.error(f"DuckDuckGo search error: {e}")
        return f"Search service error: {e}"
    except Exception as e:
        logger.error(f"Unexpected error during web search: {e}")
        return f"Search failed: {e}"

def _format_search_results(results: list) -> str:
    """Format search results for better readability."""
    if not results:
        return "No results found."
    
    formatted = []
    for i, result in enumerate(results, 1):
        title = result.get('title', 'No title')
        body = result.get('body', 'No description')
        href = result.get('href', 'No URL')
        
        formatted.append(f"{i}. **{title}**\n   {body}\n   URL: {href}\n")
    
    return "\n".join(formatted)


# Create a Bedrock model instance with temperature control
# Model and memory initialization will be done in main()



class MemoryManager:
    """Manages AgentCore Memory resource lifecycle."""
    
    def __init__(self, client: MemoryClient, memory_name: str):
        self.client = client
        self.memory_name = memory_name
        
    def get_or_create_memory(self) -> str | None:
        """Get existing memory or create new one."""
        logger.info("Attempting to retrieve or create AgentCore Memory resource...")
        
        # Try SSM first, then search, then create
        memory_id = self._get_memory_from_ssm()
        if memory_id:
            logger.info("Using memory ID from SSM")
            return memory_id
            
        memory_id = self._find_existing_memory()
        if memory_id:
            logger.info("Using found existing memory")
            return memory_id
            
        logger.info("No existing memory found, attempting to create new one")
        return self._create_new_memory()
    
    def _get_memory_from_ssm(self) -> str | None:
        """Retrieve and verify memory ID from SSM."""
        try:
            memory_id = get_ssm_parameter(AgentConfig.SSM_MEMORY_ID_PATH)
            if memory_id:
                logger.info(f"Found memory ID in SSM: {memory_id}")
                # Verify the memory exists
                try:
                    self.client.gmcp_client.get_memory(memoryId=memory_id)
                    logger.info("Memory verified successfully")
                    return memory_id
                except Exception as verify_error:
                    logger.warning(f"Memory ID from SSM is invalid: {verify_error}")
        except Exception as e:
            logger.warning(f"Could not retrieve memory ID from SSM: {e}")
        return None
    
    def _find_existing_memory(self) -> str | None:
        """Search for existing memory by name or pattern."""
        try:
            logger.info("Searching for existing memory...")
            memories = self.client.gmcp_client.list_memories()
            logger.info(f"Found {len(memories.get('memories', []))} total memories")
            
            for memory in memories.get('memories', []):
                memory_id = memory.get('id')
                memory_name_from_api = memory.get('name')
                memory_status = memory.get('status')
                
                logger.debug(f"Memory ID: {memory_id}, Name: {memory_name_from_api}, Status: {memory_status}")
                
                if memory_status == 'DELETING':
                    continue
                
                # Check by name or ID pattern
                if (memory_name_from_api == self.memory_name or 
                    (memory_name_from_api is None and self.memory_name in memory_id and memory_status == 'ACTIVE')):
                    logger.info(f"Found existing memory: {memory_id}")
                    self._save_memory_id_to_ssm(memory_id)
                    return memory_id
            
            logger.info("No existing memory found")
        except Exception as e:
            logger.error(f"Could not list existing memories: {e}")
        return None
    
    def _create_new_memory(self) -> str | None:
        """Create a new memory resource."""
        try:
            logger.info("Creating new AgentCore Memory resource...")
            strategies = self._create_memory_strategies()
            
            logger.info("Creating AgentCore Memory resources. This can take a couple of minutes...")
            response = self.client.create_memory_and_wait(
                name=self.memory_name,
                description="EKS Agent memory",
                strategies=strategies,
                event_expiry_days=AgentConfig.MEMORY_EXPIRY_DAYS,
            )
            memory_id = response["id"]
            logger.info(f"Successfully created memory: {memory_id}")
            
            self._save_memory_id_to_ssm(memory_id)
            return memory_id
        except Exception as e:
            error_str = str(e)
            # Check if memory already exists
            if "already exists" in error_str.lower() or "validation" in error_str.lower():
                logger.info(f"Memory with name '{self.memory_name}' already exists, attempting to find it...")
                # Try to find the existing memory again with more thorough search
                return self._find_existing_memory_by_name()
            else:
                logger.error(f"Failed to create memory: {e}")
                return None
    
    def _create_memory_strategies(self) -> list:
        """Create memory strategies configuration."""
        return [
            {
                StrategyType.USER_PREFERENCE.value: {
                    "name": "DevOpsPreferences",
                    "description": "Captures DevOps preferences and behavior",
                    "namespaces": ["agent/devops/{actorId}/preferences"],
                }
            },
            {
                StrategyType.SEMANTIC.value: {
                    "name": "DevOpsAgentSemantic",
                    "description": "Stores facts from conversations",
                    "namespaces": ["agent/devops/{actorId}/semantic"],
                }
            },
        ]
    
    def _find_existing_memory_by_name(self) -> str | None:
        """Find existing memory by exact name match."""
        try:
            logger.info(f"Searching for existing memory with name: {self.memory_name}")
            memories = self.client.gmcp_client.list_memories()
            
            for memory in memories.get('memories', []):
                memory_id = memory.get('id')
                memory_name_from_api = memory.get('name')
                memory_status = memory.get('status')
                
                logger.debug(f"Checking memory - ID: {memory_id}, Name: {memory_name_from_api}, Status: {memory_status}")
                
                # Skip memories that are being deleted
                if memory_status == 'DELETING':
                    continue
                
                # Exact name match
                if memory_name_from_api == self.memory_name:
                    logger.info(f"Found existing memory by name: {memory_id}")
                    self._save_memory_id_to_ssm(memory_id)
                    return memory_id
            
            logger.warning(f"No existing memory found with name: {self.memory_name}")
            return None
        except Exception as e:
            logger.error(f"Error searching for existing memory: {e}")
            return None

    def _save_memory_id_to_ssm(self, memory_id: str) -> None:
        """Save memory ID to SSM Parameter Store."""
        try:
            put_ssm_parameter(AgentConfig.SSM_MEMORY_ID_PATH, memory_id)
            logger.info("Saved memory ID to SSM")
        except Exception as e:
            logger.warning(f"Could not save memory ID to SSM: {e}")

def create_or_get_memory_resource():
    """Factory function for memory resource creation."""
    memory_manager = MemoryManager(memory_client, AgentConfig.MEMORY_NAME)
    return memory_manager.get_or_create_memory()

def initialize_memory() -> str | None:
    """Initialize memory with proper error handling."""
    try:
        memory_id = create_or_get_memory_resource()
        if memory_id:
            logger.info(f"AgentCore Memory ready with ID: {memory_id}")
            return memory_id
        else:
            _log_memory_initialization_error()
            return None
    except Exception as e:
        logger.error(f"Unexpected error during memory initialization: {e}")
        _log_memory_initialization_error()
        return None

def _log_memory_initialization_error():
    """Log memory initialization error with helpful information."""
    error_messages = [
        "Failed to create or retrieve memory resource",
        "Possible causes:",
        "1. AWS credentials not configured or insufficient permissions",
        "2. AgentCore Memory service not available in your region",
        "3. Network connectivity issues",
        "4. SSM parameter store access issues",
        "The agent will continue without memory functionality..."
    ]
    for msg in error_messages:
        logger.warning(msg)

# Memory ID initialization will be done in main()

class EKSAgentMemoryHooks(HookProvider):
    """Memory hooks for EKS Agent"""

    def __init__(
        self, memory_id: str, client: MemoryClient, actor_id: str, session_id: str
    ):
        self.memory_id = memory_id
        self.client = client
        self.actor_id = actor_id
        self.session_id = session_id
        self.namespaces = {
            i["type"]: i["namespaces"][0]
            for i in self.client.get_memory_strategies(self.memory_id)
        }

    def retrieve_eks_context(self, event: MessageAddedEvent):
        """Retrieve EKS context before processing query"""
        messages = event.agent.messages
        if (
            messages[-1]["role"] == "user"
            and "toolResult" not in messages[-1]["content"][0]
        ):
            user_query = messages[-1]["content"][0]["text"]

            try:
                all_context = []

                for context_type, namespace in self.namespaces.items():
                    # *** AGENTCORE MEMORY USAGE *** - Retrieve EKS context from each namespace
                    memories = self.client.retrieve_memories(
                        memory_id=self.memory_id,
                        namespace=namespace.format(actorId=self.actor_id),
                        query=user_query,
                        top_k=AgentConfig.CONTEXT_RETRIEVAL_TOP_K,
                    )
                    # Post-processing: Format memories into context strings
                    for memory in memories:
                        if isinstance(memory, dict):
                            content = memory.get("content", {})
                            if isinstance(content, dict):
                                text = content.get("text", "").strip()
                                if text:
                                    all_context.append(
                                        f"[{context_type.upper()}] {text}"
                                    )

                # Inject EKS context into the query
                if all_context:
                    context_text = "\n".join(all_context)
                    original_text = messages[-1]["content"][0]["text"]
                    messages[-1]["content"][0][
                        "text"
                    ] = f"EKS Context:\n{context_text}\n\n{original_text}"
                    logger.info(f"Retrieved {len(all_context)} EKS context items")

            except Exception as e:
                logger.error(f"Failed to retrieve EKS context: {e}")

    def save_eks_interaction(self, event: AfterInvocationEvent):
        """Save EKS Agent interaction after agent response"""
        try:
            messages = event.agent.messages
            if len(messages) >= 2 and messages[-1]["role"] == "agent":
                # Get last user query and agent response
                user_query = None
                agent_response = None

                for msg in reversed(messages):
                    if msg["role"] == "agent" and not agent_response:
                        agent_response = msg["content"][0]["text"]
                    elif (
                        msg["role"] == "user"
                        and not user_query
                        and "toolResult" not in msg["content"][0]
                    ):
                        user_query = msg["content"][0]["text"]
                        break

                if user_query and agent_response:
                    # *** AGENTCORE MEMORY USAGE *** - Save the DevOps interaction
                    # Note: AgentCore Memory requires "ASSISTANT" role, not "AGENT"
                    self.client.create_event(
                        memory_id=self.memory_id,
                        actor_id=self.actor_id,
                        session_id=self.session_id,
                        messages=[
                            (user_query, "USER"),
                            (agent_response, "ASSISTANT"),
                        ],
                    )
                    logger.info("Saved DevOps interaction to memory")

        except Exception as e:
            logger.error(f"Failed to save DevOps interaction: {e}")

    def register_hooks(self, registry: HookRegistry) -> None:
        """Register EKS Agent memory hooks"""
        registry.add_callback(MessageAddedEvent, self.retrieve_eks_context)
        registry.add_callback(AfterInvocationEvent, self.save_eks_interaction)
        logger.info("EKS Agent memory hooks registered")

SESSION_ID = str(uuid.uuid4())

def create_agent_hooks(memory_id: str | None) -> list:
    """Create agent hooks based on memory availability."""
    if not memory_id:
        logger.info("Running without memory functionality")
        return []
    
    session_id = str(uuid.uuid4())
    memory_hooks = EKSAgentMemoryHooks(
        memory_id, memory_client, AgentConfig.DEVOPS_USER_ID, session_id
    )
    logger.info("Memory hooks enabled")
    return [memory_hooks]

def get_full_tools_list(client):
    """
    List tools w/ support for pagination
    """
    try:
        more_tools = True
        tools = []
        pagination_token = None
        max_iterations = 10  # Prevent infinite loops
        iteration = 0
        
        while more_tools and iteration < max_iterations:
            iteration += 1
            print(f"🔍 Fetching MCP tools (iteration {iteration})...")
            
            tmp_tools = client.list_tools_sync(pagination_token=pagination_token)
            
            if hasattr(tmp_tools, '__iter__'):
                # If tmp_tools is a list/iterable of tools
                tools.extend(tmp_tools)
                more_tools = False  # Assume no pagination if we get a simple list
            elif hasattr(tmp_tools, 'tools'):
                # If tmp_tools has a tools attribute
                tools.extend(tmp_tools.tools)
                if hasattr(tmp_tools, 'pagination_token') and tmp_tools.pagination_token:
                    pagination_token = tmp_tools.pagination_token
                else:
                    more_tools = False
            else:
                # Fallback - treat as single tool or list
                if tmp_tools:
                    tools.extend([tmp_tools] if not hasattr(tmp_tools, '__iter__') else tmp_tools)
                more_tools = False
                
        print(f"✅ Retrieved {len(tools)} MCP tools total")
        return tools
        
    except Exception as e:
        # Fallback to simple list_tools_sync
        try:
            simple_tools = client.list_tools_sync()
            
            # Handle different response formats
            if isinstance(simple_tools, dict):
                if 'tools' in simple_tools and simple_tools['tools']:
                    return simple_tools['tools']
                else:
                    print("ℹ️  MCP client returned empty tools dict - no tools available")
                    return []
            elif isinstance(simple_tools, list):
                return simple_tools
            elif simple_tools is None:
                print("ℹ️  MCP client returned None - no tools available")
                return []
            else:
                return [simple_tools] if simple_tools else []
                
        except Exception as fallback_error:
            # Check for common MCP errors and provide cleaner messages
            error_str = str(fallback_error).lower()
            if "validation error" in error_str and "tools" in error_str:
                print("ℹ️  No MCP tools available")
            elif "connection" in error_str or "timeout" in error_str:
                print("ℹ️  MCP server connection unavailable")
            else:
                print("ℹ️  MCP tools unavailable")
            return []

def create_tools_list():
    """Create the list of tools for the agent."""
    tools_list = [
        websearch, 
        list_mcp_tools, 
        list_aws_mcp_tools,
        list_mcp_server_names,
        manage_mcp_config,
        list_mcp_servers_from_config,
        show_available_mcp_servers,
        list_eks_clusters,
        aws_resource_guidance,
        eks_tool_guidance
    ]
    
    # Add AgentCore Gateway MCP tools if available
    if mcp_client:
        try:
            mcp_tools = get_full_tools_list(mcp_client)
            tools_list.extend(mcp_tools)
            print(f"✅ Added {len(mcp_tools)} AgentCore Gateway MCP tools")
        except Exception as e:
            # Check for common MCP errors and provide cleaner messages
            error_str = str(e).lower()
            if "validation error" in error_str and "tools" in error_str:
                print("ℹ️  No MCP tools available")
            elif "connection" in error_str or "timeout" in error_str:
                print("ℹ️  MCP server connection unavailable")
            else:
                print("ℹ️  MCP tools unavailable")
    
    # Add AWS MCP tools if available
    if aws_mcp_manager:
        try:
            aws_tools = aws_mcp_manager.get_all_aws_tools()
            tools_list.extend(aws_tools)
            print(f"✅ Added {len(aws_tools)} AWS MCP tools")
        except Exception as e:
            # Check for common MCP errors and provide cleaner messages
            error_str = str(e).lower()
            if "validation error" in error_str and "tools" in error_str:
                print("ℹ️  No AWS MCP tools available")
            elif "connection" in error_str or "timeout" in error_str:
                print("ℹ️  AWS MCP server connection unavailable")
            else:
                print("ℹ️  AWS MCP tools unavailable")
    
    return tools_list

def create_devops_agent(model_id: str) -> Agent:
    """Create and configure the EKS agent."""
    hooks = create_agent_hooks(memory_id)
    
    # Create model with the provided model_id
    model = BedrockModel(
        model_id=model_id, 
        temperature=AgentConfig.MODEL_TEMPERATURE,
        max_tokens=AgentConfig.MAX_TOKENS,
        top_p=AgentConfig.TOP_P
    )
    
    return Agent(
        model=model,
        hooks=hooks,
        system_prompt="""You are AWS EKS agent. Help with EKS cluster management, Kubernetes operations, and AWS infrastructure.

CRITICAL TOOL SELECTION RULES:
- For "list EKS clusters": Use `list_eks_clusters()` or `list_resources` with resource_type="AWS::EKS::Cluster"
- For "list pods/services/etc": Use `list_k8s_resources` with cluster_name (requires specific cluster)
- For AWS account resources: Use CCAPI tools (list_resources, get_resource)
- For Kubernetes resources within clusters: Use EKS MCP tools (list_k8s_resources, get_pod_logs)
- NEVER use `list_k8s_resources` without a valid cluster_name parameter
- If unsure about tool selection, use `aws_resource_guidance()` or `eks_tool_guidance()`

CRITICAL EFFICIENCY RULES:
- Answer from knowledge FIRST before using tools
- Use tools ONLY when you need current/specific data
- MAXIMUM 1 tool call per response
- Keep responses under 300 words
- Be direct and actionable

NON-FUNCTIONAL RULES:
- Be friendly, patient, and understanding with users
- Always offer additional help after answering questions
- If you can't help with something, direct users to the appropriate contact
""",
        tools=create_tools_list(),
    )

class ConversationManager:
    """Manages the interactive conversation loop."""
    
    def __init__(self, agent: Agent, bot_name: str = "AWS-EKS-agent"):
        self.agent = agent
        self.bot_name = bot_name
        self.exit_commands = {'exit', 'quit', 'bye'}
    
    def _list_all_mcp_tools(self) -> str:
        """List all MCP tools loaded from the configuration file."""
        if not AgentConfig.ENABLE_MCP_CONFIG:
            return "❌ MCP configuration disabled"
        
        servers = AgentConfig.get_mcp_servers()
        if not servers:
            return "ℹ️  No MCP servers found"
        
        enabled_servers = []
        disabled_servers = []
        
        for name, config in servers.items():
            # Extract clean server name
            clean_name = name.replace('awslabs.', '').replace('-mcp-server', '').replace('-mcp', '')
            
            if config.get('disabled', False):
                disabled_servers.append(clean_name)
            else:
                enabled_servers.append(clean_name)
        
        result = f"🔧 **MCP Tools ({len(enabled_servers)} enabled):**\n"
        
        # Show enabled servers in a compact list
        for i, name in enumerate(enabled_servers, 1):
            result += f"{i:2d}. {name}\n"
        
        if disabled_servers:
            result += f"\n🔴 **Disabled ({len(disabled_servers)}):** {', '.join(disabled_servers)}"
        
        return result
    
    def _show_help(self) -> str:
        """Show available commands and help information."""
        help_text = "🔧 **Available Commands:**\n\n"
        help_text += "**Special Commands:**\n"
        help_text += "• `/tool` or `/tools` - List all MCP tools from configuration\n"
        help_text += "• `/help` or `/h` - Show this help message\n"
        help_text += "• `exit`, `quit`, `bye` - Exit the agent\n\n"
        
        help_text += "**MCP Management Tools:**\n"
        help_text += "• `list_mcp_server_names()` - Quick list of server names\n"
        help_text += "• `list_mcp_servers_from_config()` - Detailed server info\n"
        help_text += "• `manage_mcp_config()` - Manage MCP configuration\n"
        help_text += "• `show_available_mcp_servers()` - Show servers with details\n\n"
        
        help_text += "**MCP Tools:**\n"
        help_text += "• `list_mcp_tools()` - List AgentCore Gateway MCP tools\n"
        help_text += "• `list_aws_mcp_tools()` - List AWS MCP tools (AWS services)\n\n"
        
        help_text += "**Other Tools:**\n"
        help_text += "• `websearch()` - Search the web for information\n\n"
        
        help_text += "💡 **Tips:**\n"
        help_text += f"• AgentCore Gateway: {'🟢 Connected' if mcp_client else '🔴 Disconnected'}\n"
        help_text += f"• AWS MCP Integration: {'🟢 Enabled' if aws_mcp_manager else '🔴 Disabled'}\n"
        help_text += f"• Available MCP Servers: {len(AgentConfig.get_mcp_servers())}\n"
        help_text += "• Ask me anything about EKS, Kubernetes, or AWS!"
        
        return help_text
    
    def start_conversation(self):
        """Start the interactive conversation loop."""
        print(f"\n🚀 {self.bot_name}: Ask me about EKS on AWS! Type 'exit' to quit.")
        print(f"💡 Special commands: /tool or /tools (list MCP tools), /help (show commands)\n")
        
        try:
            while True:
                try:
                    user_input = input("\nYou > ").strip()
                    
                    if user_input.lower() in self.exit_commands:
                        print("👋 Goodbye!")
                        # Cleanup will be handled by the main function's finally block
                        return  # Return instead of break to exit the function
                        
                    if not user_input:
                        print(f"\n{self.bot_name} > Please ask me something about EKS on AWS!")
                        continue
                    
                    # Handle special commands
                    if user_input.lower() in ["/tool", "/tools"]:
                        tool_list = self._list_all_mcp_tools()
                        print(f"\n{self.bot_name} > {tool_list}")
                        continue
                    elif user_input.lower() in ["/help", "/h"]:
                        help_text = self._show_help()
                        print(f"\n{self.bot_name} > {help_text}")
                        continue
                    
                    response = self.agent(user_input)
                    # strands handles the response automatically, no need to print manually
                    
                except KeyboardInterrupt:
                    print("\n\n👋 Goodbye!")
                    # Cleanup will be handled by the main function's finally block
                    return  # Return instead of break to exit the function
                except Exception as e:
                    logger.error(f"Error processing user input: {e}")
                    print(f"\n{self.bot_name} > Sorry, I encountered an error: {e}")
                    
        except Exception as e:
            logger.error(f"Fatal error in conversation loop: {e}")
            print(f"Fatal error: {e}")
            # Cleanup will be handled by the main function's finally block

def setup_gateway_parameters():
    """Interactive setup for gateway SSM parameters."""
    print("\n🔧 Gateway Configuration Setup")
    print("=" * 50)
    print(f"ℹ️  Using manually created gateway: {os.getenv('EKS_AGENT_GATEWAY_ID', 'eks-agent-agentcore-gw-7uxdeftskt')}")
    print("   Gateway was created via AWS Management Console")
    
    # Check current gateway status
    manual_gateway_id = os.getenv("EKS_AGENT_GATEWAY_ID", "eks-agent-agentcore-gw-7uxdeftskt")
    gateway_client = boto3.client("bedrock-agentcore-control", region_name=REGION)
    
    try:
        gateway_response = gateway_client.get_gateway(gatewayIdentifier=manual_gateway_id)
        print(f"\n✅ Manual Gateway Status:")
        print(f"   Gateway ID: {manual_gateway_id}")
        print(f"   Name: {gateway_response['name']}")
        print(f"   Status: {gateway_response.get('status', 'ACTIVE')}")
        print(f"   URL: {gateway_response['gatewayUrl']}")
    except Exception as e:
        print(f"\n⚠️  Could not retrieve manual gateway details: {e}")
    
    # Check current parameters
    params_to_check = {
        "/app/eksagent/agentcore/machine_client_id": "Cognito Machine Client ID",
        "/app/eksagent/agentcore/cognito_discovery_url": "OIDC Discovery URL",
        "/app/eksagent/agentcore/gateway_iam_role": "Gateway IAM Role ARN",
        "/app/eksagent/agentcore/gateway_id": "Gateway ID (Auto-managed)"
    }
    
    for param_path, description in params_to_check.items():
        current_value = get_ssm_parameter(param_path)
        print(f"\n{description}:")
        print(f"  Parameter: {param_path}")
        print(f"  Current value: {current_value or 'NOT SET'}")
        
        if param_path.endswith("cognito_discovery_url") and current_value:
            if "example.com" in current_value:
                print("  ❌ This appears to be a placeholder value")
            else:
                # Test the URL
                is_valid, message = validate_discovery_url(current_value)
                if is_valid:
                    print("  ✅ URL is accessible and returns valid OIDC configuration")
                else:
                    print(f"  ❌ URL validation failed: {message}")
    
    print(f"\n💡 Manual Gateway Benefits:")
    print(f"   • Gateway created successfully via AWS Management Console")
    print(f"   • Bypasses automatic creation validation issues")
    print(f"   • Enables advanced MCP (Model Context Protocol) integrations")
    
    print(f"\n🚀 Agent Status:")
    print(f"   The agent works with full functionality including gateway support!")



def initialize_agent():
    """Initialize all agent components."""
    global REGION, sts_client, gateway, gateway_id, mcp_client, aws_mcp_manager, memory_id, memory_client
    
    # Initialize configuration
    REGION = AgentConfig.setup_aws_region()
    
    # Initialize AWS clients with proper region
    sts_client = boto3.client('sts', region_name=REGION)
    
    # Initialize MCP configuration
    print(f"🔧 MCP Configuration: {'enabled' if AgentConfig.ENABLE_MCP_CONFIG else 'disabled'}")
    
    if AgentConfig.ENABLE_MCP_CONFIG:
        mcp_servers = AgentConfig.get_mcp_servers()
        if mcp_servers:
            enabled_servers = [name for name, config in mcp_servers.items() if not config.get('disabled', False)]
            print(f"   • {len(enabled_servers)} MCP servers available")
        else:
            print(f"   • No MCP servers found")
    
    # Initialize gateway - using manually created gateway
    gateway, gateway_id = use_manual_gateway(REGION)
    
    # Initialize MCP client only if gateway is available
    mcp_client = None
    if gateway and gateway_id:
        try:
            print(f"🔗 Setting up MCP client for gateway: {gateway_id}")
            
            gateway_access_token = get_token(
                get_ssm_parameter("/app/eksagent/agentcore/machine_client_id"),
                get_cognito_client_secret(),
                get_ssm_parameter("/app/eksagent/agentcore/cognito_auth_scope"),
                get_ssm_parameter("/app/eksagent/agentcore/cognito_token_url")
            )
            
            print(f"🔍 Debug - Token response: {gateway_access_token}")
            
            # Check if we got a valid token
            if 'error' in gateway_access_token:
                print(f"❌ Token error: {gateway_access_token['error']}")
                raise Exception(f"Failed to get access token: {gateway_access_token['error']}")
            
            if 'access_token' not in gateway_access_token:
                print(f"❌ No access_token in response. Available keys: {list(gateway_access_token.keys())}")
                raise Exception("No access_token in authentication response")

            print(f"Gateway Endpoint - MCP URL: {gateway['gateway_url']}")

            # Set up MCP client
            mcp_client = MCPClient(
                lambda: streamablehttp_client(
                    gateway['gateway_url'],
                    headers={"Authorization": f"Bearer {gateway_access_token['access_token']}"},
                )
            )
            print("✅ MCP client configured successfully")
            
        except Exception as e:
            print(f"⚠️  MCP client setup failed: {e}")
            print("🔄 Continuing without MCP client functionality...")
            mcp_client = None
    else:
        print("ℹ️  No gateway available - MCP client functionality disabled")

    # Initialize MCP client if available
    if mcp_client:
        try:
            mcp_client.start()
            print("✅ MCP client started successfully")
        except Exception as e:
            print(f"⚠️  MCP client start failed: {str(e)}")
            print("🔄 Continuing without MCP client functionality...")
            mcp_client = None

    # Initialize AWS MCP Manager with timeout
    aws_mcp_manager = None
    if AgentConfig.ENABLE_AWS_MCP:
        import threading
        import time
        
        def init_aws_mcp():
            """Initialize AWS MCP Manager."""
            global aws_mcp_manager
            try:
                print("🔧 Initializing AWS MCP integration...")
                
                # Verify AWS region is properly configured before MCP initialization
                current_region = os.environ.get('AWS_DEFAULT_REGION', 'not-set')
                print(f"   • AWS region: {current_region}")
                
                # Verify AWS credentials are available
                try:
                    session = Session()
                    credentials = session.get_credentials()
                    if credentials is None:
                        raise Exception("No AWS credentials found")
                    print(f"   • AWS credentials: ✅ Available")
                except Exception as cred_error:
                    print(f"   • AWS credentials: ❌ {cred_error}")
                    raise Exception(f"AWS credentials not available: {cred_error}")
                
                aws_mcp_manager = AWSMCPManager(AgentConfig.AWS_MCP_CONFIG_PATH)
                aws_mcp_manager.initialize_aws_mcp_clients()
                aws_tools_count = len(aws_mcp_manager.get_all_aws_tools())
                print(f"✅ AWS MCP integration ready with {aws_tools_count} tools")
            except Exception as e:
                print(f"⚠️  AWS MCP initialization failed: {e}")
                print("🔄 Continuing without AWS MCP functionality...")
                aws_mcp_manager = None
        
        # Run AWS MCP initialization with timeout
        init_thread = threading.Thread(target=init_aws_mcp, daemon=True)
        init_thread.start()
        init_thread.join(timeout=15.0)  # 15 second timeout
        
        if init_thread.is_alive():
            print("⚠️  AWS MCP initialization timed out after 15s, continuing without it...")
            aws_mcp_manager = None
    else:
        print("ℹ️  AWS MCP integration disabled")
    
    # Initialize model
    current_model_id = AgentConfig.get_model_id()
    print(f"🤖 Using MODEL_ID: {current_model_id}")
    print(f"📝 Model Description: {AgentConfig.list_models()[AgentConfig.SELECTED_MODEL]}")
    
    # Initialize memory
    global memory_client, memory_id
    memory_client = MemoryClient(region_name=REGION)
    memory_id = initialize_memory()
    
    return current_model_id

def initialize_runtime_components():
    """Initialize components needed for runtime without starting interactive mode."""
    global REGION, sts_client, gateway, gateway_url, gateway_id, mcp_client, aws_mcp_manager, memory_id, memory_client, model
    
    # Setup AWS region
    REGION = AgentConfig.setup_aws_region()
    
    # Initialize STS client
    sts_client = boto3.client('sts', region_name=REGION)
    
    # Setup gateway and MCP (will be disabled by runtime config)
    gateway, gateway_url, gateway_id, mcp_client, aws_mcp_manager = setup_gateway_and_mcp()
    
    # Setup memory
    memory_id, memory_client = setup_memory()
    
    # Initialize model
    model_id = AgentConfig.get_model_id()
    model = BedrockModel(
        model_id=model_id, 
        temperature=AgentConfig.MODEL_TEMPERATURE,
        max_tokens=AgentConfig.MAX_TOKENS,
        top_p=AgentConfig.TOP_P
    )
    
    return model, memory_id, memory_client, mcp_client

def setup_gateway_and_mcp():
    """Setup gateway and MCP client for runtime use."""
    global gateway, gateway_url, gateway_id, mcp_client, aws_mcp_manager
    
    # Initialize gateway - using manually created gateway
    gateway, gateway_id = use_manual_gateway(REGION)
    
    # Set gateway_url from gateway dict
    gateway_url = gateway['gateway_url'] if gateway else None
    
    # Initialize MCP client only if gateway is available
    mcp_client = None
    aws_mcp_manager = None
    
    if gateway and gateway_id:
        try:
            print(f"🔗 Setting up MCP client for gateway: {gateway_id}")
            
            gateway_access_token = get_token(
                get_ssm_parameter("/app/eksagent/agentcore/machine_client_id"),
                get_cognito_client_secret(),
                get_ssm_parameter("/app/eksagent/agentcore/cognito_auth_scope"),
                get_ssm_parameter("/app/eksagent/agentcore/cognito_token_url")
            )
            
            print(f"🔍 Debug - Token response: {gateway_access_token}")
            
            # Check if we got a valid token
            if 'error' in gateway_access_token:
                print(f"❌ Token error: {gateway_access_token['error']}")
                raise Exception(f"Failed to get access token: {gateway_access_token['error']}")
            
            if 'access_token' not in gateway_access_token:
                print(f"❌ No access_token in response. Available keys: {list(gateway_access_token.keys())}")
                raise Exception("No access_token in authentication response")

            print(f"Gateway Endpoint - MCP URL: {gateway['gateway_url']}")

            # Set up MCP client
            mcp_client = MCPClient(
                lambda: streamablehttp_client(
                    gateway['gateway_url'],
                    headers={"Authorization": f"Bearer {gateway_access_token['access_token']}"},
                )
            )
            print("✅ MCP client configured successfully")
            
            # Initialize AWS MCP Manager
            aws_mcp_manager = AWSMCPManager(mcp_client)
            
        except Exception as e:
            print(f"⚠️  MCP client setup failed: {e}")
            print("🔄 Continuing without MCP client functionality...")
            mcp_client = None
            aws_mcp_manager = None
    else:
        print("ℹ️  No gateway available - MCP client functionality disabled")

    # Initialize MCP client if available
    if mcp_client:
        try:
            mcp_client.start()
            print("✅ MCP client started successfully")
        except Exception as e:
            print(f"⚠️  MCP client start failed: {str(e)}")
            mcp_client = None
            aws_mcp_manager = None
    
    return gateway, gateway_url, gateway_id, mcp_client, aws_mcp_manager

def setup_memory():
    """Setup memory client and initialize memory."""
    global memory_client, memory_id
    memory_client = MemoryClient(region_name=REGION)
    memory_id = initialize_memory()
    return memory_id, memory_client

def main():
    """Main execution function."""
    import sys
    import signal
    
    # Handle command line arguments first
    handle_command_line_args()
    
    # Register signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
        cleanup_all_resources()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Check for setup command
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        setup_gateway_parameters()
        return
    
    try:
        # Initialize all components
        current_model_id = initialize_agent()
        
        # Create agent with initialized components
        agent = create_devops_agent(current_model_id)
        conversation_manager = ConversationManager(agent)
        conversation_manager.start_conversation()
        
        # If we reach here, user exited normally
        print("🔄 Normal exit, cleaning up...")
        
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
    finally:
        # Only cleanup if not already done by signal handler
        if not _cleanup_done:
            cleanup_all_resources()
        
        # Force exit to prevent hanging
        import os
        os._exit(0)

if __name__ == "__main__":
    main()