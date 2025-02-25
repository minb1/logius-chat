import redis
import json
import uuid
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Redis connection
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    decode_responses=True,
    username=os.getenv('REDIS_USERNAME'),
    password=os.getenv('REDIS_PASSWORD'),
)

def create_chat_session():
    """
    Create a new chat session with a unique ID and 24-hour TTL
    
    Returns:
        str: The unique chat session ID
    """
    chat_id = str(uuid.uuid4())
    # Store creation timestamp
    redis_client.hset(f"chat:{chat_id}", "created_at", datetime.now().isoformat())
    
    # Set TTL for both the chat metadata and messages (e.g., 24 hours = 86400 seconds)
    redis_client.expire(f"chat:{chat_id}", 1800)
    redis_client.expire(f"chat:{chat_id}:messages", 1800)
    
    return chat_id

def log_message(chat_id, role, content):
    """
    Log a message to the chat history.
    
    Args:
        chat_id (str): The chat session ID
        role (str): The role of the message sender ('user' or 'assistant')
        content (str): The message content
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create a message object
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add message to the chat history list
        redis_client.rpush(f"chat:{chat_id}:messages", json.dumps(message))
        return True
    except Exception as e:
        print(f"Error logging message to Redis: {e}")
        return False

def get_chat_history(chat_id):
    """
    Retrieve the chat history for a given chat session.
    
    Args:
        chat_id (str): The chat session ID
    
    Returns:
        list: List of message objects with role and content
    """
    try:
        # Get all messages from the chat history list
        messages_json = redis_client.lrange(f"chat:{chat_id}:messages", 0, -1)
        
        # Parse JSON messages
        messages = [json.loads(msg) for msg in messages_json]
        return messages
    except Exception as e:
        print(f"Error retrieving chat history from Redis: {e}")
        return []

def format_chat_history_for_prompt(chat_id):
    """
    Format the chat history for inclusion in the prompt.
    
    Args:
        chat_id (str): The chat session ID
    
    Returns:
        str: Formatted chat history for the prompt
    """
    messages = get_chat_history(chat_id)
    
    if not messages:
        return ""
    
    formatted_history = "Previous conversation:\n\n"
    
    for msg in messages:
        role = "User" if msg["role"] == "user" else "Assistant"
        formatted_history += f"{role}: {msg['content']}\n\n"
    
    return formatted_history
