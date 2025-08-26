#!/usr/bin/env python3
"""
Explore the A2A (Agent2Agent) Python SDK
"""

from a2a.client import A2AClient, ClientConfig
from a2a.types import AgentCard, AgentCapabilities, Message, Task
import json

def explore_agent_card():
    """Explore AgentCard structure"""
    print("=== AGENT CARD STRUCTURE ===")
    
    # Check what fields an AgentCard has
    print("AgentCard fields:")
    if hasattr(AgentCard, 'model_fields'):
        for field_name, field_info in AgentCard.model_fields.items():
            print(f"  - {field_name}: {field_info.annotation}")
    else:
        print("  AgentCard attributes:", [attr for attr in dir(AgentCard) if not attr.startswith('_')])

def explore_capabilities():
    """Explore AgentCapabilities structure"""
    print("\n=== AGENT CAPABILITIES ===")
    
    if hasattr(AgentCapabilities, 'model_fields'):
        for field_name, field_info in AgentCapabilities.model_fields.items():
            print(f"  - {field_name}: {field_info.annotation}")
    else:
        print("  AgentCapabilities attributes:", [attr for attr in dir(AgentCapabilities) if not attr.startswith('_')])

def explore_message():
    """Explore Message structure"""
    print("\n=== MESSAGE STRUCTURE ===")
    
    if hasattr(Message, 'model_fields'):
        for field_name, field_info in Message.model_fields.items():
            print(f"  - {field_name}: {field_info.annotation}")
    else:
        print("  Message attributes:", [attr for attr in dir(Message) if not attr.startswith('_')])

def explore_task():
    """Explore Task structure"""
    print("\n=== TASK STRUCTURE ===")
    
    if hasattr(Task, 'model_fields'):
        for field_name, field_info in Task.model_fields.items():
            print(f"  - {field_name}: {field_info.annotation}")
    else:
        print("  Task attributes:", [attr for attr in dir(Task) if not attr.startswith('_')])

def explore_client_config():
    """Explore ClientConfig"""
    print("\n=== CLIENT CONFIG ===")
    
    if hasattr(ClientConfig, 'model_fields'):
        for field_name, field_info in ClientConfig.model_fields.items():
            print(f"  - {field_name}: {field_info.annotation}")
    else:
        print("  ClientConfig attributes:", [attr for attr in dir(ClientConfig) if not attr.startswith('_')])

if __name__ == "__main__":
    print("Exploring A2A Python SDK Components\n")
    
    explore_agent_card()
    explore_capabilities()
    explore_message()
    explore_task()
    explore_client_config()
    
    print("\n=== A2A CLIENT METHODS ===")
    client_methods = [method for method in dir(A2AClient) if not method.startswith('_') and callable(getattr(A2AClient, method, None))]
    for method in client_methods:
        print(f"  - {method}")