# MCP Server for Dust Agent Integration

A custom MCP (Multi-Cloud Provider) server that connects to the Dust.tt agent platform via HTTP calls. This server exposes the capabilities of Dust AI agents through the MCP interface.

## Features

- Connect to Dust.tt AI agents via API
- Systems Thinking agent integration with cognitive neuroscience and problem-solving capabilities
- RAG (Retrieval Augmented Generation) support
- Web navigation capability
- Simplified MCP tool interface

## Prerequisites

- Python 3.10 or higher
- `pip` package manager
- A Dust.tt account with API access
- An existing Dust agent configuration

## Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/Ma3u/mcp-server-dust.git
   cd mcp-server-dust
   ```

2. Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
   ```

3. Install required dependencies:

   ```bash
   pip install --upgrade pip
   pip install mcp requests python-dotenv
   ```

4. Configure the Dust agent:
   - Create a `.env` file in the root directory with your configuration:
   ```
   DUST_AGENT_ID=your_agent_id
   DUST_DOMAIN=https://dust.tt
   DUST_WORKSPACE_ID=your_workspace_id
   DUST_WORKSPACE_NAME=your_workspace_name
   DUST_API_KEY=your_api_key
   DUST_AGENT_NAME=your_agent_name
   ```
   - This approach keeps your API keys secure and out of your code
   - Make sure to add `.env` to your `.gitignore` file to prevent committing sensitive information

The server configuration parameters in server.py are now loaded from environment variables with fallbacks:

### MCP Server Configuration

``` python
MCP_NAME = "Dust MCP Server"  # Name of your MCP server
MCP_HOST = "127.0.0.1"        # Host to run the server on
MCP_PORT = 5001               # Port to run the server on
MCP_TIMEOUT = 30              # Request timeout in seconds
```

## Running the Server

To start the MCP server:
```bash
python server.py
```

You should see output similar to:
```
Starting MCP server 'Dust MCP Server' on 127.0.0.1:5001
Connected to Dust agent 'SystemsThinking' (ID: 8x9nuWdMnR)
```

The server will run until interrupted with Ctrl+C.

## Claude Desktop Configuration
        
To configure Claude Desktop for use with this MCP server:
        
1. **Installation**:
   - Download Claude Desktop from the official Anthropic website (https://www.anthropic.com/claude/download)
   - Install the application following the on-screen instructions for your OS
        
2. **Initial Setup**:
   - Launch the app after installation
   - Sign in with your Anthropic account (free account is enough)
        
3. **Integration with MCP Server**:
   - Launch Claude Desktop and go to Settings
   - Select the "Developer" tab on the left sidebar
   - Click the "Edit Config" button at the bottom of the screen
   - Add your Dust MCP server to the configuration by including it in the `mcpServers` array:

```json
    {
        "mcpServers": {
            "dust": {
                "command": "/Users/ma3u/projects/mcp-server-dust/.venv/bin/python",
                "args": [
                "/Users/ma3u/projects/mcp-server-dust/server.py"
                ],
                "host": "127.0.0.1",
                "port": 5001,
                "timeout": 10000
            }
        }
    }
```
   - If there are existing entries in the `mcpServers` array, add your configuration as a new item
   - Save the configuration and restart Claude Desktop
        
4. **Applying Configuration Changes**:
   - After making changes to your MCP server configuration:
    - For Claude Desktop, quit the application completely 
    - Relaunch Claude Desktop for the new configuration to take effect
   - Verify the connection by checking if your server appears in the list in the Developer settings

5. **Testing in Claude Desktop**:
- Type i:"Use Systemsthinking Agent to explain MCP Protocol."

## Dust.tt API Workflow

The MCP Server interfaces with Dust.tt's API through a multi-step workflow. Each Claude request that uses the Dust agent follows this process:

### 1. Create a New Conversation

First, the server creates a new conversation with the Dust agent:

```bash
curl -X POST "https://dust.tt/api/v1/w/{WORKSPACE_ID}/assistant/conversations" \
  -H "Authorization: Bearer {YOUR_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Systems Thinking Conversation",
    "model": "claude-3-opus-20240229"
  }'
```

This returns a conversation ID that's used in subsequent requests:

```json
{
  "conversation": {
    "sId": "DhvpbhW74S",
    "title": "Systems Thinking Conversation",
    "created_at": 1742923287427
  }
}
```

### 2. Send a Message to the Conversation

Next, the server sends the user's query as a message to the conversation:

```bash
curl -X POST "https://dust.tt/api/v1/w/{WORKSPACE_ID}/assistant/conversations/{CONVERSATION_ID}/messages" \
  -H "Authorization: Bearer {YOUR_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Explain the MCP Protocol in detail",
    "mentions": [{
      "configurationId": "{AGENT_ID}",
      "context": {
        "timezone": "Europe/Berlin",
        "modelSettings": {"provider": "anthropic"}
      }
    }],
    "context": {
      "timezone": "Europe/Berlin"
    }
  }'
```

The response includes the message ID:

```json
{
  "message": {
    "sId": "qwenj3rusI",
    "conversation_sId": "DhvpbhW74S",
    "content": "Explain the MCP Protocol in detail",
    "author_name": "User",
    "author_type": "user",
    "created_at": 1742923287627
  }
}
```

### 3. Retrieve Messages from the Conversation

Finally, the server retrieves the agent's response. This requires a specific format for the message retrieval request:

```bash
curl -X POST "https://dust.tt/api/v1/w/{WORKSPACE_ID}/assistant/conversations/{CONVERSATION_ID}/messages" \
  -H "Authorization: Bearer {YOUR_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "RETRIEVAL_QUERY",
    "mentions": [{
      "configurationId": "{AGENT_ID}",
      "context": {
        "timezone": "Europe/Berlin",
        "modelSettings": {"provider": "anthropic"}
      }
    }],
    "context": {
      "timezone": "Europe/Berlin",
      "username": "api_retrieval",
      "queryType": "history_analysis"
    }
  }'
```

The response contains all messages in the conversation, including the agent's response:

```json
{
  "messages": [
    {
      "id": "msg_user123",
      "role": "user",
      "content": "Explain the MCP Protocol in detail",
      "timestamp": 1742923287627,
      "status": "processed"
    },
    {
      "id": "msg_agent456",
      "role": "assistant",
      "content": "The MCP (Mission Control Protocol) is a framework designed for...",
      "timestamp": 1742923290000,
      "status": "processed"
    }
  ]
}
```

### Important Notes About the API

- The message retrieval endpoint serves a dual purpose - it can be used to create new messages OR retrieve conversation history
- For message retrieval, a properly structured payload is required even though it's essentially a GET operation
- The content field is required and must be at least one character (we use "RETRIEVAL_QUERY" as a placeholder)
- The mentions and context fields must be structured correctly as shown above
- You need to poll this endpoint multiple times until the agent's response appears

### Error Handling

Common errors when working with the Dust.tt API:

- **400 Bad Request**: Often indicates malformed JSON or missing required fields in your request payload
- **401 Unauthorized**: Check your API key
- **404 Not Found**: Verify your workspace ID and conversation ID
- **429 Too Many Requests**: You've exceeded API rate limits

For debugging purposes, the server logs all API requests in curl format so you can reproduce and troubleshoot them manually.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.