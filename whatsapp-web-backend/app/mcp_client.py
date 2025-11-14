"""
MCP Client for communicating with the WhatsApp MCP server
"""
import asyncio
import json
from typing import List, Dict, Any, Optional
import subprocess


class MCPClient:
    """Client for interacting with MCP server"""

    def __init__(self, server_command: str, server_args: List[str], cwd: str = None):
        self.server_command = server_command
        self.server_args = server_args
        self.cwd = cwd
        self.process: Optional[subprocess.Popen] = None
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self.message_id = 0
        self.tools_cache: Optional[List[Dict[str, Any]]] = None

    async def start(self):
        """Start the MCP server process"""
        print(f"Starting MCP server: {self.server_command} {' '.join(self.server_args)}")

        # Start the MCP server as a subprocess
        self.process = await asyncio.create_subprocess_exec(
            self.server_command,
            *self.server_args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.cwd
        )

        self.reader = self.process.stdout
        self.writer = self.process.stdin

        print("MCP server started successfully")

        # Initialize the connection
        await self._initialize()

    async def stop(self):
        """Stop the MCP server process"""
        if self.process:
            self.process.terminate()
            await self.process.wait()
            print("MCP server stopped")

    async def _initialize(self):
        """Initialize the MCP connection"""
        # Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "whatsapp-web-backend",
                    "version": "0.1.0"
                }
            }
        }

        await self._send_request(init_request)
        response = await self._read_response()

        if "error" in response:
            raise Exception(f"MCP initialization failed: {response['error']}")

        print("MCP connection initialized")

        # Send initialized notification
        initialized_notif = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        await self._send_request(initialized_notif)

    def _next_id(self) -> int:
        """Get next message ID"""
        self.message_id += 1
        return self.message_id

    async def _send_request(self, request: Dict[str, Any]):
        """Send a JSON-RPC request"""
        message = json.dumps(request) + "\n"
        self.writer.write(message.encode())
        await self.writer.drain()

    async def _read_response(self) -> Dict[str, Any]:
        """Read a JSON-RPC response"""
        line = await self.reader.readline()
        if not line:
            raise Exception("MCP server connection closed")
        return json.loads(line.decode())

    async def get_tools(self) -> List[Dict[str, Any]]:
        """
        Get available tools from MCP server

        Returns:
            List of tool definitions in Anthropic format
        """
        # Return cached tools if available
        if self.tools_cache:
            return self.tools_cache

        # Request tools from MCP server
        request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/list"
        }

        await self._send_request(request)
        response = await self._read_response()

        if "error" in response:
            raise Exception(f"Failed to get tools: {response['error']}")

        # Convert MCP tools to Anthropic tool format
        mcp_tools = response.get("result", {}).get("tools", [])
        anthropic_tools = []

        for tool in mcp_tools:
            anthropic_tool = {
                "name": tool["name"],
                "description": tool.get("description", ""),
                "input_schema": tool.get("inputSchema", {
                    "type": "object",
                    "properties": {},
                    "required": []
                })
            }
            anthropic_tools.append(anthropic_tool)

        # Cache the tools
        self.tools_cache = anthropic_tools

        print(f"Loaded {len(anthropic_tools)} tools from MCP server")
        return anthropic_tools

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Call an MCP tool

        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments

        Returns:
            Tool execution result
        """
        request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }

        await self._send_request(request)
        response = await self._read_response()

        if "error" in response:
            error_msg = response["error"].get("message", "Unknown error")
            raise Exception(f"Tool call failed: {error_msg}")

        result = response.get("result", {})

        # Extract content from MCP response
        content = result.get("content", [])
        if not content:
            return "No result"

        # Combine all text content
        text_parts = []
        for item in content:
            if item.get("type") == "text":
                text_parts.append(item.get("text", ""))

        return "\n".join(text_parts) if text_parts else str(result)


    async def list_tools_names(self) -> List[str]:
        """Get list of available tool names"""
        tools = await self.get_tools()
        return [tool["name"] for tool in tools]
