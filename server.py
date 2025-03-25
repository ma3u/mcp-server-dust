from mcp.server.fastmcp import FastMCP
import signal
import requests
import json
import os
import logging
from typing import Dict, Any, Optional
import time
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [dust] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S.%fZ'
)
logger = logging.getLogger("dust")

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
DUST_API_KEY = os.getenv("DUST_API_KEY", "store SECRETS in .env file")
DUST_AGENT_NAME = os.getenv("DUST_AGENT_NAME", "SystemsThinking")

# Conversation state (global to maintain conversation)
CONVERSATION_ID = None
LAST_MESSAGE_ID = None

# handle SIGINT (Ctrl+C) for gracefully shutdown
def signal_handler(sig, frame):
    logger.info("Shutting down mcp dust server...")
    exit(0)
signal.signal(signal.SIGINT, signal_handler)

# create an MCP server with increased timeout
mcp = FastMCP(
    name=MCP_NAME,
    host=MCP_HOST,
    timeout=MCP_TIMEOUT,
    port=MCP_PORT
)

# helper function to format requests as curl commands for external debugging of the DUST API
def format_as_curl(url, method, headers, payload=None):
    """Format a request as a curl command for debugging"""
    headers_str = ' '.join([f"-H '{k}: {v}'" for k, v in headers.items()])
    
    if payload and method.upper() != "GET":
        payload_str = f"-d '{json.dumps(payload)}'"
        return f"curl -X {method.upper()} {headers_str} {payload_str} '{url}'"
    else:
        return f"curl -X {method.upper()} {headers_str} '{url}'"

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
    try:
        # Load API key and other parameters from environment
        DUST_API_KEY = os.getenv('DUST_API_KEY')
        DUST_DOMAIN = os.getenv('DUST_DOMAIN', 'https://dust.tt')
        DUST_WORKSPACE_ID = os.getenv('DUST_WORKSPACE_ID')
        DUST_AGENT_ID = os.getenv('DUST_AGENT_ID')
        
        if not all([DUST_API_KEY, DUST_WORKSPACE_ID, DUST_AGENT_ID]):
            error_msg = "Missing required environment variables: DUST_API_KEY, DUST_WORKSPACE_ID, or DUST_AGENT_ID"
            logger.error(error_msg)
            return {"error": error_msg}
            
        # Base headers for all API requests
        headers = {
            'Authorization': f'Bearer {DUST_API_KEY}',
            'Accept': 'application/json'
        }
        
        # Either create a new conversation or use existing one
        global CONVERSATION_ID
        
        # Step 1: Create new conversation if requested or if we don't have a valid ID
        if new_conversation or not CONVERSATION_ID:
            create_url = f"{DUST_DOMAIN}/api/v1/w/{DUST_WORKSPACE_ID}/assistant/conversations"
            
            # Add Content-Type for POST request
            headers['Content-Type'] = 'application/json'
            
            create_payload = {
                "title": f"Systems Thinking Query: {query[:30]}...",
                "agent_configuration_id": DUST_AGENT_ID
            }
            
            logger.info(f"Creating new conversation with: {create_url}")
            logger.debug(format_as_curl(create_url, "POST", headers, create_payload))
            
            try:
                create_response = requests.post(create_url, headers=headers, json=create_payload)
                create_response.raise_for_status()
                create_data = create_response.json()
                
                logger.debug(f"Create conversation response: {json.dumps(create_data)}")
                
                # Extract conversation ID from the nested structure
                if "conversation" in create_data and "sId" in create_data["conversation"]:
                    CONVERSATION_ID = create_data["conversation"]["sId"]
                    logger.info(f"Step 1: Created conversation with ID: {CONVERSATION_ID}")
                else:
                    error_msg = f"Step 1: Unexpected response format: {json.dumps(create_data)}"
                    logger.error(error_msg)
                    logger.error(f"Failed curl command: \n{format_as_curl(create_url, 'POST', headers, create_payload)}")
                    return {"error": error_msg}
                
            except requests.exceptions.RequestException as e:
                error_msg = f"Step 1: Failed to create conversation: {str(e)}"
                logger.error(error_msg)
                logger.error(f"Failed curl command: \n{format_as_curl(create_url, 'POST', headers, create_payload)}")
                return {"error": error_msg}
        
        # Step 2: Send a message in the conversation
        message_url = f"{DUST_DOMAIN}/api/v1/w/{DUST_WORKSPACE_ID}/assistant/conversations/{CONVERSATION_ID}/messages"
        
        # Get timezone from environment or use default
        timezone = os.getenv('DUST_TIMEZONE', 'Europe/Berlin')
        
        # Ensure we have Content-Type header for POST request
        headers['Content-Type'] = 'application/json'
        
        # Complete message payload structure as required by Dust API
        message_payload = {
            "content": query,
            "mentions": [{
                "configurationId": DUST_AGENT_ID,
                "context": {
                    "timezone": timezone,
                    "modelSettings": {
                        "provider": "anthropic",
                        "model": "claude-3-opus-20240229"
                    }
                }
            }],
            "context": {
                "timezone": timezone,
                "username": os.getenv('DUST_USERNAME', 'systems_analyst'),
                "fullName": os.getenv('DUST_FULLNAME', 'AI Research Team')
            }
        }
        
        logger.info(f"Sending message to: {message_url}")
        logger.debug(format_as_curl(message_url, "POST", headers, message_payload))
        
        try:
            message_response = requests.post(message_url, headers=headers, json=message_payload)
            message_response.raise_for_status()
            message_data = message_response.json()
            
            logger.debug(f"Send message response: {json.dumps(message_data)}")
            
            # Extract message ID with improved error handling for different response formats
            user_message_id = None
            
            # Try different possible response structures
            if "message" in message_data and "sId" in message_data["message"]:
                user_message_id = message_data["message"]["sId"]
            elif "id" in message_data:
                user_message_id = message_data["id"]
            elif "sId" in message_data:
                user_message_id = message_data["sId"]
            else:
                # Log the full structure to help understand the format
                logger.error(f"Could not find message ID in response: {json.dumps(message_data)}")
                return {"error": f"Step 2: Could not find message ID in response"}
                
            logger.info(f"Step 2: Sent message with ID: {user_message_id}")
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Step 2: Failed to send message: {str(e)}"
            logger.error(error_msg)
            logger.error(f"Failed curl command: \n{format_as_curl(message_url, 'POST', headers, message_payload)}")
            return {"error": error_msg}
        
        # Step 3: Get conversation messages to find agent's response
        conversation_messages_url = f"{DUST_DOMAIN}/api/v1/w/{DUST_WORKSPACE_ID}/assistant/conversations/{CONVERSATION_ID}/messages"
        
        # Add Content-Type for POST request
        headers['Content-Type'] = 'application/json'
        
        logger.info(f"Getting conversation messages from: {conversation_messages_url}")
        
        # Construct proper payload for message retrieval
        retrieval_payload = {
            "content": "RETRIEVAL_QUERY",
            "mentions": [{
                "configurationId": "8x9nuWdMnR",
                "context": {
                    "timezone": os.environ.get("DUST_TIMEZONE", "Europe/Berlin"),
                    "modelSettings": {"provider": "anthropic"}
                }
            }],
            "context": {
                "timezone": os.environ.get("DUST_TIMEZONE", "Europe/Berlin"),
                "username": os.environ.get("DUST_USERNAME", "api_retrieval"),
                "queryType": "history_analysis"
            }
        }
        
        logger.debug(format_as_curl(conversation_messages_url, "POST", headers, retrieval_payload))
        
        max_retries = 30
        agent_message_id = None
        
        for attempt in range(max_retries):
            logger.debug(f"Waiting for agent message (attempt {attempt+1}/{max_retries})...")
            
            try:
                messages_response = requests.post(conversation_messages_url, headers=headers, json=retrieval_payload)
                messages_response.raise_for_status()
                messages_data = messages_response.json()
                
                logger.debug(f"Messages response: {json.dumps(messages_data)}")
                
                # Extract messages from nested structure
                messages = []
                if "messages" in messages_data:
                    messages = messages_data["messages"]
                    
                # Look for an agent message that came after our user message
                found = False
                for message in messages:
                    # Skip messages that don't have both sId and created_at
                    if "sId" not in message or "created_at" not in message:
                        continue
                    
                    # If this is our user message, mark that we found it
                    if message["sId"] == user_message_id:
                        found = True
                        continue
                    
                    # If we've found our user message, and this is an agent message, we're done
                    if found and message.get("author_type") == "agent":
                        agent_message_id = message["sId"]
                        logger.info(f"Step 3: Found agent message with ID: {agent_message_id}")
                        break
                
                if agent_message_id:
                    break
                
                # Wait before trying again
                time.sleep(1)
                
            except requests.exceptions.RequestException as e:
                error_msg = f"Step 3: Failed to get messages: {str(e)}"
                logger.error(error_msg)
                logger.error(f"Failed curl command: \n{format_as_curl(conversation_messages_url, 'POST', headers, retrieval_payload)}")
                return {"error": error_msg}
        
        if not agent_message_id:
            error_msg = f"Step 3: No agent message found after {max_retries} attempts"
            logger.warning(error_msg)
            logger.warning(f"Last curl command attempted: \n{format_as_curl(conversation_messages_url, 'POST', headers, retrieval_payload)}")
            return {"error": error_msg}
        
        # Step 4: Poll for events on the agent message
        events_url = f"{DUST_DOMAIN}/api/v1/w/{DUST_WORKSPACE_ID}/assistant/conversations/{CONVERSATION_ID}/messages/{agent_message_id}/events"
        
        for attempt in range(max_retries):
            logger.debug(f"Polling for response (attempt {attempt+1}/{max_retries})...")
            logger.debug(format_as_curl(events_url, "GET", headers))
            
            try:
                events_response = requests.get(events_url, headers=headers)
                events_response.raise_for_status()
                events_data = events_response.json()
                
                logger.debug(f"Events response: {json.dumps(events_data)}")
                
                # Extract events from nested structure
                events = []
                if "events" in events_data:
                    events = events_data["events"]
                else:
                    error_msg = f"Unexpected response format: {json.dumps(events_data)}"
                    logger.error(error_msg)
                    logger.error(f"Failed curl command: \n{format_as_curl(events_url, 'GET', headers)}")
                    return {"error": error_msg}
                
                completed = False
                full_content = []
                
                # Look for content in events
                for event in events:
                    if event.get("type") == "content_block" and "content" in event:
                        # For content blocks, collect the content
                        full_content.append(event["content"])
                    
                    if event.get("type") == "status" and event.get("status") == "completed":
                        # For status events, check if completed
                        completed = True
                
                if completed:
                    # Join all content blocks into the response
                    response_content = "\n".join(full_content)
                    logger.info(f"Step 4: Received response: {response_content[:100]}...")
                    return {"response": response_content}
                
                # Wait before trying again
                time.sleep(1)
                
            except requests.exceptions.RequestException as e:
                error_msg = f"Step 4: Request error: {str(e)}"
                logger.error(error_msg)
                logger.error(f"Failed curl command: \n{format_as_curl(events_url, 'GET', headers)}")
                return {"error": error_msg}
        
        # If we get here, we've timed out
        error_msg = f"Step 4: Timed out waiting for a response after {max_retries} attempts"
        logger.warning(error_msg)
        logger.warning(f"Last curl command attempted: \n{format_as_curl(events_url, 'GET', headers)}")
        return {"error": error_msg}
    
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
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
        # log the error
        logger.error(f"Error in count_r: {str(e)}")
        # return 0 if an error occurs
        return str(e)

if __name__ == "__main__":
    # start the server and add a error handling
    try:
        # get mcp hostname
        logger.info(f"Starting MCP server '{MCP_NAME}' on {MCP_HOST}:{MCP_PORT}")
        logger.info(f"Connected to Dust agent '{DUST_AGENT_NAME}' (ID: {DUST_AGENT_ID})")
        mcp.run()
    except Exception as e:
        logger.error(f"Server startup error: {e}")
        # sleep before exit to give time to show error message
        time.sleep(5)
        exit(1) # exit with error