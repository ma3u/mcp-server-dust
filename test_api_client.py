#!/usr/bin/env python3
"""
Test script for the Dust API Client.

This script tests the message retrieval functionality of the DustAPIClient
to verify that the message extraction logic works correctly.
"""

import logging
import json
import time
from config import DustAgentConfig
from api_client import DustAPIClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [dust-test] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S.%fZ'
)
logger = logging.getLogger("dust-test")

def test_message_retrieval():
    """
    Test message retrieval functionality.
    
    This function tests the complete flow:
    1. Creating a conversation
    2. Sending a message
    3. Getting the agent's response message ID
    4. Getting the full agent response content
    """
    # Create API client with config
    config = DustAgentConfig()
    api_client = DustAPIClient(config)
    
    # Step 1: Create a new conversation
    query = "Can you explain how the Dust API works with message retrieval?"
    logger.info(f"Creating new conversation with query: {query}")
    success, conversation_id, error = api_client.create_conversation(query)
    
    if not success:
        logger.error(f"Failed to create conversation: {error}")
        return
    
    logger.info(f"Successfully created conversation with ID: {conversation_id}")
    
    # Step 2: Send a message
    logger.info(f"Sending message in conversation: {conversation_id}")
    success, user_message_id, error = api_client.send_message(conversation_id, query)
    
    if not success:
        logger.error(f"Failed to send message: {error}")
        return
    
    logger.info(f"Successfully sent message with ID: {user_message_id}")
    
    # Step 3: Get the agent's response message ID
    logger.info(f"Getting agent message ID for conversation: {conversation_id}, user message: {user_message_id}")
    success, agent_message_id, error = api_client.get_agent_message(conversation_id, user_message_id, query)
    
    if not success:
        logger.error(f"Failed to get agent message ID: {error}")
        return
    
    logger.info(f"Successfully got agent message ID: {agent_message_id}")
    
    # Step 4: Get the full agent response content
    logger.info(f"Getting agent response content for message: {agent_message_id}")
    success, response_content, error = api_client.get_agent_response(conversation_id, agent_message_id)
    
    if not success:
        logger.error(f"Failed to get agent response content: {error}")
        return
    
    logger.info(f"Successfully got agent response content:")
    logger.info(f"Response length: {len(response_content)}")
    logger.info(f"Response preview: {response_content[:200]}...")
    
    logger.info("Test completed successfully!")

if __name__ == "__main__":
    logger.info("Starting API client message retrieval test")
    test_message_retrieval()
