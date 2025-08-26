"""
Agent2Agent Integration Package for AWS Telco AgentCore

This package provides Agent2Agent protocol integration for AWS telco agents,
enabling cross-agent communication and collaboration.
"""

__version__ = "1.0.0"
__author__ = "AWS Telco Infrastructure Team"

# Import key components for easy access
from .wrappers.eks_a2a_wrapper import EKSA2AWrapper

__all__ = [
    "EKSA2AWrapper"
]