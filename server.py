"""
Dust MCP Server - A bridge between Claude and the Dust.tt AI agent platform.

This module provides a FastMCP server that connects to the Dust.tt platform,
allowing users to interact with specialized AI agents through an MCP interface.
"""

from mcp.server.fastmcp import FastMCP
import signal
import requests
import json
import os
import logging
from typing import Dict, Any, Optional, List, Tuple
import time
from dotenv import load_dotenv

# Import local modules
from config import DustAgentConfig
from api_client import DustAPIClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [dust] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S.%fZ'
)
logger = logging.getLogger("dust")

# Load environment variables from .env file
load_dotenv()

# Global configuration instance
config = DustAgentConfig()

# Create an MCP server with increased timeout
mcp = FastMCP(
    name=config.mcp_name,
    host=config.mcp_host,
    timeout=config.mcp_timeout,
    port=config.mcp_port
)

# Signal handler for graceful shutdown on SIGINT
def signal_handler(sig, frame):
    """Handle SIGINT (Ctrl+C) to shutdown the server gracefully."""
    logger.info("Shutting down Dust MCP server...")
    mcp.server.shutdown()

# Register signal handler
signal.signal(signal.SIGINT, signal_handler)

def dust_systems_thinking(query: str, new_conversation: bool = False) -> Dict[Any, Any]:
    """
    Connect to the SystemsThinking Dust agent specializing in systems thinking, 
    cognitive neuroscience, and problem-solving strategies.
    
    Args:
        query: The question or request to send to the agent
        new_conversation: Whether to start a new conversation (default: False)
    
    Returns:
        Dict[Any, Any]: The response from the Dust agent or an error message
    """
    # Create API client
    api_client = DustAPIClient(config)
    
    # Start a new conversation if requested or if we don't have an active one
    if new_conversation or not config.conversation_id:
        logger.info("Starting a new conversation")
        success, conversation_id, error = api_client.create_conversation(query)
        if not success:
            return error
        config.conversation_id = conversation_id
    
    # Send the message in the conversation
    success, user_message_id, error = api_client.send_message(config.conversation_id, query)
    if not success:
        return error
    
    # Get the agent's response message
    success, agent_message_id, error = api_client.get_agent_message(config.conversation_id, user_message_id, query)
    if not success:
        return error
    
    # Get the content of the agent's response
    success, response_content, error = api_client.get_agent_response(config.conversation_id, agent_message_id)
    if not success:
        return error
    
    # Return the response content
    return {"content": response_content}



if __name__ == "__main__":
    """Main entry point for starting the MCP server."""
    # Start the server and add error handling
    try:
        # Register our dust_systems_thinking function
        mcp.add_tool(dust_systems_thinking, name="dust_systems_thinking", description="Connect to the Dust SystemsThinking agent to answer questions")
        
        # Start the server
        logger.info(f"Starting Dust MCP server at {config.mcp_host}:{config.mcp_port}")
        mcp.run()
    except Exception as e:
        logger.error(f"Error starting MCP server: {str(e)}")
