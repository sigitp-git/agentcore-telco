#!/usr/bin/env python3
"""
Amazon Bedrock AgentCore Runtime version of the VPC Agent.
This version wraps the existing agent for deployment to Amazon Bedrock AgentCore Runtime.
"""

import logging
import os
import json
from typing import Dict, Any
from datetime import datetime

# Import the BedrockAgentCoreApp wrapper
from bedrock_agentcore.runtime import BedrockAgentCoreApp

# Configure MCP settings before importing agent components
# Disable MCP configuration for runtime to avoid initialization issues

# Import and configure AgentConfig first
from agent import AgentConfig

# Disable AWS_MCP but enable AgentCore Gateway MCP configuration for runtime environment
AgentConfig.ENABLE_MCP_CONFIG = True
AgentConfig.ENABLE_AWS_MCP = False

# Import agent module and initialization functions
import agent
from agent import (
    create_agent_hooks, create_tools_list, AgentConfig
)
from strands.agent import Agent

# Configure logging for runtime
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Log MCP configuration status
logger.info(f"Runtime MCP Configuration - ENABLE_MCP_CONFIG: {AgentConfig.ENABLE_MCP_CONFIG}")
logger.info(f"Runtime MCP Configuration - ENABLE_AWS_MCP: {AgentConfig.ENABLE_AWS_MCP}")

# Initialize the BedrockAgentCoreApp
app = BedrockAgentCoreApp()

# Create the agent instance with all existing functionality
def create_runtime_agent():
    """Create the runtime agent with memory and tools."""
    try:
        # Initialize runtime components
        model, memory_id, memory_client, mcp_client = agent.initialize_runtime_components()
        
        # Create hooks (memory functionality)
        hooks = create_agent_hooks(memory_id)
        
        # Create tools list (websearch, MCP tools, etc.)
        tools = create_tools_list()
        
        # Create agent with existing configuration
        runtime_agent = Agent(
            model=model,
            tools=tools,
            hooks=hooks,
            system_prompt=AgentConfig.VPC_SYSTEM_PROMPT
        )
        
        logger.info("Runtime agent created successfully")
        logger.info(f"Memory enabled: {memory_id is not None}")
        logger.info(f"MCP client enabled: {mcp_client is not None}")
        logger.info(f"Tools available: {len(tools)}")
        logger.info(f"MCP Configuration disabled for runtime: ENABLE_MCP_CONFIG={AgentConfig.ENABLE_MCP_CONFIG}, ENABLE_AWS_MCP={AgentConfig.ENABLE_AWS_MCP}")
        
        # Log available tool names for debugging
        tool_names = [getattr(tool, 'name', str(tool)) for tool in tools]
        logger.info(f"Available tools: {tool_names}")
        
        return runtime_agent
        
    except Exception as e:
        logger.error(f"Failed to create runtime agent: {e}")
        raise

# Create the agent instance
try:
    runtime_agent = create_runtime_agent()
    logger.info("✅ Runtime agent initialization completed")
except Exception as e:
    logger.error(f"❌ Runtime agent initialization failed: {e}")
    runtime_agent = None

@app.entrypoint
def invoke(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    AgentCore Runtime entrypoint for processing user requests.
    
    Args:
        payload: JSON payload containing the user prompt and optional parameters
        
    Returns:
        JSON response with the agent's response
    """
    try:
        logger.info(f"Received payload: {payload}")
        
        # Check if agent is available
        if runtime_agent is None:
            return {
                "error": "Agent not initialized properly",
                "timestamp": datetime.utcnow().isoformat(),
                "status": "error"
            }
        
        # Extract user message from payload
        user_message = payload.get("prompt", "")
        session_id = payload.get("session_id", "runtime-session")
        
        if not user_message:
            error_response = {
                "error": "No prompt found in input. Please provide a 'prompt' key in the payload.",
                "timestamp": datetime.utcnow().isoformat(),
                "status": "error"
            }
            logger.warning(f"Empty prompt, returning: {error_response}")
            return error_response
        
        logger.info(f"Processing request: {user_message[:100]}...")
        
        # Process the message with the memory-enabled runtime agent
        try:
            response = runtime_agent(user_message)
            logger.info(f"Agent response type: {type(response)}")
            logger.info(f"Agent response: {str(response)[:200]}...")
        except Exception as agent_error:
            logger.error(f"Agent processing error: {agent_error}", exc_info=True)
            return {
                "error": f"Agent processing failed: {str(agent_error)}",
                "timestamp": datetime.utcnow().isoformat(),
                "status": "error"
            }
        
        # Format the response
        try:
            # Extract the message text from the AgentResult
            message_text = ""
            if hasattr(response, 'message'):
                if isinstance(response.message, dict):
                    # Handle dictionary format
                    if 'content' in response.message and isinstance(response.message['content'], list):
                        # Extract text from content list
                        for content_item in response.message['content']:
                            if isinstance(content_item, dict) and 'text' in content_item:
                                message_text += content_item['text']
                    else:
                        message_text = str(response.message)
                elif hasattr(response.message, 'content') and isinstance(response.message.content, list):
                    # Handle object format with content list
                    for content_item in response.message.content:
                        if isinstance(content_item, dict) and 'text' in content_item:
                            message_text += content_item['text']
                else:
                    message_text = str(response.message)
            else:
                message_text = str(response)
            
            # Fallback if we couldn't extract text
            if not message_text:
                message_text = str(response)
            
            result = {
                "message": message_text,
                "timestamp": datetime.utcnow().isoformat(),
                "model": AgentConfig.get_model_id(),
                "session_id": session_id,
                "status": "success"
            }
            
            # Add tool usage information if available
            if hasattr(response, 'tool_calls') and response.tool_calls:
                result["tools_used"] = [tool.name for tool in response.tool_calls]
            
            logger.info("Request processed successfully")
            return result
            
        except Exception as format_error:
            logger.error(f"Response formatting error: {format_error}")
            return {
                "error": f"Response formatting failed: {str(format_error)}",
                "timestamp": datetime.utcnow().isoformat(),
                "status": "error"
            }
        
    except Exception as e:
        logger.error(f"Unexpected error processing request: {e}", exc_info=True)
        return {
            "error": f"Unexpected error: {str(e)}",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "error"
        }

# Removed async entrypoint to avoid streaming issues in testing
# The synchronous entrypoint above handles all requests

# Health check endpoint (automatically handled by BedrockAgentCoreApp)
# The /ping endpoint is automatically created by the framework

if __name__ == "__main__":
    # Run the AgentCore Runtime server
    logger.info("Starting VPC Agent Runtime Server...")
    logger.info(f"Server will start on http://0.0.0.0:8080")
    logger.info("Endpoints:")
    logger.info("  POST /invocations - Main agent processing")
    logger.info("  GET /ping - Health check")
    
    app.run()