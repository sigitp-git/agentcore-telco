#!/usr/bin/env python3
"""
Script to invoke the deployed Prometheus Agent in Amazon Bedrock AgentCore Runtime.
"""

import boto3
import json
import os
import time
import uuid
from datetime import datetime
# Removed get_ssm_parameter import - using environment variables
from agent import AgentConfig

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
# The Prometheus Agent is deployed in us-east-1 region
if not os.environ.get('AWS_DEFAULT_REGION'):
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

class AgentRuntimeInvoker:
    """Invoke the deployed agent runtime."""
    
    def __init__(self, region="us-east-1"):
        self.region = region
        self.client = boto3.client('bedrock-agentcore', region_name=region)
        
        # Print current model configuration
        current_model = AgentConfig.get_model_id()
        model_name = AgentConfig.list_models().get(AgentConfig.SELECTED_MODEL, "Unknown")
        print(f"🤖 Current Model: {model_name}")
        print(f"📝 Model ID: {current_model}")
        print()
        
    def get_agent_runtime_arn(self):
        """Get the agent runtime ARN for Prometheus Agent from environment variable."""
        # Get Prometheus Agent runtime ARN from environment variable
        arn = os.getenv("PROMETHEUS_AGENT_RUNTIME_ARN", "arn:aws:bedrock-agentcore:us-east-1:ACCOUNT_ID:runtime/prometheus_agent-RUNTIME_ID")
        print(f"✅ Using Prometheus agent runtime ARN: {arn}")
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
        print("🤖 Prometheus Agent Interactive Mode")
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
💡 Prometheus Agent Help:

Example prompts:
• "How do I set up Prometheus monitoring for Kubernetes?"
• "What are the best practices for Prometheus alerting rules?"
• "Help me configure Grafana dashboards for Prometheus metrics"
• "How do I troubleshoot high cardinality metrics in Prometheus?"
• "What's the difference between Prometheus and CloudWatch?"

Features:
• Web search for current information
• Memory of conversation context
• Prometheus and monitoring expertise
• Observability best practices

Commands:
• 'quit' or 'exit' - End session
• 'help' - Show this help
        """)
    
    def run_test_scenarios(self):
        """Run predefined test scenarios."""
        test_scenarios = [
            {
                "name": "Basic Prometheus Question",
                "prompt": "What is Prometheus and what are its main use cases?"
            },
            {
                "name": "Monitoring Best Practices",
                "prompt": "What are the key principles of effective monitoring with Prometheus?"
            },
            {
                "name": "Web Search Test",
                "prompt": "Search for the latest Prometheus features and updates"
            },
            {
                "name": "Troubleshooting Help",
                "prompt": "My Prometheus server is using too much memory. What should I check?"
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