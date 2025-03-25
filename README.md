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
   pip install mcp requests
   ```

4. Configure the Dust agent:
   - Replace the placeholder values in the configuration with your actual Dust agent details.

The server configuration is done in the server.py file. The following parameters can be modified:

### MCP Server Configuration

``` python
MCP_NAME = "Dust MCP Server"  # Name of your MCP server
MCP_HOST = "127.0.0.1"        # Host to run the server on
MCP_PORT = 5001               # Port to run the server on
MCP_TIMEOUT = 30              # Request timeout in seconds
```

### Dust Agent Configuration:

``` python
DUST_AGENT_ID = "8x9nuWdMnR"           # The ID of your Dust agent
DUST_DOMAIN = "https://dust.tt"           # Dust API domain
DUST_WORKSPACE_ID = "11453f1c9e"   # Your Dust workspace ID
DUST_WORKSPACE_NAME = "WorkwithAI_Launchpad"    # Your Dust workspace name
DUST_API_KEY = "sk-XXX"             # Your Dust API key
DUST_AGENT_NAME = "SystemsThinking"             # Name of your Dust agent
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

5. **Testing the Connection**:
   {
     "specification_hash": "latest",
     "inputs": [
       {
         "query": "your question",
         "use_rag_search": true,
         "use_web_navigation": true
       }
     ]
   }