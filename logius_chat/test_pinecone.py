import os
import sys
import logging
import traceback
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Try to import Pinecone
try:
    # Try the newer import style first
    try:
        from pinecone import Pinecone
        PINECONE_NEW_API = True
        logger.info("Successfully imported Pinecone (new API)")
    except ImportError:
        # Fall back to the older import style
        import pinecone
        PINECONE_NEW_API = False
        logger.info("Successfully imported Pinecone (old API)")
    
    PINECONE_AVAILABLE = True
except (ImportError, ModuleNotFoundError) as e:
    logger.error(f"Pinecone package not available or incompatible: {e}")
    logger.error(traceback.format_exc())
    PINECONE_AVAILABLE = False
    PINECONE_NEW_API = False

# Import embedding service
try:
    from model_layer.embedding_service import get_embedding
    logger.info("Successfully imported embedding service")
except Exception as e:
    logger.error(f"Error importing embedding service: {e}")
    logger.error(traceback.format_exc())

def test_pinecone_connection():
    """Test the connection to Pinecone."""
    if not PINECONE_AVAILABLE:
        logger.error("Pinecone package not available")
        return False
    
    api_key = os.environ.get("PINECONE_API_KEY")
    if not api_key:
        logger.error("PINECONE_API_KEY not found in environment variables")
        return False
    
    index_name = os.environ.get("PINECONE_INDEX_NAME")
    if not index_name:
        logger.error("PINECONE_INDEX_NAME not found in environment variables")
        return False
    
    environment = os.environ.get("PINECONE_ENVIRONMENT")
    if not environment and not PINECONE_NEW_API:
        logger.error("PINECONE_ENVIRONMENT not found in environment variables (required for old API)")
        return False
    
    try:
        logger.info(f"Connecting to Pinecone with API key: {api_key[:5]}...{api_key[-5:]}")
        
        if PINECONE_NEW_API:
            # New API style
            pc = Pinecone(api_key=api_key)
            logger.info("Successfully created Pinecone client (new API)")
            
            logger.info(f"Getting index: {index_name}")
            index = pc.Index(index_name)
            logger.info("Successfully got Pinecone index")
            
            # Get index stats
            stats = index.describe_index_stats()
            logger.info(f"Index stats: {stats}")
        else:
            # Old API style
            logger.info(f"Initializing Pinecone with environment: {environment}")
            pinecone.init(api_key=api_key, environment=environment)
            logger.info("Successfully initialized Pinecone (old API)")
            
            logger.info(f"Getting index: {index_name}")
            index = pinecone.Index(index_name)
            logger.info("Successfully got Pinecone index")
            
            # Get index stats
            stats = index.describe_index_stats()
            logger.info(f"Index stats: {stats}")
        
        return True
    except Exception as e:
        logger.error(f"Error connecting to Pinecone: {e}")
        logger.error(traceback.format_exc())
        return False

def test_pinecone_search(query="Wat is het beheermodel van de API Design Rules?"):
    """Test searching in Pinecone."""
    if not PINECONE_AVAILABLE:
        logger.error("Pinecone package not available")
        return
    
    api_key = os.environ.get("PINECONE_API_KEY")
    index_name = os.environ.get("PINECONE_INDEX_NAME")
    environment = os.environ.get("PINECONE_ENVIRONMENT")
    
    if not api_key or not index_name:
        logger.error("Pinecone API key or index name not found in environment variables")
        return
    
    if not environment and not PINECONE_NEW_API:
        logger.error("PINECONE_ENVIRONMENT not found in environment variables (required for old API)")
        return
    
    try:
        # Generate embedding for the query
        logger.info(f"Generating embedding for query: '{query}'")
        query_embedding = get_embedding(query)
        if not query_embedding:
            logger.error("Failed to generate embedding for query")
            return
        logger.info(f"Successfully generated embedding (dimension: {len(query_embedding)})")
        
        # Connect to Pinecone
        if PINECONE_NEW_API:
            # New API style
            pc = Pinecone(api_key=api_key)
            index = pc.Index(index_name)
        else:
            # Old API style
            pinecone.init(api_key=api_key, environment=environment)
            index = pinecone.Index(index_name)
        
        # Search in Pinecone
        logger.info("Searching in Pinecone...")
        
        if PINECONE_NEW_API:
            # New API style
            response = index.query(
                namespace="ns1",
                vector=query_embedding,
                top_k=10,
                include_metadata=True,
                include_values=False
            )
        else:
            # Old API style
            response = index.query(
                namespace="ns1",
                vector=query_embedding,
                top_k=10,
                include_metadata=True
            )
        
        # Process results
        if PINECONE_NEW_API:
            matches = response.matches
        else:
            matches = response.get('matches', [])
            
        if not matches:
            logger.warning("No matches found in Pinecone")
            return
        
        logger.info(f"Found {len(matches)} matches in Pinecone")
        for i, match in enumerate(matches[:5], 1):
            if PINECONE_NEW_API:
                match_id = match.id
                score = match.score if hasattr(match, 'score') else 'N/A'
                metadata = match.metadata if hasattr(match, 'metadata') else {}
            else:
                match_id = match.get('id', 'N/A')
                score = match.get('score', 'N/A')
                metadata = match.get('metadata', {})
            
            logger.info(f"Match {i}:")
            logger.info(f"  ID: {match_id}")
            logger.info(f"  Score: {score}")
            logger.info(f"  Metadata: {metadata}")
        
    except Exception as e:
        logger.error(f"Error searching in Pinecone: {e}")
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    # Test Pinecone connection
    print("=" * 80)
    print("TESTING PINECONE CONNECTION")
    print("=" * 80)
    
    if test_pinecone_connection():
        print("\n" + "=" * 80)
        print("TESTING PINECONE SEARCH")
        print("=" * 80)
        
        # Test query
        test_query = "Wat is het beheermodel van de API Design Rules?"
        test_pinecone_search(test_query)
    else:
        print("Skipping search test due to connection failure") 