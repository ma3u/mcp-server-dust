"""
API client module for interacting with the Dust.tt platform.

This module provides the DustAPIClient class that handles all API calls
to the Dust.tt service.
"""

import json
import logging
import requests
import time
from typing import Dict, Any, Optional, Tuple

# Configure logging
logger = logging.getLogger("dust")


class DustAPIClient:
    """Client for interacting with the Dust.tt API."""
    
    def __init__(self, config):
        """
        Initialize the Dust API Client.
        
        Args:
            config: DustAgentConfig instance containing API credentials and settings
        """
        self.config = config
    
    def format_as_curl(self, url: str, method: str, headers: Dict[str, str], 
                       payload: Optional[Dict[Any, Any]] = None) -> str:
        """
        Format a request as a curl command for debugging purposes.
        
        Args:
            url: The request URL
            method: HTTP method (GET, POST, etc.)
            headers: Request headers
            payload: Optional request payload (for POST, PUT, etc.)
            
        Returns:
            str: Formatted curl command
        """
        headers_str = ' '.join([f'-H "{k}: {v}"' for k, v in headers.items()])
        
        if payload:
            payload_str = f"-d '{json.dumps(payload)}'"
            return f"curl -X {method.upper()} {headers_str} {payload_str} {url}"
        else:
            return f"curl -X {method.upper()} {headers_str} {url}"
    
    def handle_request_error(self, step: str, error: str, url: str, 
                           method: str, headers: Dict[str, str], 
                           payload: Optional[Dict[Any, Any]] = None) -> Dict[str, str]:
        """
        Standardized error handling for API requests.
        
        Args:
            step: Current step identifier (for logging)
            error: Error message
            url: Request URL
            method: HTTP method
            headers: Request headers
            payload: Optional request payload
            
        Returns:
            Dict[str, str]: Error response dictionary
        """
        error_msg = f"Step {step}: {error}"
        logger.error(error_msg)
        logger.error(f"Failed curl command: \n{self.format_as_curl(url, method, headers, payload)}")
        return {"error": error_msg}
    
    def create_conversation(self, query: str) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Create a new conversation on the Dust platform.
        
        Args:
            query: The initial query text
            
        Returns:
            Tuple containing:
                - Success status (bool)
                - Conversation ID if successful, None otherwise
                - Error dict if failed, None otherwise
        """
        create_url = f"{self.config.domain}/api/v1/w/{self.config.workspace_id}/assistant/conversations"
        headers = self.config.get_headers()
        
        create_payload = {
            "title": f"Systems Thinking Query: {query[:30]}...",
            "agent_configuration_id": self.config.agent_id
        }
        
        logger.info(f"Creating new conversation with: {create_url}")
        logger.debug(self.format_as_curl(create_url, "POST", headers, create_payload))
        
        try:
            create_response = requests.post(create_url, headers=headers, json=create_payload)
            create_response.raise_for_status()
            create_data = create_response.json()
            
            logger.debug(f"Create conversation response: {json.dumps(create_data)}")
            
            # Extract conversation ID from the nested structure
            if "conversation" in create_data and "sId" in create_data["conversation"]:
                conversation_id = create_data["conversation"]["sId"]
                logger.info(f"Step 1: Created conversation with ID: {conversation_id}")
                return True, conversation_id, None
            else:
                error = self.handle_request_error(
                    "1", 
                    f"Unexpected response format: {json.dumps(create_data)}", 
                    create_url, "POST", headers, create_payload
                )
                return False, None, error
                
        except requests.exceptions.RequestException as e:
            error = self.handle_request_error(
                "1", 
                f"Failed to create conversation: {str(e)}", 
                create_url, "POST", headers, create_payload
            )
            return False, None, error
    
    def send_message(self, conversation_id: str, query: str) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Send a message in an existing conversation.
        
        Args:
            conversation_id: The conversation ID
            query: The query text to send
            
        Returns:
            Tuple containing:
                - Success status (bool)
                - Message ID if successful, None otherwise
                - Error dict if failed, None otherwise
        """
        message_url = f"{self.config.domain}/api/v1/w/{self.config.workspace_id}/assistant/conversations/{conversation_id}/messages"
        headers = self.config.get_headers()
        
        # Complete message payload structure as required by Dust API
        message_payload = {
            "content": query,
            "mentions": [{
                "configurationId": self.config.agent_id,
                "context": {
                    "timezone": self.config.timezone,
                    "modelSettings": {
                        "provider": "anthropic",
                        "model": "claude-3-opus-20240229"
                    }
                }
            }],
            "context": {
                "timezone": self.config.timezone,
                "username": self.config.username,
                "fullName": self.config.fullname
            }
        }
        
        logger.info(f"Sending message to conversation: {message_url}")
        logger.debug(self.format_as_curl(message_url, "POST", headers, message_payload))
        
        try:
            message_response = requests.post(message_url, headers=headers, json=message_payload)
            message_response.raise_for_status()
            message_data = message_response.json()
            
            logger.debug(f"Send message response: {json.dumps(message_data)}")
            
            # Extract message ID for our user's message
            user_message_id = None
            if "message" in message_data and "sId" in message_data["message"]:
                user_message_id = message_data["message"]["sId"]
            else:
                # Log the full structure to help understand the format
                logger.error(f"Could not find message ID in response: {json.dumps(message_data)}")
                return False, None, {"error": f"Step 2: Could not find message ID in response"}
                
            logger.info(f"Step 2: Sent message with ID: {user_message_id}")
            return True, user_message_id, None
                
        except requests.exceptions.RequestException as e:
            error = self.handle_request_error(
                "2", 
                f"Failed to send message: {str(e)}", 
                message_url, "POST", headers, message_payload
            )
            return False, None, error
    
    def get_agent_message(self, conversation_id: str, user_message_id: str, 
                         max_retries: int = 30) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Get the agent's response message to a user message.
        
        Args:
            conversation_id: The conversation ID
            user_message_id: The user message ID to find the response to
            max_retries: Maximum number of retries
            
        Returns:
            Tuple containing:
                - Success status (bool)
                - Agent message ID if successful, None otherwise
                - Error dict if failed, None otherwise
        """
        conversation_messages_url = f"{self.config.domain}/api/v1/w/{self.config.workspace_id}/assistant/conversations/{conversation_id}/messages"
        headers = self.config.get_headers()
        
        logger.info(f"Getting conversation messages from: {conversation_messages_url}")
        
        # Special retrieval payload for retrieving messages
        retrieval_payload = {
            "content": "RETRIEVAL_QUERY",
            "mentions": [{
                "configurationId": self.config.agent_id,
                "context": {
                    "timezone": self.config.timezone,
                    "modelSettings": {"provider": "anthropic"}
                }
            }],
            "context": {
                "timezone": self.config.timezone,
                "username": "api_retrieval",
                "queryType": "history_analysis"
            }
        }
        
        logger.debug(self.format_as_curl(conversation_messages_url, "POST", headers, retrieval_payload))
        
        agent_message_id = None
        
        for attempt in range(max_retries):
            try:
                messages_response = requests.post(conversation_messages_url, headers=headers, json=retrieval_payload)
                messages_response.raise_for_status()
                messages_data = messages_response.json()
                
                # Extract messages array from response
                messages = []
                if "messages" in messages_data:
                    messages = messages_data["messages"]
                else:
                    error = self.handle_request_error(
                        "3", 
                        f"Unexpected response format: {json.dumps(messages_data)}", 
                        conversation_messages_url, "POST", headers, retrieval_payload
                    )
                    return False, None, error
                
                # Look for an agent message that came after our user message
                found = False
                for message in messages:
                    # First find our user message
                    if message.get("sId") == user_message_id:
                        found = True
                        continue
                    
                    # After finding user message, look for agent message
                    if found and message.get("author", {}).get("type") == "assistant":
                        agent_message_id = message.get("sId")
                        logger.info(f"Step 3: Found agent response with ID: {agent_message_id}")
                        break
                
                if agent_message_id:
                    return True, agent_message_id, None
                
                # Wait longer before trying again (increase from 1s to 2s)
                logger.debug(f"No agent message found yet, waiting before retry {attempt+1}")
                time.sleep(2)
                
            except requests.exceptions.RequestException as e:
                error = self.handle_request_error(
                    "3", 
                    f"Failed to get messages: {str(e)}", 
                    conversation_messages_url, "POST", headers, retrieval_payload
                )
                return False, None, error
        
        error_msg = f"Step 3: No agent message found after {max_retries} attempts"
        logger.warning(error_msg)
        logger.warning(f"Last curl command attempted: \n{self.format_as_curl(conversation_messages_url, 'POST', headers, retrieval_payload)}")
        return False, None, {"error": error_msg}
    
    def get_agent_response(self, conversation_id: str, agent_message_id: str, 
                          max_retries: int = 30) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """
        Get the content of an agent's message by polling for events.
        
        Args:
            conversation_id: The conversation ID
            agent_message_id: The agent message ID to get content for
            max_retries: Maximum number of retries
            
        Returns:
            Tuple containing:
                - Success status (bool)
                - Response content if successful, None otherwise
                - Error dict if failed, None otherwise
        """
        events_url = f"{self.config.domain}/api/v1/w/{self.config.workspace_id}/assistant/conversations/{conversation_id}/messages/{agent_message_id}/events"
        headers = self.config.get_headers(include_content_type=False)
        
        for attempt in range(max_retries):
            logger.debug(f"Polling for response (attempt {attempt+1}/{max_retries})...")
            logger.debug(self.format_as_curl(events_url, "GET", headers))
            
            try:
                events_response = requests.get(events_url, headers=headers)
                events_response.raise_for_status()
                events_data = events_response.json()
                
                # Extract events array from response
                events = []
                if "events" in events_data:
                    events = events_data["events"]
                else:
                    error = self.handle_request_error(
                        "4", 
                        f"Unexpected response format: {json.dumps(events_data)}", 
                        events_url, "GET", headers
                    )
                    return False, None, error
                
                completed = False
                full_content = []
                
                for event in events:
                    # We are looking for an event with a contentBlock
                    if "contentBlock" in event and "content" in event["contentBlock"]:
                        full_content.append(event["contentBlock"]["content"])
                    
                    # Check if the generation is completed
                    if event.get("type") == "generation-complete":
                        completed = True
                
                if completed:
                    # Join all content blocks into the response
                    response_content = "\n".join(full_content)
                    logger.info(f"Step 4: Received response: {response_content[:100]}...")
                    return True, response_content, None
                
                # Wait before trying again
                time.sleep(1)
                
            except requests.exceptions.RequestException as e:
                error = self.handle_request_error(
                    "4", 
                    f"Request error: {str(e)}", 
                    events_url, "GET", headers
                )
                return False, None, error
        
        # If we get here, we've timed out
        error_msg = f"Step 4: Timed out waiting for a response after {max_retries} attempts"
        logger.warning(error_msg)
        logger.warning(f"Last curl command attempted: \n{self.format_as_curl(events_url, 'GET', headers)}")
        return False, None, {"error": error_msg}
