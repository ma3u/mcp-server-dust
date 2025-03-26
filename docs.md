# Dust MCP Server Documentation

## Overview

The Dust MCP Server is a middleware solution that enables Windsurf IDE to communicate with the Dust.tt API for AI-powered assistance. This server acts as a bridge between the Windsurf JSON-RPC interface and the Dust.tt conversational API, allowing users to interact with Dust AI agents directly from their development environment.

## Architecture

The system is composed of three main components:

1. **Configuration (`config.py`)**: Manages environment variables and configuration settings
2. **API Client (`api_client.py`)**: Handles all interactions with the Dust.tt API
3. **Server (`server.py`)**: Implements the JSON-RPC interface for the Windsurf IDE

### Data Flow

1. Windsurf IDE sends a JSON-RPC request to the MCP server
2. The server processes the request and translates it to the appropriate Dust API calls
3. The API client communicates with Dust.tt and retrieves responses
4. The server formats the response and returns it to Windsurf IDE

## Components

### Configuration (`config.py`)

The configuration module manages all environment variables and settings needed for connecting to the Dust API.

```python
class DustAgentConfig:
    """Configuration for Dust API integration."""
    
    def __init__(self, env_file=".env"):
        """Initialize configuration from environment variables."""
        # Load configuration from .env file
        
    def get_headers(self):
        """Get HTTP headers for API requests."""
        # Return authorization headers
```

### API Client (`api_client.py`)

The API client handles all the communication with the Dust.tt API, including:

1. Creating and managing conversations
2. Sending user messages
3. Retrieving agent responses
4. Error handling

```python
class DustAPIClient:
    """Client for interacting with the Dust.tt API."""
    
    def __init__(self, config):
        """Initialize with configuration."""
        self.config = config
        
    def create_conversation(self):
        """Create a new conversation."""
        # API call to create conversation
        
    def send_user_message(self, conversation_id, content):
        """Send a user message to a conversation."""
        # API call to send message
        
    def get_agent_message(self, conversation_id, user_message_id):
        """Get agent's response message ID."""
        # API call to retrieve agent message
        
    def get_agent_response(self, conversation_id, agent_message_id):
        """Get the content of an agent's message."""
        # API call to get message content
```

### Server (`server.py`)

The server component implements the JSON-RPC interface that Windsurf uses to communicate with AI systems.

```python
class DustMCPServer:
    """JSON-RPC server for Dust.tt integration."""
    
    def __init__(self, host, port):
        """Initialize the server."""
        # Configure JSON-RPC server
        
    def handle_jsonrpc(self, request):
        """Handle JSON-RPC requests."""
        # Process request and return response
```

## Setup

1. Clone the repository
2. Create a `.env` file with your Dust.tt API credentials:

```env
DUST_API_KEY=your_api_key
DUST_WORKSPACE_ID=your_workspace_id
DUST_AGENT_ID=your_agent_id
DUST_DOMAIN=https://dust.tt
PORT=5001
TIMEZONE=Europe/Berlin
```

1. Install required dependencies:

```bash
pip install -r requirements.txt
```

1. Start the server:

```bash
python server.py
```

## Usage

The server exposes a JSON-RPC endpoint at `http://localhost:5001/jsonrpc` with the following methods:

### `tools/list`

Lists available AI tools (agents).

### `tools/call`

Calls a specific AI tool with parameters.

Example:

```json
{
  "method": "tools/call",
  "params": {
    "name": "dust_systems_thinking",
    "arguments": {
      "query": "What is Systems Thinking?", 
      "new_conversation": true
    }
  },
  "jsonrpc": "2.0",
  "id": 1
}
```

## Troubleshooting

### Common Issues

1. **Connection errors**: Verify that your API key and workspace ID are correct
2. **Timeout errors**: Check the Dust.tt API status and ensure your request is properly formatted
3. **Response format errors**: The API format may have changed, check logs for details

### Logging

The server logs detailed information to `/Users/ma3u/Library/Logs/Claude/mcp-server-dust.log`. Check this file for debugging information.

## Advanced Configuration

### Agent Selection

To use a different agent, modify the `DUST_AGENT_ID` in your `.env` file to the ID of the desired agent.

### Rate Limiting

The server implements exponential backoff and retry logic to handle API rate limits and temporary failures.
