from model_layer.embedding_service import get_embedding
from context_layer.pinecone_service import search_similar_documents, get_chunk_content
from context_layer.redis_service import log_message, format_chat_history_for_prompt
from model_layer.gemini_service import generate_response
from prompt_layer.base_template import create_prompt
import os
from pathlib import Path

# Get base directory
BASE_DIR = Path(__file__).resolve().parent.parent
CHUNKS_DIR = os.path.join(BASE_DIR, 'data', 'chunks')

def process_query(query, chat_id=None):
    print("Processing query: ", query)
    """
    Process a user query through the RAG pipeline.
    
    Args:
        query (str): The user's query
        chat_id (str, optional): The chat session ID for history tracking
        
    Returns:
        dict: Dictionary containing the response and retrieved chunks
    """
    # Step 1: Generate embeddings for the query
    query_embedding = get_embedding(query)
    if not query_embedding:
        return {"response": "Failed to generate embeddings for your query.", "chunks": []}
    
    # Step 2: Search for similar documents in Pinecone
    chunk_paths = search_similar_documents(query_embedding)
    if not chunk_paths:
        return {"response": "No relevant documentation found for your query.", "chunks": []}
    print("Step 2 completed successfully")
    
    # Step 3: Get the content of the retrieved chunks
    context = get_chunk_content(chunk_paths)
    print("Step 3 completed successfully")
    
    # Prepare chunks for the frontend
    chunks = []
    for path in chunk_paths:
        try:
            # Convert to Path object to handle different OS path formats
            path_obj = Path(path)
            
            # Check if the path exists directly
            if path_obj.exists():
                file_path = path_obj
            else:
                # Try to find the file in chunks directory by name
                filename = path_obj.name
                chunk_path = Path(CHUNKS_DIR) / filename
                
                if chunk_path.exists():
                    file_path = chunk_path
                else:
                    # Search for the file in chunks directory
                    for root, dirs, files in os.walk(CHUNKS_DIR):
                        if filename in files:
                            file_path = Path(root) / filename
                            break
                    else:
                        print(f"Warning: Chunk file not found: {path}")
                        continue
            
            # Read the content
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
                # Get the filename without extension
                filename = file_path.name
                
                # Create a more readable title from the path
                # Extract document name and section from path
                parts = file_path.parts
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
                    "content": content
                })
        except Exception as e:
            print(f"Error reading chunk file {path}: {e}")
    
    # Step 4: Get chat history if chat_id is provided
    chat_history = ""
    if chat_id:
        chat_history = format_chat_history_for_prompt(chat_id)
    
    # Step 5: Create the prompt with the context and chat history
    prompt = create_prompt(query, context, chat_history)
    print("Step 4 completed successfully")
    
    # Step 6: Generate a response using Gemini
    response = generate_response(prompt)
    print("Step 5 completed successfully")
    
    # Step 7: Log the interaction to Redis if chat_id is provided
    if chat_id:
        # Log user query
        log_message(chat_id, "user", query)
        # Log assistant response
        log_message(chat_id, "assistant", response)
    
    return {
        "response": response,
        "chunks": chunks
    } 