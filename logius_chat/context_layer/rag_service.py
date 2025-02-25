from model_layer.embedding_service import get_embedding
from context_layer.pinecone_service import search_similar_documents, get_chunk_content, get_chunks_for_display
from context_layer.redis_service import log_message, format_chat_history_for_prompt
from model_layer.gemini_service import generate_response
from prompt_layer.base_template import create_prompt
import os
from pathlib import Path

# Get base directory
BASE_DIR = Path(__file__).resolve().parent.parent
CHUNKS_DIR = os.path.join(BASE_DIR, 'data', 'chunks')

def process_query(query, chat_id=None):
    """
    Process a user query through the RAG pipeline.
    
    Args:
        query (str): The user's query
        chat_id (str, optional): The chat session ID for history tracking
        
    Returns:
        dict: Dictionary containing the response and retrieved chunks
    """
    print(f"Processing query: {query}")
    
    # Step 1: Generate embeddings for the query
    query_embedding = get_embedding(query)
    if not query_embedding:
        print("Failed to generate embeddings")
        return {"response": "Failed to generate embeddings for your query.", "chunks": []}
    
    # Step 2: Search for similar documents in Pinecone
    chunk_paths = search_similar_documents(query_embedding, top_k=50)
    if not chunk_paths:
        print("No relevant documents found")
        return {"response": "No relevant documentation found for your query.", "chunks": []}
    print(f"Found {len(chunk_paths)} relevant documents")
    
    # Step 3: Get the content of the retrieved chunks for the prompt
    context = get_chunk_content(chunk_paths)
    if context == "No relevant content found.":
        print("No content could be retrieved from the chunks")
        return {"response": "No relevant content could be retrieved for your query.", "chunks": []}
    print("Successfully retrieved context for prompt")
    
    # Step 4: Prepare chunks for the frontend display
    chunks = get_chunks_for_display(chunk_paths)
    print(f"Prepared {len(chunks)} chunks for display")
    
    # Step 5: Get chat history if chat_id is provided
    chat_history = ""
    if chat_id:
        chat_history = format_chat_history_for_prompt(chat_id)
        print("Retrieved chat history for context")
    
    # Step 6: Create the prompt with the context and chat history
    prompt = create_prompt(query, context, chat_history)
    print("Created prompt with context and chat history")
    
    # Step 7: Generate a response using Gemini
    response = generate_response(prompt)
    print("Generated response from Gemini")
    
    # Step 8: Log the interaction to Redis if chat_id is provided
    if chat_id:
        # Log user query
        log_message(chat_id, "user", query)
        # Log assistant response
        log_message(chat_id, "assistant", response)
        print("Logged interaction to Redis")
    
    return {
        "response": response,
        "chunks": chunks
    } 