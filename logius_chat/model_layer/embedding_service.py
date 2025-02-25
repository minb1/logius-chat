import os
import asyncio
from google import genai
from google.generativeai import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create a new event loop for the current thread
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# Initialize the Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def get_embedding(text):
    """
    Generate embeddings for the given text using Gemini's text-embedding-004 model.
    
    Args:
        text (str): The text to embed
        
    Returns:
        list: The embedding vector
    """
    if not client:
        print("Error: Gemini client not initialized. Missing API key.")
        return None
        
    try:
        result = client.models.embed_content(
            model="text-embedding-004",
            contents=text
        )
        return result.embeddings[0].values
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None
