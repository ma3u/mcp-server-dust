"""
Configuration module for the Dust MCP Server.

This module provides the DustAgentConfig class which encapsulates
all configuration settings for the Dust agent and MCP server.
"""

import os
from typing import Dict, Tuple


class DustAgentConfig:
    """Configuration class for the Dust Agent environment and settings."""

    def __init__(self):
        """Initialize the Dust Agent configuration from environment variables."""
        # MCP Server configuration
        self.mcp_name = os.getenv("MCP_NAME", "Dust MCP Server")
        self.mcp_host = os.getenv("MCP_HOST", "127.0.0.1")
        self.mcp_port = int(os.getenv("MCP_PORT", "5001"))
        self.mcp_timeout = int(os.getenv("MCP_TIMEOUT", "30"))
        
        # Dust Agent configuration
        self.agent_id = os.getenv("DUST_AGENT_ID", "8x9nuWdMnR")
        self.domain = os.getenv("DUST_DOMAIN", "https://dust.tt")
        self.workspace_id = os.getenv("DUST_WORKSPACE_ID", "11453f1c9e")
        self.workspace_name = os.getenv("DUST_WORKSPACE_NAME", "WorkwithAI_Launchpad")
        self.api_key = os.getenv("DUST_API_KEY", "store SECRETS in .env file")
        self.agent_name = os.getenv("DUST_AGENT_NAME", "SystemsThinking")
        self.timezone = os.getenv("DUST_TIMEZONE", "Europe/Berlin")
        self.username = os.getenv("DUST_USERNAME", "systems_analyst")
        self.fullname = os.getenv("DUST_FULLNAME", "AI Research Team")
        
        # Conversation state
        self.conversation_id = None
        self.last_message_id = None

    def validate(self) -> Tuple[bool, str]:
        """
        Validate that all required configuration parameters are present.
        
        Returns:
            Tuple[bool, str]: A tuple containing (is_valid, error_message)
        """
        if not self.api_key or self.api_key == "store SECRETS in .env file":
            return False, "Missing DUST_API_KEY environment variable"
        
        if not self.workspace_id:
            return False, "Missing DUST_WORKSPACE_ID environment variable"
            
        if not self.agent_id:
            return False, "Missing DUST_AGENT_ID environment variable"
            
        return True, ""
    
    def get_headers(self, include_content_type: bool = True) -> Dict[str, str]:
        """
        Get standardized headers for Dust API requests.
        
        Args:
            include_content_type: Whether to include Content-Type header
            
        Returns:
            Dict[str, str]: Headers dictionary for API requests
        """
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Accept': 'application/json'
        }
        if include_content_type:
            headers['Content-Type'] = 'application/json'
        return headers
