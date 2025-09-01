#!/usr/bin/env python3
"""
Streamlit Frontend for AWS Prometheus Agent
A user-friendly web interface for interacting with the deployed Prometheus Agent.
"""

import streamlit as st
import boto3
import json
import os
import sys
import time
import uuid
from datetime import datetime

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent import AgentConfig
from utils import get_ssm_parameter, get_cognito_client_secret

# Load environment variables from .env.agents file
try:
    from dotenv import load_dotenv
    # Load from parent directory's .env.agents file (two levels up from streamlit/)
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env.agents')
    load_dotenv(env_path)
except ImportError:
    print("⚠️  python-dotenv not installed. Using system environment variables only.")
except Exception as e:
    print(f"⚠️  Could not load .env.agents file: {e}")

# Set default AWS region if not already configured
if not os.environ.get('AWS_DEFAULT_REGION'):
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

class StreamlitAgentInterface:
    """Streamlit interface for the Prometheus Agent."""
    
    def __init__(self):
        self.region = "us-east-1"
        self.client = boto3.client('bedrock-agentcore', region_name=self.region)
        self.gateway_client = boto3.client('bedrock-agentcore-control', region_name=self.region)
        self._mcp_tools_cache = None
        
    def get_agent_runtime_arn(self):
        """Get the agent runtime ARN for Prometheus Agent from environment variable."""
        # Get Prometheus Agent runtime ARN from environment variable
        arn = os.getenv("PROMETHEUS_AGENT_RUNTIME_ARN", "arn:aws:bedrock-agentcore:us-east-1:ACCOUNT_ID:runtime/prometheus_agent-RUNTIME_ID")
        return arn
    
    def get_agent_gateway_id(self):
        """Get the agent gateway ID for Prometheus Agent from SSM parameter."""
        try:
            gateway_id = get_ssm_parameter("/app/prometheusagent/agentcore/gateway_id")
            if gateway_id:
                return gateway_id
        except Exception:
            pass
        
        # Fallback to environment variable
        gateway_id = os.getenv("PROMETHEUS_AGENT_GATEWAY_ID", "prometheus-agent-agentcore-gw-GATEWAY_ID")
        return gateway_id
    
    def get_runtime_info(self):
        """Get formatted runtime and gateway information."""
        runtime_arn = self.get_agent_runtime_arn()
        gateway_id = self.get_agent_gateway_id()
        
        # Extract runtime ID from ARN
        runtime_id = "RUNTIME_ID"
        if "runtime/" in runtime_arn:
            runtime_id = runtime_arn.split("runtime/")[-1]
        
        # Check if using actual values or placeholders
        runtime_status = "✅ Active" if "ACCOUNT_ID" not in runtime_arn else "⚠️ Placeholder"
        gateway_status = "✅ Active" if "GATEWAY_ID" not in gateway_id else "⚠️ Placeholder"
        
        return {
            "runtime_arn": runtime_arn,
            "runtime_id": runtime_id,
            "runtime_status": runtime_status,
            "gateway_id": gateway_id,
            "gateway_status": gateway_status
        }
    
    def get_mcp_tools_info(self):
        """Get information about MCP tools available through the AgentCore Gateway."""
        if self._mcp_tools_cache is not None:
            return self._mcp_tools_cache
        
        try:
            gateway_id = self.get_agent_gateway_id()
            if not gateway_id or "GATEWAY_ID" in gateway_id:
                self._mcp_tools_cache = {"status": "error", "message": "Gateway not configured", "tools": []}
                return self._mcp_tools_cache
            
            # Get gateway details
            gateway_response = self.gateway_client.get_gateway(gatewayIdentifier=gateway_id)
            gateway_url = gateway_response.get("gatewayUrl")
            gateway_status = gateway_response.get("status", "Unknown")
            
            if gateway_status != "READY":
                self._mcp_tools_cache = {"status": "error", "message": f"Gateway not ready: {gateway_status}", "tools": []}
                return self._mcp_tools_cache
            
            # Try to get authentication token and connect to MCP
            from strands.tools.mcp import MCPClient
            from mcp.client.streamable_http import streamablehttp_client
            from agent import get_token
            
            gateway_access_token = get_token(
                get_ssm_parameter("/app/prometheusagent/agentcore/machine_client_id"),
                get_cognito_client_secret(),
                get_ssm_parameter("/app/prometheusagent/agentcore/cognito_auth_scope"),
                get_ssm_parameter("/app/prometheusagent/agentcore/cognito_token_url")
            )
            
            if 'access_token' not in gateway_access_token:
                self._mcp_tools_cache = {"status": "error", "message": "Authentication failed", "tools": []}
                return self._mcp_tools_cache
            
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
            
            # Process tools
            tools_list = []
            if isinstance(tools, dict) and 'tools' in tools:
                raw_tools = tools['tools']
            elif isinstance(tools, list):
                raw_tools = tools
            else:
                raw_tools = []
            

            
            for tool in raw_tools:
                # Use the exact same logic as invoke_runtime.py
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
                
                tool_info = {
                    "name": tool_name,
                    "description": tool_desc if tool_desc != "No description available" else "No description available"
                }
                
                tools_list.append(tool_info)
            
            # Cleanup
            try:
                mcp_client.stop(None, None, None)
            except:
                pass
            
            self._mcp_tools_cache = {
                "status": "success",
                "gateway_url": gateway_url,
                "gateway_status": gateway_status,
                "tools": tools_list,
                "total_tools": len(tools_list)
            }
            
        except Exception as e:
            self._mcp_tools_cache = {
                "status": "error", 
                "message": f"Failed to retrieve MCP tools: {str(e)[:100]}...",
                "tools": []
            }
        
        return self._mcp_tools_cache
    
    def invoke_agent(self, prompt, session_id=None):
        """Invoke the agent with a prompt."""
        try:
            agent_runtime_arn = self.get_agent_runtime_arn()
            if not agent_runtime_arn:
                return None
            
            if not session_id:
                session_id = f"streamlit-{uuid.uuid4()}-{int(time.time())}"
            
            # Prepare payload
            payload = {
                "prompt": prompt,
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Show loading spinner
            with st.spinner('🤖 Prometheus Agent is thinking...'):
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
                
                return response_data
                
        except Exception as e:
            st.error(f"❌ Agent invocation failed: {e}")
            return None

def main():
    """Main Streamlit application."""
    
    # Page configuration
    st.set_page_config(
        page_title="AWS Prometheus Agent",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Display MODEL_ID information
    current_model_id = AgentConfig.get_model_id()
    print(f"🌐 Streamlit App - Backend MODEL_ID: {current_model_id}")
    print(f"📝 Model Description: {AgentConfig.list_models()[AgentConfig.SELECTED_MODEL]}")
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #FF9900;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .user-message {
        background-color: #E3F2FD;
        border-left: 4px solid #2196F3;
    }
    .agent-message {
        background-color: #F3E5F5;
        border-left: 4px solid #9C27B0;
    }
    .sidebar-content {
        background-color: #F5F5F5;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">📊 AWS Prometheus Agent</h1>', unsafe_allow_html=True)
    st.markdown("**Your intelligent monitoring and observability assistant powered by Amazon Bedrock**")
    
    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'session_id' not in st.session_state:
        st.session_state.session_id = f"streamlit-{uuid.uuid4()}-{int(time.time())}"
    if 'agent_interface' not in st.session_state:
        st.session_state.agent_interface = StreamlitAgentInterface()
    
    # Sidebar
    with st.sidebar:
        st.header("🛠️ Agent Controls")
        
        # AgentCore Runtime & Gateway Information
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        st.subheader("🏗️ AgentCore Configuration")
        
        # Get runtime and gateway info
        runtime_info = st.session_state.agent_interface.get_runtime_info()
        
        # Display Runtime Information
        st.markdown("**🚀 Runtime:**")
        st.text(f"Status: {runtime_info['runtime_status']}")
        st.text(f"ID: {runtime_info['runtime_id']}")
        
        # Display Gateway Information  
        st.markdown("**🌐 Gateway:**")
        st.text(f"Status: {runtime_info['gateway_status']}")
        st.text(f"ID: {runtime_info['gateway_id']}")
        
        # Show full ARN in expander for technical details
        with st.expander("🔍 Technical Details"):
            st.code(f"Runtime ARN:\n{runtime_info['runtime_arn']}", language="text")
            st.code(f"Gateway ID:\n{runtime_info['gateway_id']}", language="text")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # MCP Tools Information
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        st.subheader("🔧 AgentCore Gateway MCP Tools")
        
        # Get MCP tools info
        mcp_info = st.session_state.agent_interface.get_mcp_tools_info()
        
        if mcp_info["status"] == "success":
            st.success(f"✅ Connected - {mcp_info['total_tools']} tools available")
            
            # Show tools in an expander
            with st.expander(f"📋 View {mcp_info['total_tools']} MCP Tools"):
                for i, tool in enumerate(mcp_info["tools"], 1):
                    # Make tool names more readable by replacing underscores
                    display_name = tool['name'].replace('___', ' → ').replace('_', ' ').title()
                    st.markdown(f"**{i}. {display_name}**")
                    st.code(tool['name'], language="text")  # Show original name in code block
                    if tool['description'] and tool['description'] != "No description available":
                        st.caption(tool['description'][:150] + ("..." if len(tool['description']) > 150 else ""))
                    if i < len(mcp_info["tools"]):  # Don't add separator after last item
                        st.markdown("---")
            
            # Gateway status
            st.caption(f"Gateway Status: {mcp_info.get('gateway_status', 'Unknown')}")
            
        elif mcp_info["status"] == "error":
            st.error(f"❌ {mcp_info.get('message', 'MCP tools unavailable')}")
            
            # Add refresh button
            if st.button("🔄 Refresh MCP Tools"):
                st.session_state.agent_interface._mcp_tools_cache = None
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Session information
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        st.subheader("📊 Session Info")
        st.text(f"Session ID: {st.session_state.session_id[:20]}...")
        st.text(f"Region: us-east-1")
        st.text(f"Messages: {len(st.session_state.messages)}")
        current_model_id = AgentConfig.get_model_id()
        st.text(f"Model: {current_model_id.split('.')[-1]}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Model selector
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        st.subheader("🤖 Model Selection")
        
        # Initialize model selection in session state
        if 'selected_model_key' not in st.session_state:
            st.session_state.selected_model_key = AgentConfig.SELECTED_MODEL
        
        # Model selector dropdown
        model_options = AgentConfig.list_models()
        selected_model = st.selectbox(
            "Choose Claude Model:",
            options=list(model_options.keys()),
            index=list(model_options.keys()).index(st.session_state.selected_model_key),
            format_func=lambda x: model_options[x],
            key="model_selector"
        )
        
        # Update model if changed
        if selected_model != st.session_state.selected_model_key:
            st.session_state.selected_model_key = selected_model
            AgentConfig.set_model(selected_model)
            st.success(f"✅ Model updated to: {model_options[selected_model]}")
            st.rerun()
        
        # Display current model info
        st.info(f"🔧 Current: {model_options[AgentConfig.SELECTED_MODEL]}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Quick actions
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        st.subheader("⚡ Quick Actions")
        
        if st.button("🔄 New Session"):
            st.session_state.messages = []
            st.session_state.session_id = f"streamlit-{uuid.uuid4()}-{int(time.time())}"
            st.rerun()
        
        if st.button("📋 Clear Chat"):
            st.session_state.messages = []
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Example prompts
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        st.subheader("💡 Example Prompts")
        
        example_prompts = [
            "How do I set up Prometheus monitoring for Kubernetes?",
            "What are the best practices for Prometheus alerting rules?",
            "Help me configure Grafana dashboards for Prometheus metrics",
            "How do I troubleshoot high cardinality metrics in Prometheus?",
            "What's the difference between Prometheus and CloudWatch?",
            "How do I optimize Prometheus storage and retention?"
        ]
        
        for prompt in example_prompts:
            if st.button(f"📝 {prompt[:30]}...", key=f"example_{hash(prompt)}"):
                st.session_state.example_prompt = prompt
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Agent capabilities
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        st.subheader("🎯 Agent Capabilities")
        st.markdown("""
        - **Prometheus Configuration & Setup**
        - **Monitoring Best Practices**
        - **Alerting Rules & Notifications**
        - **Grafana Dashboard Design**
        - **Metrics Collection & Storage**
        - **Performance Optimization**
        - **Troubleshooting & Debugging**
        - **Observability Strategy**
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Main chat interface
    st.header("💬 Chat with Prometheus Agent")
    
    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f'''
            <div class="chat-message user-message">
                <strong>👤 You:</strong><br>
                {message["content"]}
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown(f'''
            <div class="chat-message agent-message">
                <strong>🤖 Prometheus Agent:</strong><br>
                {message["content"]}
            </div>
            ''', unsafe_allow_html=True)
    
    # Handle example prompt selection
    if hasattr(st.session_state, 'example_prompt'):
        user_input = st.session_state.example_prompt
        delattr(st.session_state, 'example_prompt')
    else:
        user_input = None
    
    # Chat input
    if not user_input:
        user_input = st.chat_input("Ask me anything about Prometheus monitoring...")
    
    if user_input:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Display user message immediately
        st.markdown(f'''
        <div class="chat-message user-message">
            <strong>👤 You:</strong><br>
            {user_input}
        </div>
        ''', unsafe_allow_html=True)
        
        # Get agent response
        response = st.session_state.agent_interface.invoke_agent(
            user_input, 
            st.session_state.session_id
        )
        
        if response:
            if "error" in response:
                agent_message = f"❌ Error: {response['error']}"
            else:
                agent_message = response.get('message', 'No response received')
                
                # Show additional info if available
                if 'tools_used' in response and response['tools_used']:
                    agent_message += f"\n\n🔧 **Tools used:** {', '.join(response['tools_used'])}"
                
                if 'timestamp' in response:
                    agent_message += f"\n\n⏰ **Response time:** {response['timestamp']}"
        else:
            agent_message = "❌ Failed to get response from the agent. Please try again."
        
        # Add agent response to chat history
        st.session_state.messages.append({"role": "agent", "content": agent_message})
        
        # Display agent message
        st.markdown(f'''
        <div class="chat-message agent-message">
            <strong>🤖 Prometheus Agent:</strong><br>
            {agent_message}
        </div>
        ''', unsafe_allow_html=True)
        
        # Rerun to update the interface
        st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; margin-top: 2rem;">
        <p>📊 <strong>AWS Prometheus Agent</strong> | Powered by Amazon Bedrock & AgentCore Runtime</p>
        <p>Built with ❤️ using Streamlit | <a href="https://github.com/sigitp-git/aws-devops-strands-agentcore" target="_blank">View on GitHub</a></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()