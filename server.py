from mcp.server.fastmcp import FastMCP
import signal
import requests
import json
import os
from typing import Dict, Any, Optional
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration variables
MCP_NAME = "Dust MCP Server"
MCP_HOST = "127.0.0.1"  # if you run it locally
MCP_PORT = 5001         # default port
MCP_TIMEOUT = 30        # 30s timeout

# Dust Agent configuration
DUST_AGENT_ID = os.getenv("DUST_AGENT_ID", "8x9nuWdMnR")
DUST_DOMAIN = os.getenv("DUST_DOMAIN", "https://dust.tt")
DUST_WORKSPACE_ID = os.getenv("DUST_WORKSPACE_ID", "11453f1c9e")
DUST_WORKSPACE_NAME = os.getenv("DUST_WORKSPACE_NAME", "WorkwithAI_Launchpad")
DUST_API_KEY = os.getenv("DUST_API_KEY", "sk-28a4168f60a9b865380a0e350e5fd193")
DUST_AGENT_NAME = os.getenv("DUST_AGENT_NAME", "SystemsThinking")

# Conversation state (global to maintain conversation)
CONVERSATION_ID = None
LAST_MESSAGE_ID = None

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
)

# define the dust agent mcp tool
@mcp.tool()
def dust_systems_thinking(query: str, new_conversation: bool = False) -> Dict[Any, Any]:
    """
    Connect to the SystemsThinking Dust agent specializing in systems thinking, 
    cognitive neuroscience, and problem-solving strategies.
    
    Args:
        query: The question or request to send to the agent
        new_conversation: Whether to start a new conversation (default: False)
    
    Returns:
        The response from the Dust agent
    """
    global CONVERSATION_ID, LAST_MESSAGE_ID
    
    try:
        headers = {
            "Authorization": f"Bearer {DUST_API_KEY}",
            "Content-Type": "application/json",
            "accept": "application/json"
        }
        
        # If starting a new conversation or no conversation exists
        if new_conversation or CONVERSATION_ID is None:
            # Step 1: Create a new conversation
            create_url = f"{DUST_DOMAIN}/api/v1/w/{DUST_WORKSPACE_ID}/assistant/conversations"
            create_payload = {
                "title": f"Systems Thinking Query: {query[:30]}...",
                "agent_configuration_id": DUST_AGENT_ID
            }
            
            print(f"Creating new conversation with: {create_url}")
            print(f"Payload: {json.dumps(create_payload, indent=2)}")
            
            create_response = requests.post(create_url, headers=headers, json=create_payload)
            create_response.raise_for_status()
            create_data = create_response.json()
            
            CONVERSATION_ID = create_data.get("conversation", {}).get("sId")
            print(f"Created new conversation with ID: {CONVERSATION_ID}")
            
            if not CONVERSATION_ID:
                raise ValueError("Failed to get conversation ID from response")
        else:
            print(f"Continuing conversation with ID: {CONVERSATION_ID}")
        
        # Step 2: Send a message to the conversation
        message_url = f"{DUST_DOMAIN}/api/v1/w/{DUST_WORKSPACE_ID}/assistant/conversations/{CONVERSATION_ID}/messages"
        message_payload = {
            "content": query
        }
        
        print(f"Sending message to: {message_url}")
        print(f"Payload: {json.dumps(message_payload, indent=2)}")
        
        message_response = requests.post(message_url, headers=headers, json=message_payload)
        message_response.raise_for_status()
        message_data = message_response.json()
        
        LAST_MESSAGE_ID = message_data.get("message", {}).get("sId")
        print(f"Sent message with ID: {LAST_MESSAGE_ID}")
        
        if not LAST_MESSAGE_ID:
            raise ValueError("Failed to get message ID from response")
        
        # Step 3: Wait for the agent to respond (poll for events)
        events_url = f"{DUST_DOMAIN}/api/v1/w/{DUST_WORKSPACE_ID}/assistant/conversations/{CONVERSATION_ID}/messages/{LAST_MESSAGE_ID}/events"
        
        max_retries = 30
        for attempt in range(max_retries):
            print(f"Polling for response (attempt {attempt+1}/{max_retries})...")
            events_response = requests.get(events_url, headers=headers)
            events_response.raise_for_status()
            events_data = events_response.json()
            
            # Check if the agent has responded
            events = events_data.get("events", [])
            completed = False
            agent_response = []
            
            for event in events:
                if event.get("type") == "MESSAGE_CREATED" and event.get("role") == "ASSISTANT":
                    agent_response.append(event.get("content", ""))
                elif event.get("type") == "MESSAGE_CREATED_LOADING_DONE" and event.get("role") == "ASSISTANT":
                    completed = True
            
            if completed and agent_response:
                response_text = "\n".join(agent_response)
                print(f"Got response from agent: {response_text[:100]}...")
                return {"response": response_text}
            
            # If not completed, wait and try again
            time.sleep(1)
        
        return {"error": "Timed out waiting for agent response"}
    
    except requests.exceptions.RequestException as e:
        error_msg = f"Request error: {str(e)}"
        print(f"ERROR: {error_msg}")
        return {"error": error_msg}
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"ERROR: {error_msg}")
        return {"error": error_msg}

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
        print(f"Connected to Dust agent '{DUST_AGENT_NAME}' (ID: {DUST_AGENT_ID})")
        mcp.run()
    except Exception as e:
        print(f"Error: {e}")
        # sleep before exit to give time to show error message
        time.sleep(5)
        exit(1) # exit with error