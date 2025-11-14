"""
Pydantic models for request/response validation
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Chat message from user"""
    message: str = Field(..., description="User message")
    history: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description="Conversation history"
    )


class ChatResponse(BaseModel):
    """Response from Claude"""
    response: str = Field(..., description="Claude's response")
    success: bool = Field(default=True, description="Success status")
    tool_calls: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Tools called during processing"
    )


class QRCodeResponse(BaseModel):
    """QR code response"""
    success: bool
    status: str
    qr_code: Optional[str] = None
    message: Optional[str] = None


class ConnectionStatusResponse(BaseModel):
    """WhatsApp connection status"""
    status: str = Field(..., description="Connection status")
    qr_code: Optional[str] = Field(None, description="QR code if available")
    message: Optional[str] = Field(None, description="Status message")
    timestamp: int = Field(..., description="Timestamp of status")


class MCPTool(BaseModel):
    """MCP tool definition"""
    name: str
    description: str
    input_schema: Dict[str, Any]


class MCPToolCall(BaseModel):
    """MCP tool call request"""
    tool_name: str
    arguments: Dict[str, Any]


class MCPToolResult(BaseModel):
    """MCP tool call result"""
    tool_name: str
    result: Any
    error: Optional[str] = None
