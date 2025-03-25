from mcp.server.fastmcp import FastMCP
import signal
import requests
import json
from typing import Dict, Any, Optional
import time

# Configuration variables
MCP_NAME = "Dust MCP Server"
MCP_HOST = "127.0.0.1"  # if you run it locally
MCP_PORT = 5001         # default port
MCP_TIMEOUT = 30        # 30s timeout

# handle SIGINT (Ctrl+C) for gracefully shutdown
def signal_handler(sig, frame):
    print("\nShutting down mcp dust server...")
    exit(0)
signal.signal(signal.SIGINT, signal_handler)

# create an MCP server with increased timeout
mcp = FastMCP(
    name=MCP_NAME,
    host=MCP_HOST,
    timeout=MCP_TIMEOUT,
    port=MCP_PORT
    
    # Dust Agent configuration
    DUST_AGENT_ID = "8x9nuWdMnR"
    DUST_DOMAIN = "https://dust.tt"
    DUST_WORKSPACE_ID = "11453f1c9e"
    DUST_WORKSPACE_NAME = "WorkwithAI_Launchpad"
    DUST_API_KEY = "sk-28a4168f60a9b865380a0e350e5fd193"
    DUST_AGENT_NAME = "SystemsThinking"
    
    # Keep your existing count_r function and add this new function below it:
    # define the dust agent mcp tool
    @mcp.tool()
    def dust_systems_thinking(query: str, use_rag: bool = True, use_web: bool = True) -> Dict[Any, Any]:
        """
        Connect to the SystemsThinking Dust agent specializing in systems thinking, 
        cognitive neuroscience, and problem-solving strategies.
        
        Args:
            query: The question or request to send to the agent
            use_rag: Whether to use RAG Search (default: True)
            use_web: Whether to use Web Navigation (default: True)
        
        Returns:
            The response from the Dust agent
        """
        try:
            # Construct the API URL
            url = f"{DUST_DOMAIN}/api/v1/w/{DUST_WORKSPACE_ID}/apps/{DUST_AGENT_ID}/runs"
            
            # Prepare headers with API key
            headers = {
                "Authorization": f"Bearer {DUST_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # Prepare the payload
            payload = {
                "inputs": {
                    "query": query
                },
                "config": {
                    "use_rag_search": use_rag,
                    "use_web_navigation": use_web,
                    "use_reasoning": True,
                    "use_data_visualization": False
                }
            }
            
            # Make the API request
            response = requests.post(url, headers=headers, json=payload)
            
            # Check for successful response
            response.raise_for_status()
            
            # Parse and return the response
            return response.json()
        
        except requests.exceptions.RequestException as e:
            return {"error": f"Request error: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}if __name__ == "__main__":
                # start the server and add a error handling
                try:
                    # get mcp hostname
                    print(f"Starting MCP server '{MCP_NAME}' on {MCP_HOST}:{MCP_PORT}")
                    print(f"Connected to Dust agent '{DUST_AGENT_NAME}' (ID: {DUST_AGENT_ID})")
                    mcp.run()
                except Exception as e:
                    print(f"Error: {e}")
                    # sleep before exit to give time to show error message
                    time.sleep(5)
                    exit(1) # exit with error
    port=MCP_PORT
)

# define our mcp tool
@mcp.tool() 
def count_r(word:str) -> int:
    """ Count the number of 'r' letters in the given word """
    try:
        # add robust error handling
        if not isinstance(word, str):
            raise ValueError("Input must be a string")
        # count the numbers of lower and upper 'r' letters
        return word.count("r") + word.count("R")
    except Exception as e:
        # return 0 if an error occurs
        return str(e)

if __name__ == "__main__":
    # start the server and add a error handling
    try:
        # get mcp hostname
        print(f"Starting MCP server '{MCP_NAME}' on {MCP_HOST}:{MCP_PORT}")
        mcp.run()
    except Exception as e:
        print(f"Error: {e}")
        # sleep before exit to give time to show error message
        time.sleep(5)
        exit(1) # exit with error