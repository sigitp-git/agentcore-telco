#!/usr/bin/env python3
"""
Script to invoke the deployed EKS Agent in Amazon Bedrock AgentCore Runtime.
"""

import boto3
import json
import os
import time
import uuid
from datetime import datetime
from agent import AgentConfig
from utils import get_ssm_parameter, get_cognito_client_secret

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

# Set default AWS region if not already configured
# The EKS Agent is deployed in us-east-1 region
if not os.environ.get('AWS_DEFAULT_REGION'):
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

class AgentRuntimeInvoker:
    """Invoke the deployed agent runtime."""
    
    def __init__(self, region="us-east-1"):
        self.region = region
        self.client = boto3.client('bedrock-agentcore', region_name=region)
        self.gateway_client = boto3.client('bedrock-agentcore-control', region_name=region)
        
        # Print current model configuration
        current_model = AgentConfig.get_model_id()
        model_name = AgentConfig.list_models().get(AgentConfig.SELECTED_MODEL, "Unknown")
        print(f"🤖 Current Model: {model_name}")
        print(f"📝 Model ID: {current_model}")
        print()
        
        # Display gateway and runtime information
        self.display_infrastructure_info()
    
    def display_infrastructure_info(self):
        """Display gateway ID, runtime ID, and MCP tools information."""
        print("🏗️  EKS Agent Infrastructure Information")
        print("=" * 50)
        
        # Get and display Gateway ID
        try:
            gateway_id = get_ssm_parameter("/app/eksagent/agentcore/gateway_id")
            if gateway_id:
                print(f"🌐 Gateway ID: {gateway_id}")
                
                # Get gateway details
                try:
                    gateway_response = self.gateway_client.get_gateway(gatewayIdentifier=gateway_id)
                    gateway_url = gateway_response.get("gatewayUrl", "Unknown")
                    gateway_name = gateway_response.get("name", "Unknown")
                    gateway_status = gateway_response.get("status", "Unknown")
                    
                    print(f"📛 Gateway Name: {gateway_name}")
                    print(f"🔗 Gateway URL: {gateway_url}")
                    print(f"📊 Gateway Status: {gateway_status}")
                    
                    # Try to get MCP tools from the gateway
                    self.display_mcp_tools_info(gateway_id)
                    
                except Exception as e:
                    print(f"⚠️  Could not retrieve gateway details: {e}")
            else:
                print("❌ Gateway ID not found in SSM")
        except Exception as e:
            print(f"⚠️  Could not retrieve gateway ID: {e}")
        
        # Get and display Runtime ARN
        runtime_arn = self.get_agent_runtime_arn()
        if runtime_arn and "ACCOUNT_ID" not in runtime_arn:
            # Extract runtime ID from ARN
            runtime_id = runtime_arn.split("/")[-1] if "/" in runtime_arn else "Unknown"
            print(f"🚀 Runtime ID: {runtime_id}")
            print(f"📋 Runtime ARN: {runtime_arn}")
        
        print("📋 Summary:")
        print(f"   • Gateway: {'✅ Connected' if gateway_id else '❌ Not configured'}")
        print(f"   • Runtime: {'✅ Available' if runtime_arn and 'ACCOUNT_ID' not in runtime_arn else '❌ Not configured'}")
        print(f"   • MCP Tools: Available via AgentCore Gateway")
        print()
    
    def display_mcp_tools_info(self, gateway_id):
        """Display information about MCP tools available through the gateway."""
        try:
            # Import MCP client components to test gateway connection
            from strands.tools.mcp import MCPClient
            from mcp.client.streamable_http import streamablehttp_client
            
            # Get authentication token
            from agent import get_token
            gateway_access_token = get_token(
                get_ssm_parameter("/app/eksagent/agentcore/machine_client_id"),
                get_cognito_client_secret(),
                get_ssm_parameter("/app/eksagent/agentcore/cognito_auth_scope"),
                get_ssm_parameter("/app/eksagent/agentcore/cognito_token_url")
            )
            
            if 'access_token' in gateway_access_token:
                # Get gateway URL
                gateway_response = self.gateway_client.get_gateway(gatewayIdentifier=gateway_id)
                gateway_url = gateway_response.get("gatewayUrl")
                
                # Create MCP client
                mcp_client = MCPClient(
                    lambda: streamablehttp_client(
                        gateway_url,
                        headers={"Authorization": f"Bearer {gateway_access_token['access_token']}"},
                    )
                )
                
                # Start client and get tools
                mcp_client.start()
                tools = mcp_client.list_tools_sync()
                
                print(f"🔧 AgentCore Gateway MCP Tools:")
                if isinstance(tools, dict) and 'tools' in tools:
                    tools_list = tools['tools']
                elif isinstance(tools, list):
                    tools_list = tools
                else:
                    tools_list = []
                
                if tools_list:
                    print(f"   📊 Total Tools: {len(tools_list)}")
                    for i, tool in enumerate(tools_list, 1):
                        # Try different ways to get tool name and description
                        tool_name = "Unknown Tool"
                        tool_desc = "No description available"
                        
                        # Check if it's an MCP tool object
                        if hasattr(tool, 'name'):
                            tool_name = tool.name
                        elif hasattr(tool, '_name'):
                            tool_name = tool._name
                        elif hasattr(tool, 'tool_name'):
                            tool_name = tool.tool_name
                        
                        # Check for description
                        if hasattr(tool, 'description'):
                            tool_desc = tool.description
                        elif hasattr(tool, '_description'):
                            tool_desc = tool._description
                        elif hasattr(tool, 'tool_description'):
                            tool_desc = tool.tool_description
                        
                        # If it's a dict-like object, try to extract info
                        if hasattr(tool, '__dict__'):
                            tool_dict = tool.__dict__
                            if 'name' in tool_dict:
                                tool_name = tool_dict['name']
                            if 'description' in tool_dict:
                                tool_desc = tool_dict['description']
                        
                        print(f"   {i}. {tool_name}")
                        if tool_desc and tool_desc != 'No description available' and len(tool_desc.strip()) > 0:
                            print(f"      └─ {tool_desc[:80]}{'...' if len(tool_desc) > 80 else ''}")
                else:
                    print("   ❌ No MCP tools found")
                
                # Cleanup
                try:
                    mcp_client.stop(None, None, None)
                except:
                    pass
                    
        except Exception as e:
            print(f"🔧 AgentCore Gateway MCP Tools: ❌ Could not retrieve ({str(e)[:50]}...)")
    
    def get_agent_runtime_arn(self):
        """Get the agent runtime ARN for EKS Agent from environment variable."""
        # Get EKS Agent runtime ARN from environment variable
        arn = os.getenv("EKS_AGENT_RUNTIME_ARN", "arn:aws:bedrock-agentcore:us-east-1:ACCOUNT_ID:runtime/eks_agent-RUNTIME_ID")
        return arn
        
        return arn
    
    def invoke_agent(self, prompt, session_id=None):
        """Invoke the agent with a prompt."""
        try:
            agent_runtime_arn = self.get_agent_runtime_arn()
            if not agent_runtime_arn:
                return None
            
            if not session_id:
                session_id = f"session-{uuid.uuid4()}-{int(time.time())}"
            
            # Prepare payload
            payload = {
                "prompt": prompt,
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            print(f"🚀 Invoking agent...")
            print(f"   Prompt: {prompt}")
            print(f"   Session: {session_id}")
            print(f"   Runtime: {agent_runtime_arn.split('/')[-1] if '/' in agent_runtime_arn else 'Unknown'}")
            
            # Invoke the agent
            response = self.client.invoke_agent_runtime(
                agentRuntimeArn=agent_runtime_arn,
                runtimeSessionId=session_id,
                payload=json.dumps(payload).encode('utf-8'),
                qualifier="DEFAULT"
            )
            
            # Parse response
            response_body = response['response'].read()
            response_data = json.loads(response_body)
            
            print(f"✅ Response received:")
            
            if "error" in response_data:
                print(f"❌ Error: {response_data['error']}")
                return response_data
            
            message = response_data.get('message', 'No message')
            print(f"💬 Message: {message}")
            
            # Show additional info
            if 'tools_used' in response_data:
                print(f"🔧 Tools used: {', '.join(response_data['tools_used'])}")
            
            if 'timestamp' in response_data:
                print(f"⏰ Timestamp: {response_data['timestamp']}")
            
            return response_data
            
        except Exception as e:
            print(f"❌ Invocation failed: {e}")
            return None
    
    def interactive_mode(self):
        """Interactive chat mode with the agent."""
        print("🤖 EKS Agent Interactive Mode")
        print("=" * 40)
        print("Type 'quit' or 'exit' to end the session")
        print("Type 'help' for usage tips")
        print()
        
        session_id = f"interactive-{uuid.uuid4()}-{int(time.time())}"
        
        while True:
            try:
                prompt = input("You: ").strip()
                
                if prompt.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if prompt.lower() == 'help':
                    self.show_help()
                    continue
                
                if not prompt:
                    continue
                
                print()
                response = self.invoke_agent(prompt, session_id)
                print()
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def show_help(self):
        """Show help information."""
        print("""
💡 EKS Agent Help:

Example prompts:
• "How do I create an EKS cluster with best practices?"
• "What are the essential EKS add-ons I should install?"
• "Help me troubleshoot pod scheduling issues in EKS"
• "How do I set up ALB Ingress Controller in EKS?"
• "What's the best way to manage EKS node groups?"

Features:
• Web search for current information
• Memory of conversation context
• EKS and Kubernetes expertise
• Container orchestration guidance

Commands:
• 'quit' or 'exit' - End session
• 'help' - Show this help
        """)
    
    def run_test_scenarios(self):
        """Run predefined test scenarios."""
        test_scenarios = [
            {
                "name": "Basic EKS Question",
                "prompt": "What is Amazon EKS and what are its main benefits?"
            },
            {
                "name": "EKS Best Practices",
                "prompt": "What are the key principles of EKS cluster security?"
            },
            {
                "name": "Web Search Test",
                "prompt": "Search for the latest EKS features and updates"
            },
            {
                "name": "Troubleshooting Help",
                "prompt": "My pods are stuck in pending state. What should I check?"
            }
        ]
        
        print("🧪 Running Test Scenarios")
        print("=" * 30)
        
        session_id = f"test-{uuid.uuid4()}-{int(time.time())}"
        results = []
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n📋 Test {i}: {scenario['name']}")
            print("-" * 40)
            
            response = self.invoke_agent(scenario['prompt'], session_id)
            
            if response and 'error' not in response:
                results.append({"test": scenario['name'], "status": "success"})
                print("✅ Test passed")
            else:
                results.append({"test": scenario['name'], "status": "failed"})
                print("❌ Test failed")
        
        # Summary
        print(f"\n📊 Test Results Summary")
        print("=" * 30)
        successful = sum(1 for r in results if r['status'] == 'success')
        print(f"Passed: {successful}/{len(results)} tests")
        
        for result in results:
            status_icon = "✅" if result['status'] == 'success' else "❌"
            print(f"{status_icon} {result['test']}")

def main():
    """Main function."""
    import sys
    
    invoker = AgentRuntimeInvoker()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'test':
            invoker.run_test_scenarios()
        elif command == 'interactive':
            invoker.interactive_mode()
        elif command == 'invoke':
            if len(sys.argv) > 2:
                prompt = ' '.join(sys.argv[2:])
                invoker.invoke_agent(prompt)
            else:
                print("❌ Please provide a prompt: python invoke_runtime.py invoke 'your prompt here'")
        else:
            print(f"❌ Unknown command: {command}")
            print("Usage: python invoke_runtime.py [test|interactive|invoke 'prompt']")
    else:
        # Default to interactive mode
        invoker.interactive_mode()

if __name__ == "__main__":
    main()