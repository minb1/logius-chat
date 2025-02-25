import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Get base directory
BASE_DIR = Path(__file__).resolve().parent.parent
CHUNKS_DIR = os.path.join(BASE_DIR, 'data', 'chunks')

# Try to import Pinecone
try:
    from pinecone import Pinecone
    pinecone_available = True
except ImportError:
    print("WARNING: Pinecone package not available or incompatible version. Using fallback mode.")
    pinecone_available = False

# Get API keys
pinecone_api_key = os.getenv("PINECONE_API_KEY")
pinecone_environment = os.getenv("PINECONE_ENVIRONMENT")

if not pinecone_api_key or not pinecone_environment:
    print("WARNING: PINECONE_API_KEY or PINECONE_ENVIRONMENT not found in environment variables. Please set them in your .env file.")

# Initialize Pinecone if API keys are available
index = None
if pinecone_available and pinecone_api_key and pinecone_environment:
    try:
        pinecone = Pinecone(api_key=pinecone_api_key)
        # Get the Pinecone index
        index = pinecone.Index(pinecone_environment)
    except Exception as e:
        print(f"Error initializing Pinecone: {e}")

def search_similar_documents(query_embedding, top_k=50):
    """
    Search Pinecone for documents similar to the query embedding.
    
    Args:
        query_embedding (list): The embedding vector of the query
        top_k (int): Number of similar documents to retrieve
        
    Returns:
        list: List of file paths to the most similar document chunks
    """
    if not pinecone_available:
        print("Warning: Pinecone is not available. No context will be used.")
        return []
        
    if not index:
        print("Error: Pinecone index not initialized. Missing API keys.")
        return []
        
    try:
        # Query Pinecone with the embedding
        response = index.query(
            namespace="ns1",
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            include_values=False
        )
        
        # Extract file paths from the matches, handling both chunk_id and file_path metadata
        file_paths = []
        for match in response["matches"]:
            if "metadata" in match:
                # Try to get file_path first
                if "file_path" in match["metadata"] and match["metadata"]["file_path"]:
                    file_path = match["metadata"]["file_path"]
                    # Normalize path separators
                    file_path = file_path.replace("\\", "/")
                    file_paths.append(file_path)
                # If no file_path, try chunk_id
                elif "chunk_id" in match["metadata"] and match["metadata"]["chunk_id"]:
                    chunk_id = match["metadata"]["chunk_id"]
                    file_path = f"{chunk_id}.txt"
                    file_paths.append(file_path)
        
        return file_paths
    except Exception as e:
        print(f"Error searching Pinecone: {e}")
        return []

def get_chunk_content(file_paths):
    """
    Read the content of chunk files for prompt context.
    
    Args:
        file_paths (list): List of file paths to chunk files
        
    Returns:
        str: Concatenated content of all chunks with proper formatting
    """
    content = []
    seen_content = set()  # To avoid duplicate content
    
    for path in file_paths:
        try:
            # Normalize path separators
            normalized_path = path.replace("\\", "/")
            
            # Try different ways to find the file
            file_content = None
            
            # 1. Try direct path in chunks directory
            full_path = os.path.join(CHUNKS_DIR, normalized_path)
            if os.path.exists(full_path):
                with open(full_path, 'r', encoding='utf-8') as file:
                    file_content = file.read().strip()
            
            # 2. Try with just the filename
            if not file_content:
                filename = os.path.basename(normalized_path)
                chunk_path = os.path.join(CHUNKS_DIR, filename)
                if os.path.exists(chunk_path):
                    with open(chunk_path, 'r', encoding='utf-8') as file:
                        file_content = file.read().strip()
            
            # 3. Search recursively through chunks directory
            if not file_content:
                filename = os.path.basename(normalized_path)
                for root, dirs, files in os.walk(CHUNKS_DIR):
                    if filename in files:
                        full_path = os.path.join(root, filename)
                        with open(full_path, 'r', encoding='utf-8') as file:
                            file_content = file.read().strip()
                        break
            
            # Add content if found and not a duplicate
            if file_content and file_content not in seen_content:
                seen_content.add(file_content)
                content.append(file_content)
                
        except Exception as e:
            print(f"Error reading chunk file {path}: {e}")
    
    if not content:
        return "No relevant content found."
        
    # Join chunks with clear separation
    return "\n\n---\n\n".join(content)

def get_chunks_for_display(file_paths):
    """
    Read the content of chunk files for display in the UI.
    
    Args:
        file_paths (list): List of file paths to chunk files
        
    Returns:
        list: List of dictionaries with chunk information
    """
    chunks = []
    seen_paths = set()  # To avoid duplicate chunks
    
    for path in file_paths:
        try:
            # Skip if we've already processed this path
            if path in seen_paths:
                continue
            seen_paths.add(path)
            
            # Normalize path separators
            normalized_path = path.replace("\\", "/")
            
            # Try different ways to find the file
            file_path = None
            file_content = None
            
            # 1. Try direct path in chunks directory
            full_path = os.path.join(CHUNKS_DIR, normalized_path)
            if os.path.exists(full_path):
                file_path = full_path
                with open(file_path, 'r', encoding='utf-8') as file:
                    file_content = file.read()
            
            # 2. Try with just the filename
            if not file_content:
                filename = os.path.basename(normalized_path)
                chunk_path = os.path.join(CHUNKS_DIR, filename)
                if os.path.exists(chunk_path):
                    file_path = chunk_path
                    with open(file_path, 'r', encoding='utf-8') as file:
                        file_content = file.read()
            
            # 3. Search recursively through chunks directory
            if not file_content:
                filename = os.path.basename(normalized_path)
                for root, dirs, files in os.walk(CHUNKS_DIR):
                    if filename in files:
                        file_path = os.path.join(root, filename)
                        with open(file_path, 'r', encoding='utf-8') as file:
                            file_content = file.read()
                        break
            
            # Add chunk if found
            if file_path and file_content:
                # Create a Path object for easier path manipulation
                path_obj = Path(file_path)
                
                # Get the filename
                filename = path_obj.name
                
                # Create a more readable title from the path
                parts = path_obj.parts
                doc_name = None
                section = None
                
                # Look for document name pattern (usually contains underscore)
                for part in parts:
                    if '_' in part and not part.startswith('chunk_'):
                        doc_name = part.replace('_', ' ').replace('-', ' ')
                        break
                
                # Look for chapter/section pattern
                for part in parts:
                    if part.startswith('ch') and len(part) > 2:
                        section = part.replace('_', ' ')
                        break
                
                # Create a readable title
                if doc_name and section:
                    title = f"{doc_name} - {section}"
                elif doc_name:
                    title = doc_name
                else:
                    title = filename
                
                # Get the relative path for display
                try:
                    rel_path = os.path.relpath(file_path, BASE_DIR)
                except ValueError:
                    # Handle case where paths are on different drives
                    rel_path = str(file_path)
                
                chunks.append({
                    "id": filename,
                    "title": title,
                    "path": rel_path,
                    "content": file_content
                })
                
        except Exception as e:
            print(f"Error processing chunk file {path}: {e}")
    
    return chunks 