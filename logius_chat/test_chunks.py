import os
from dotenv import load_dotenv
from model_layer.embedding_service import get_embedding
from context_layer.pinecone_service import search_similar_documents, get_chunk_content

# Load environment variables
load_dotenv()

def test_chunk_retrieval(query):
    """
    Test the chunk retrieval process.
    
    Args:
        query (str): The test query
    """
    print(f"Testing chunk retrieval for query: '{query}'")
    
    # Step 1: Generate embeddings for the query
    print("\nStep 1: Generating embeddings...")
    query_embedding = get_embedding(query)
    if not query_embedding:
        print("Failed to generate embeddings for your query.")
        return
    
    print(f"Embedding generated successfully (length: {len(query_embedding)})")
    
    # Step 2: Search for similar documents in Pinecone
    print("\nStep 2: Searching for similar documents...")
    chunk_paths = search_similar_documents(query_embedding)
    if not chunk_paths:
        print("No relevant documentation found for your query.")
        return
    
    print(f"Found {len(chunk_paths)} relevant chunks:")
    for i, path in enumerate(chunk_paths, 1):
        print(f"  {i}. {path}")
    
    # Step 3: Get the content of the retrieved chunks
    print("\nStep 3: Retrieving chunk content...")
    context = get_chunk_content(chunk_paths)
    
    print(f"\nRetrieved content (first 500 chars):")
    print(context[:500] + "..." if len(context) > 500 else context)

if __name__ == "__main__":
    test_query = "How do I create a new branch in Git?"
    test_chunk_retrieval(test_query) 