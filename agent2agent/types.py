#!/usr/bin/env python3
"""
Agent2Agent Types and Data Models

Defines the core types and data structures for Agent2Agent communication protocol.
"""

from typing import List, Optional, Dict, Any, Union
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class Role(Enum):
    """Message role enumeration"""
    user = "user"
    agent = "agent"
    system = "system"


@dataclass
class TextPart:
    """Text part of a message"""
    text: str
    
    def __post_init__(self):
        if not isinstance(self.text, str):
            raise ValueError("TextPart text must be a string")


@dataclass
class Message:
    """A2A message structure"""
    message_id: str
    role: Role
    parts: List[TextPart]
    kind: str = "message"
    context_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        
        if not self.parts:
            raise ValueError("Message must have at least one part")
        
        if not all(isinstance(part, TextPart) for part in self.parts):
            raise ValueError("All message parts must be TextPart instances")


@dataclass
class AgentCapabilities:
    """Agent capabilities definition"""
    streaming: bool = False
    push_notifications: bool = False
    state_transition_history: bool = False
    extensions: List[str] = None
    
    def __post_init__(self):
        if self.extensions is None:
            self.extensions = []


@dataclass
class AgentSkill:
    """Agent skill definition"""
    id: str
    name: str
    description: str
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        
        if not self.id or not self.name:
            raise ValueError("AgentSkill must have id and name")


@dataclass
class AgentProvider:
    """Agent provider information"""
    organization: str
    url: Optional[str] = None
    contact: Optional[str] = None
    
    def __post_init__(self):
        if not self.organization:
            raise ValueError("AgentProvider must have organization")


@dataclass
class AgentCard:
    """Agent card containing agent metadata and capabilities"""
    name: str
    version: str
    description: str
    url: str
    capabilities: AgentCapabilities
    skills: List[AgentSkill]
    provider: AgentProvider
    default_input_modes: List[str] = None
    default_output_modes: List[str] = None
    protocol_version: str = "1.0"
    
    def __post_init__(self):
        if self.default_input_modes is None:
            self.default_input_modes = ["text"]
        
        if self.default_output_modes is None:
            self.default_output_modes = ["text"]
        
        if not all([self.name, self.version, self.description, self.url]):
            raise ValueError("AgentCard must have name, version, description, and url")
        
        if not isinstance(self.capabilities, AgentCapabilities):
            raise ValueError("AgentCard capabilities must be AgentCapabilities instance")
        
        if not isinstance(self.provider, AgentProvider):
            raise ValueError("AgentCard provider must be AgentProvider instance")
        
        if not all(isinstance(skill, AgentSkill) for skill in self.skills):
            raise ValueError("All skills must be AgentSkill instances")


@dataclass
class A2ARequest:
    """A2A request structure"""
    target_agent: str
    action: str
    parameters: Dict[str, Any]
    request_id: Optional[str] = None
    timeout: Optional[int] = 30
    
    def __post_init__(self):
        if self.request_id is None:
            self.request_id = f"req-{datetime.utcnow().timestamp()}"


@dataclass
class A2AResponse:
    """A2A response structure"""
    request_id: str
    status: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


# Utility functions for A2A protocol

def create_text_message(text: str, role: Role = Role.user, context_id: Optional[str] = None) -> Message:
    """Create a simple text message"""
    return Message(
        message_id=f"msg-{datetime.utcnow().timestamp()}",
        role=role,
        parts=[TextPart(text=text)],
        context_id=context_id
    )


def create_agent_skill(skill_id: str, name: str, description: str, tags: List[str] = None) -> AgentSkill:
    """Create an agent skill with validation"""
    return AgentSkill(
        id=skill_id,
        name=name,
        description=description,
        tags=tags or []
    )


def create_basic_capabilities(streaming: bool = False, notifications: bool = False) -> AgentCapabilities:
    """Create basic agent capabilities"""
    return AgentCapabilities(
        streaming=streaming,
        push_notifications=notifications,
        state_transition_history=True,
        extensions=[]
    )