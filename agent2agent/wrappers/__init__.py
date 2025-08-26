"""
Agent2Agent Wrappers for AWS Telco Agents

This module contains A2A wrapper classes that make existing AgentCore agents
compatible with the Agent2Agent protocol.
"""

from .eks_a2a_wrapper import EKSA2AWrapper

__all__ = [
    "EKSA2AWrapper"
]