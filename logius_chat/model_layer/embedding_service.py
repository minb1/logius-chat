import os
import asyncio
import logging
import numpy as np
from google import genai
from google.generativeai import types
from dotenv import load_dotenv

# Set up logging
logger = logging.getLogger(__name__)

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
        logger.error("Gemini client not initialized. Missing API key.")
        return None
        
    try:
        result = client.models.embed_content(
            model="text-embedding-004",
            contents=text
        )
        return result.embeddings[0].values
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        return None

def generate_embeddings_for_chunk(chunk):
    """
    Generate embeddings for a chunk and save them to the database.
    
    Args:
        chunk: The Chunk model instance
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Check if the chunk already has an embedding
        if chunk.embedding is not None:
            logger.info(f"Chunk {chunk.chunk_id} already has an embedding")
            return True
        
        # Generate embedding
        embedding = get_embedding(chunk.content)
        if embedding is None:
            logger.error(f"Failed to generate embedding for chunk {chunk.chunk_id}")
            return False
        
        # Convert embedding to a format that can be stored in the database
        # This depends on how your Chunk model stores embeddings
        # For PostgreSQL with JSONField:
        chunk.embedding = embedding
        
        # Save the chunk
        chunk.save()
        
        logger.info(f"Successfully generated and saved embedding for chunk {chunk.chunk_id}")
        return True
    except Exception as e:
        logger.exception(f"Error generating embedding for chunk {chunk.chunk_id}: {e}")
        return False

def cosine_similarity(vec1, vec2):
    """
    Calculate cosine similarity between two vectors.
    
    Args:
        vec1 (list): First vector
        vec2 (list): Second vector
        
    Returns:
        float: Cosine similarity score
    """
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    
    dot_product = np.dot(vec1, vec2)
    norm_vec1 = np.linalg.norm(vec1)
    norm_vec2 = np.linalg.norm(vec2)
    
    if norm_vec1 == 0 or norm_vec2 == 0:
        return 0
    
    return dot_product / (norm_vec1 * norm_vec2)
