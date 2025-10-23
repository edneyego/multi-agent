"""
Modelos de domínio para o sistema multi-agent.
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum


class AgentType(str, Enum):
    INFORMATION = "information"
    ACTION = "action"
    SUPERVISOR = "supervisor"


class MessageType(str, Enum):
    TEXT = "text"
    TOOL_CALL = "tool_call"
    TOOL_RESPONSE = "tool_response"
    ERROR = "error"


class Message(BaseModel):
    """Modelo de mensagem entre agentes."""
    id: str = Field(..., description="Identificador único da mensagem")
    content: str = Field(..., description="Conteúdo da mensagem")
    message_type: MessageType = Field(default=MessageType.TEXT)
    sender: str = Field(..., description="Agente remetente")
    receiver: Optional[str] = Field(None, description="Agente destinatário")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)


class Task(BaseModel):
    """Modelo de tarefa para ser processada pelos agentes."""
    id: str = Field(..., description="Identificador único da tarefa")
    content: str = Field(..., description="Conteúdo da tarefa")
    agent_type: AgentType = Field(..., description="Tipo de agente responsável")
    status: str = Field(default="pending")
    result: Optional[str] = Field(None)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(None)


class ConversationContext(BaseModel):
    """Contexto de conversação."""
    id: str = Field(..., description="Identificador da conversação")
    messages: List[Message] = Field(default_factory=list)
    current_agent: Optional[str] = Field(None)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(None)


class WeatherQuery(BaseModel):
    """Modelo para consultas meteorológicas."""
    location: str = Field(..., description="Localização para consulta")
    latitude: Optional[float] = Field(None)
    longitude: Optional[float] = Field(None)
    parameters: List[str] = Field(default=["temperature_2m", "wind_speed_10m", "weather_code"])


class WeatherResponse(BaseModel):
    """Resposta da consulta meteorológica."""
    location: str
    latitude: float
    longitude: float
    current: Dict[str, Any]
    forecast: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class AgentResponse(BaseModel):
    """Resposta padrão dos agentes."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    agent_id: str
    timestamp: datetime = Field(default_factory=datetime.now)