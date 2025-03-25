# mcp-server-dust
## connect to a dust agent via HTTP call

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
2. Install required dependencies:
   ```bash
   pip install requests
   pip install fastmcp
   ```

3. Configure the Dust agent:
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

## Claude Desktop Configuration

To configure Claude Desktop for use with this MCP server:

1. **Installation**:
   - Download Claude Desktop from the official Anthropic website (https://www.anthropic.com/claude/download)
   - Install the application following the on-screen instructions for your OS

2. **Initial Setup**:
   - Launch the app after installation
   - Sign in with your Anthropic account (free account is enough)

3. **Integration with MCP Server**:
   - To connect Claude Desktop to your MCP server, go to Settings > Integrations
   - Add a custom integration with the following details:
     - Name: "Dust Agent MCP"
     - URL: The URL where your MCP server is running (e.g., `http://127.0.0.1:5001`)
     - Authentication: API Key (not required)
   - Claude Desktop will now be able to use the capabilities of your Dust agent
   - 3. **Integration with MCP Server**:
      - To connect Claude Desktop to your MCP server, go to Settings > Integrations
      - Add a custom integration with the following details:
        - Name: "Dust Agent MCP"
        - URL: The URL where your MCP server is running (e.g., `http://127.0.0.1:5001`)
        - Authentication: API Key (not required)
      - Claude Desktop will now be able to use the capabilities of your Dust agent
      - You can also create a `claude_desktop.config` file with the following content:

        ```json
        {
          "mcpServers": [
            {
              "name": "Dust Agent MCP",
              "url": "http://127.0.0.1:5001",
              "authType": "none",
              "enabled": true
            }
          ]
        }## Claude Desktop Configuration
        
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
             ```
           - If there are existing entries in the `mcpServers` array, add your configuration as a new item
           - Save the configuration and restart Claude Desktop
        
        4. **Applying Configuration Changes**:
           - After making changes to your MCP server configuration:
             - Restart your MCP server to apply server-side changes
             - For Claude Desktop, quit the application completely (right-click the icon in taskbar/menu bar and select "Quit")
             - Relaunch Claude Desktop for the new configuration to take effect
           - Verify the connection by checking if your server appears in the list in the Developer settings
        ```
   
   1. **Applying Configuration Changes**:
      - After making changes to your MCP server or `claude_desktop.config` file
      - Save the `claude_desktop.config` file to your Claude Desktop configuration directory:
        - macOS: `~/Library/Application Support/Claude Desktop/config/`
        - Windows: `%APPDATA%\Claude Desktop\config\`
      - Restart Claude Desktop:
        - Quit the application completely (right-click the icon in taskbar/menu bar and select "Quit")
        - Relaunch Claude Desktop
        - The new configuration will be applied on restart
      - Verify connection in Settings > Integrations to ensure the MCP server is properly connected
4. **Applying Configuration Changes**:
   - After making changes to your MCP server or `claude_desktop.config` file
   - Save the `claude_desktop.config` file to your Claude Desktop configuration directory:
     - macOS: `~/Library/Application Support/Claude Desktop/config/`
     - Windows: `%APPDATA%\Claude Desktop\config\`
   - Restart Claude Desktop:
     - Quit the application completely (right-click the icon in taskbar/menu bar and select "Quit")
     - Relaunch Claude Desktop
     - The new configuration will be applied on restart
   - Verify connection in Settings > Integrations to ensure the MCP server is properly connected