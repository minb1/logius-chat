from model_layer.embedding_service import get_embedding
from context_layer.pinecone_service import search_similar_documents, get_chunk_content
from context_layer.redis_service import log_message, format_chat_history_for_prompt
from model_layer.gemini_service import generate_response
from prompt_layer.base_template import create_prompt
import os
from pathlib import Path

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
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
                # Get the filename without extension
                filename = os.path.basename(path)
                # Get the relative path for display
                rel_path = os.path.relpath(path, Path(__file__).resolve().parent.parent)
                chunks.append({
                    "id": filename,
                    "title": filename,
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