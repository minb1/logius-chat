import os
from pinecone import Pinecone
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Get base directory
BASE_DIR = Path(__file__).resolve().parent.parent
CHUNKS_DIR = os.path.join(BASE_DIR, 'data', 'chunks')

# Get API keys
pinecone_api_key = os.getenv("PINECONE_API_KEY")
pinecone_environment = os.getenv("PINECONE_ENVIRONMENT")

if not pinecone_api_key or not pinecone_environment:
    print("WARNING: PINECONE_API_KEY or PINECONE_ENVIRONMENT not found in environment variables. Please set them in your .env file.")
# Initialize Pinecone if API keys are available
index = None
if pinecone_api_key and pinecone_environment:
    try:
        pinecone = Pinecone(api_key=pinecone_api_key)
        # Get the Pinecone index
        index = pinecone.Index(pinecone_environment)
    except Exception as e:
        print(f"Error initializing Pinecone: {e}")

def search_similar_documents(query_embedding, top_k=20):
    """
    Search Pinecone for documents similar to the query embedding.
    
    Args:
        query_embedding (list): The embedding vector of the query
        top_k (int): Number of similar documents to retrieve
        
    Returns:
        list: List of file paths to the most similar document chunks
    """
    if not index:
        print("Error: Pinecone index not initialized. Missing API keys.")
        return []
        
    try:
        response = index.query(
            namespace="ns1",
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            include_values=False
        )
        
        # Extract chunk IDs from the matches
        chunk_ids = [match["metadata"].get("chunk_id") for match in response["matches"] if match["metadata"].get("chunk_id")]
        
        # If no chunk_id is found, try file_path
        if not chunk_ids:
            return [match["metadata"].get("file_path") for match in response["matches"] if match["metadata"].get("file_path")]
        
        # Convert chunk IDs to actual file paths in the data/chunks directory
        return [os.path.join(CHUNKS_DIR, f"{chunk_id}.txt") for chunk_id in chunk_ids]
    except Exception as e:
        print(f"Error searching Pinecone: {e}")
        return []

def get_chunk_content(file_paths):
    """
    Read the content of chunk files.
    
    Args:
        file_paths (list): List of file paths to chunk files
        
    Returns:
        str: Concatenated content of all chunks
    """
    content = []
    
    for path in file_paths:
        try:
            # Check if the path is absolute or relative
            if not os.path.isabs(path):
                # If it's a relative path, try to find it in the data/chunks directory
                # First, get just the filename part (e.g., "chunk_001.txt")
                filename = os.path.basename(path)
                # Get the subdirectory structure (e.g., "Logius-standaarden_API-Standaarden-Beheermodel/ch06_Communicatie")
                subdir = os.path.dirname(path)
                # Construct the full path in data/chunks
                chunk_path = os.path.join(CHUNKS_DIR, subdir, filename)
                if os.path.exists(chunk_path):
                    path = chunk_path
            
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as file:
                    content.append(file.read())
            else:
                print(f"Warning: Chunk file not found: {path}")
        except Exception as e:
            print(f"Error reading chunk file {path}: {e}")
    
    if not content:
        return "No relevant content found."
        
    return "\n\n".join(content) 