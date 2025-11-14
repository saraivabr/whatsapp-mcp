"""
Configuration settings for the backend
"""
import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""

    # Anthropic API
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    anthropic_model: str = "claude-sonnet-4-20250514"

    # WhatsApp Bridge URLs
    whatsapp_bridge_url: str = "http://localhost:8080"
    whatsapp_bridge_ws_url: str = "ws://localhost:8080"

    # MCP Server Configuration
    mcp_server_command: str = "uv"
    mcp_server_args: List[str] = ["run", "main.py"]
    mcp_server_cwd: str = "../whatsapp-mcp-server"

    # CORS
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ]

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# Create global settings instance
settings = Settings()
