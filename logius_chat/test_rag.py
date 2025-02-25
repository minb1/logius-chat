import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(str(Path(__file__).resolve().parent))

# Load environment variables
load_dotenv()

# Import the necessary modules
from model_layer.embedding_service import get_embedding
from context_layer.pinecone_service import search_similar_documents, get_chunk_content, get_chunks_for_display
from model_layer.gemini_service import generate_response
from prompt_layer.base_template import create_prompt

def test_rag_pipeline(query):
    """
    Test the RAG pipeline with a given query.
    
    Args:
        query (str): The query to test
    """
    print(f"Testing RAG pipeline with query: '{query}'")
    print("-" * 80)
    
    # Step 1: Generate embeddings
    print("\n1. Generating embeddings...")
    query_embedding = get_embedding(query)
    if not query_embedding:
        print("Failed to generate embeddings.")
        return
    print(f"Successfully generated embeddings (dimension: {len(query_embedding)})")
    
    # Step 2: Search for similar documents
    print("\n2. Searching for similar documents...")
    chunk_paths = search_similar_documents(query_embedding, top_k=10)
    if not chunk_paths:
        print("No similar documents found.")
        return
    print(f"Found {len(chunk_paths)} similar documents:")
    for i, path in enumerate(chunk_paths[:5]):
        print(f"  {i+1}. {path}")
    if len(chunk_paths) > 5:
        print(f"  ... and {len(chunk_paths) - 5} more")
    
    # Step 3: Get chunk content for prompt
    print("\n3. Getting chunk content for prompt...")
    context = get_chunk_content(chunk_paths)
    if context == "No relevant content found.":
        print("No content could be retrieved from the chunks.")
        return
    print("Successfully retrieved context:")
    print("-" * 40)
    print(context[:500] + "..." if len(context) > 500 else context)
    print("-" * 40)
    
    # Step 4: Get chunks for display
    print("\n4. Getting chunks for display...")
    chunks = get_chunks_for_display(chunk_paths)
    print(f"Prepared {len(chunks)} chunks for display:")
    for i, chunk in enumerate(chunks[:3]):
        print(f"  {i+1}. {chunk['title']} ({chunk['id']})")
        print(f"     Content preview: {chunk['content'][:100]}...")
    if len(chunks) > 3:
        print(f"  ... and {len(chunks) - 3} more")
    
    # Step 5: Create prompt
    print("\n5. Creating prompt...")
    prompt = create_prompt(query, context)
    print("Prompt created successfully.")
    
    # Step 6: Generate response
    print("\n6. Generating response...")
    response = generate_response(prompt)
    print("Response generated successfully:")
    print("-" * 40)
    print(response)
    print("-" * 40)
    
    print("\nRAG pipeline test completed successfully!")

if __name__ == "__main__":
    # Test query
    test_query = "Wat is het beheermodel van de API Design Rules?"
    
    # Run the test
    test_rag_pipeline(test_query) 