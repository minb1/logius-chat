import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).resolve().parent))

# Try importing the required modules, with fallbacks
try:
    from context_layer.pinecone_service import search_similar_documents, get_chunk_content
    from model_layer.embedding_service import get_embedding
    pinecone_available = True
except ImportError as e:
    print(f"Warning: Could not import required modules: {e}")
    print("Will run in limited test mode.")
    pinecone_available = False

def test_file_paths():
    """Test file path handling without using Pinecone or embeddings"""
    # Get base directory
    BASE_DIR = Path(__file__).resolve().parent
    CHUNKS_DIR = os.path.join(BASE_DIR, 'data', 'chunks')
    
    print(f"Base directory: {BASE_DIR}")
    print(f"Chunks directory: {CHUNKS_DIR}")
    
    # Check if chunks directory exists
    if not os.path.exists(CHUNKS_DIR):
        print(f"Creating chunks directory: {CHUNKS_DIR}")
        os.makedirs(CHUNKS_DIR, exist_ok=True)
    
    # List files in chunks directory
    print("\nListing files in chunks directory:")
    chunk_files = list(Path(CHUNKS_DIR).glob('**/*.txt'))
    
    if not chunk_files:
        print("No chunk files found. Creating a sample chunk file for testing.")
        # Create a sample chunk file for testing
        sample_chunk_path = os.path.join(CHUNKS_DIR, 'sample_chunk.txt')
        with open(sample_chunk_path, 'w', encoding='utf-8') as f:
            f.write("This is a sample chunk for testing purposes.\n")
            f.write("It contains information about Git commands.\n")
            f.write("Git is a distributed version control system.\n")
        print(f"Created a sample chunk file at {sample_chunk_path}")
        chunk_files = [Path(sample_chunk_path)]
    
    print(f"Found {len(chunk_files)} chunk files:")
    for i, file_path in enumerate(chunk_files[:10]):  # Show only first 10 files
        print(f"  {i+1}. {file_path}")
    
    if len(chunk_files) > 10:
        print(f"  ... and {len(chunk_files) - 10} more files")
    
    # Test reading chunk files directly
    print("\nTesting direct file reading:")
    for file_path in chunk_files[:3]:  # Test first 3 files
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"Successfully read file: {file_path}")
                print(f"Content preview: {content[:100]}...")
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")

def test_chunk_retrieval():
    """Test the chunk retrieval process using Pinecone and embeddings"""
    if not pinecone_available:
        print("Skipping full chunk retrieval test as required modules are not available.")
        return
        
    # Get base directory
    BASE_DIR = Path(__file__).resolve().parent
    CHUNKS_DIR = os.path.join(BASE_DIR, 'data', 'chunks')
    
    # List files in chunks directory
    chunk_files = list(Path(CHUNKS_DIR).glob('**/*.txt'))
    
    # Test embedding generation
    print("\nTesting embedding generation:")
    query = "How do I use Git?"
    query_embedding = get_embedding(query)
    
    if query_embedding:
        print(f"Successfully generated embedding for query: '{query}'")
        print(f"Embedding dimension: {len(query_embedding)}")
    else:
        print("Failed to generate embedding for query.")
        return
    
    # Test document search
    print("\nTesting document search:")
    chunk_paths = search_similar_documents(query_embedding)
    
    if chunk_paths:
        print(f"Found {len(chunk_paths)} similar documents:")
        for i, path in enumerate(chunk_paths[:5]):  # Show only first 5 paths
            print(f"  {i+1}. {path}")
        
        if len(chunk_paths) > 5:
            print(f"  ... and {len(chunk_paths) - 5} more paths")
    else:
        print("No similar documents found.")
        # Use the sample chunk files we found earlier
        chunk_paths = [str(path) for path in chunk_files[:5]]
        print(f"Using {len(chunk_paths)} sample chunk files for testing:")
        for i, path in enumerate(chunk_paths):
            print(f"  {i+1}. {path}")
    
    # Test chunk content retrieval
    print("\nTesting chunk content retrieval:")
    content = get_chunk_content(chunk_paths)
    
    if content and content != "No relevant content found.":
        print("Successfully retrieved chunk content:")
        print("-" * 50)
        print(content[:500] + "..." if len(content) > 500 else content)
        print("-" * 50)
    else:
        print("Failed to retrieve chunk content or no content found.")

if __name__ == "__main__":
    # Always run the file path test
    test_file_paths()
    
    # Try to run the full test if possible
    if pinecone_available:
        print("\n" + "="*50)
        print("Running full chunk retrieval test")
        print("="*50)
        test_chunk_retrieval() 