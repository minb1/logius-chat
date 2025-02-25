import os
import sys
import django
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logius_chat.settings')
django.setup()

# Import Django models
from documents.models import Document, Chunk

# Import RAG services
from model_layer.embedding_service import get_embedding
from context_layer.pinecone_service import search_similar_documents, get_chunk_content, get_chunks_for_display
from prompt_layer.base_template import create_prompt
from model_layer.gemini_service import generate_response

def test_database_stats():
    """
    Print statistics about the database.
    """
    total_documents = Document.objects.count()
    total_chunks = Chunk.objects.count()
    chunks_with_embeddings = Chunk.objects.exclude(embedding__isnull=True).count()
    
    print(f"Total documents: {total_documents}")
    print(f"Total chunks: {total_chunks}")
    
    if total_chunks > 0:
        embedding_coverage = (chunks_with_embeddings / total_chunks) * 100
        print(f"Chunks with embeddings: {chunks_with_embeddings} ({embedding_coverage:.2f}%)")
    else:
        print("No chunks found in the database.")

def test_rag_pipeline(query):
    """
    Test the RAG pipeline with a given query.
    
    Args:
        query (str): The query to test
    """
    print(f"\nTesting RAG pipeline with query: '{query}'")
    
    # Step 1: Generate embeddings
    print("\n1. Generating embeddings...")
    embedding = get_embedding(query)
    if embedding:
        print(f"✓ Successfully generated embeddings (dimension: {len(embedding)})")
    else:
        print("✗ Failed to generate embeddings")
        return
    
    # Step 2: Search for similar documents
    print("\n2. Searching for similar documents...")
    chunk_ids = search_similar_documents(embedding, top_k=10)
    if chunk_ids:
        print(f"✓ Found {len(chunk_ids)} similar documents")
        print(f"  First few chunk IDs: {chunk_ids[:3]}")
    else:
        print("✗ No similar documents found")
        return
    
    # Step 3: Get chunk content for prompt
    print("\n3. Getting chunk content for prompt...")
    context = get_chunk_content(chunk_ids)
    if context:
        print(f"✓ Successfully retrieved context ({len(context)} characters)")
        print(f"  Preview: {context[:100]}...")
    else:
        print("✗ Failed to retrieve context")
        return
    
    # Step 4: Get chunks for display
    print("\n4. Getting chunks for display...")
    chunks = get_chunks_for_display(chunk_ids)
    if chunks:
        print(f"✓ Prepared {len(chunks)} chunks for display")
        for i, chunk in enumerate(chunks[:3], 1):
            print(f"  Chunk {i}: {chunk['title']} - {chunk['content'][:50]}...")
    else:
        print("✗ Failed to prepare chunks for display")
    
    # Step 5: Create prompt
    print("\n5. Creating prompt...")
    prompt = create_prompt(query, context)
    if prompt:
        print("✓ Successfully created prompt")
        print(f"  Prompt length: {len(prompt)} characters")
    else:
        print("✗ Failed to create prompt")
        return
    
    # Step 6: Generate response
    print("\n6. Generating response...")
    response = generate_response(prompt)
    if response:
        print("✓ Successfully generated response")
        print("\nResponse:")
        print("-" * 80)
        print(response)
        print("-" * 80)
    else:
        print("✗ Failed to generate response")

if __name__ == "__main__":
    # Test database statistics
    print("=" * 80)
    print("DATABASE STATISTICS")
    print("=" * 80)
    test_database_stats()
    
    # Test RAG pipeline
    print("\n" + "=" * 80)
    print("RAG PIPELINE TEST")
    print("=" * 80)
    
    # Define a test query
    test_query = "Wat is het beheermodel van de API Design Rules?"
    
    # Run the test
    test_rag_pipeline(test_query) 