"""
WhatsApp Web Backend - FastAPI server for web interface
"""
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx

from .models import ChatMessage, ChatResponse, QRCodeResponse, ConnectionStatusResponse
from .claude_client import ClaudeClient
from .mcp_client import MCPClient
from .config import settings


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass


manager = ConnectionManager()


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    # Startup
    print("Starting WhatsApp Web Backend...")

    # Initialize clients
    app.state.claude_client = ClaudeClient(api_key=settings.anthropic_api_key)
    app.state.mcp_client = MCPClient(
        server_command=settings.mcp_server_command,
        server_args=settings.mcp_server_args
    )

    # Start MCP client
    await app.state.mcp_client.start()
    print("MCP client started successfully")

    yield

    # Shutdown
    print("Shutting down WhatsApp Web Backend...")
    await app.state.mcp_client.stop()


# Create FastAPI app
app = FastAPI(
    title="WhatsApp Web Backend",
    description="Backend server for WhatsApp MCP web interface",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "WhatsApp Web Backend is running"}


@app.get("/api/qrcode", response_model=QRCodeResponse)
async def get_qrcode():
    """Get QR code from WhatsApp bridge"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.whatsapp_bridge_url}/api/qrcode")
            response.raise_for_status()
            data = response.json()

            return QRCodeResponse(
                success=data.get("success", False),
                status=data.get("status", "unknown"),
                qr_code=data.get("qr_code"),
                message=data.get("message")
            )
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Failed to get QR code: {str(e)}")


@app.get("/api/connection-status", response_model=ConnectionStatusResponse)
async def get_connection_status():
    """Get WhatsApp connection status"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.whatsapp_bridge_url}/api/connection-status")
            response.raise_for_status()
            data = response.json()

            return ConnectionStatusResponse(
                status=data.get("status", "unknown"),
                qr_code=data.get("qr_code"),
                message=data.get("message"),
                timestamp=data.get("timestamp", 0)
            )
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


@app.post("/api/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """
    Process a chat message through Claude with MCP tools access
    """
    try:
        # Get Claude client from app state
        claude_client: ClaudeClient = app.state.claude_client
        mcp_client: MCPClient = app.state.mcp_client

        # Get available MCP tools
        tools = await mcp_client.get_tools()

        # Send message to Claude with tools
        response_text = await claude_client.chat(
            message=message.message,
            conversation_history=message.history or [],
            tools=tools,
            mcp_client=mcp_client
        )

        return ChatResponse(
            response=response_text,
            success=True
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@app.websocket("/ws/whatsapp-status")
async def websocket_whatsapp_status(websocket: WebSocket):
    """
    WebSocket endpoint that forwards WhatsApp connection status from the Go bridge
    """
    await manager.connect(websocket)

    try:
        # Connect to Go bridge WebSocket
        async with websockets.connect(f"{settings.whatsapp_bridge_ws_url}/ws/status") as bridge_ws:
            # Forward messages from bridge to client
            async for message in bridge_ws:
                await manager.send_message({"data": message}, websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """
    WebSocket endpoint for streaming chat responses
    """
    await manager.connect(websocket)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message = data.get("message", "")
            history = data.get("history", [])

            if not message:
                await websocket.send_json({"error": "Empty message"})
                continue

            # Get clients
            claude_client: ClaudeClient = app.state.claude_client
            mcp_client: MCPClient = app.state.mcp_client

            # Get available MCP tools
            tools = await mcp_client.get_tools()

            # Stream response from Claude
            async for chunk in claude_client.chat_stream(
                message=message,
                conversation_history=history,
                tools=tools,
                mcp_client=mcp_client
            ):
                await websocket.send_json({"type": "chunk", "content": chunk})

            # Send end marker
            await websocket.send_json({"type": "end"})

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"Chat WebSocket error: {e}")
        await websocket.send_json({"type": "error", "message": str(e)})
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
