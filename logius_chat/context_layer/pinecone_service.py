import os
import json
from pathlib import Path
import logging
import traceback
from django.conf import settings
from django.db.models import Q

# Set up logging
logger = logging.getLogger(__name__)

# Try to import Pinecone, but don't fail if it's not available
try:
    # Try the newer import style first
    try:
        from pinecone import Pinecone, ServerlessSpec
        PINECONE_NEW_API = True
        logger.info("Successfully imported Pinecone (new API)")
    except ImportError:
        # Fall back to the older import style
        import pinecone
        PINECONE_NEW_API = False
        logger.info("Successfully imported Pinecone (old API)")
    
    PINECONE_AVAILABLE = True
except (ImportError, ModuleNotFoundError) as e:
    logger.warning(f"Pinecone package not available or incompatible: {e}")
    logger.debug(traceback.format_exc())
    PINECONE_AVAILABLE = False
    PINECONE_NEW_API = False

# Try to import the Document and Chunk models
try:
    from documents.models import Document, Chunk
    DATABASE_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    logger.warning("Document and Chunk models not available, falling back to file mode")
    DATABASE_AVAILABLE = False

def get_pinecone_client():
    """
    Get a Pinecone client instance.
    
    Returns:
        Pinecone: A Pinecone client instance or None if not available
    """
    if not PINECONE_AVAILABLE:
        logger.warning("Pinecone package not available, falling back to database mode")
        return None
    
    api_key = os.environ.get("PINECONE_API_KEY")
    if not api_key:
        logger.warning("PINECONE_API_KEY not found in environment variables, falling back to database mode")
        return None
    
    try:
        if PINECONE_NEW_API:
            return Pinecone(api_key=api_key)
        else:
            environment = os.environ.get("PINECONE_ENVIRONMENT")
            if not environment:
                logger.warning("PINECONE_ENVIRONMENT not found in environment variables (required for old API), falling back to database mode")
                return None
            
            pinecone.init(api_key=api_key, environment=environment)
            return True  # Return True to indicate successful initialization
    except Exception as e:
        logger.error(f"Error initializing Pinecone client: {e}, falling back to database mode")
        logger.debug(traceback.format_exc())
        return None

def get_pinecone_index(client=None):
    """
    Get a Pinecone index instance.
    
    Args:
        client (Pinecone, optional): A Pinecone client instance. If None, a new client will be created.
        
    Returns:
        Index: A Pinecone index instance or None if not available
    """
    if not PINECONE_AVAILABLE:
        logger.warning("Pinecone package not available, falling back to database mode")
        return None
    
    # Use the correct environment variable for the index name
    index_name = os.environ.get("PINECONE_INDEX_NAME")
    if not index_name:
        logger.warning("PINECONE_INDEX_NAME not found in environment variables, falling back to database mode")
        return None
    
    try:
        if PINECONE_NEW_API:
            if client is None:
                client = get_pinecone_client()
                if client is None:
                    return None
            return client.Index(index_name)
        else:
            if client is None:
                client = get_pinecone_client()
                if not client:
                    return None
            return pinecone.Index(index_name)
    except Exception as e:
        logger.error(f"Error getting Pinecone index: {e}, falling back to database mode")
        logger.debug(traceback.format_exc())
        return None

def search_similar_documents(embedding, top_k=50):
    """
    Search for similar documents in Pinecone or database.
    
    Args:
        embedding (list): The embedding vector to search for
        top_k (int, optional): The number of results to return. Defaults to 50.
        
    Returns:
        list: A list of chunk IDs or file paths
    """
    # Try Pinecone first
    if PINECONE_AVAILABLE:
        try:
            index = get_pinecone_index()
            if index:
                try:
                    # Use the correct query parameters based on API version
                    if PINECONE_NEW_API:
                        query_response = index.query(
                            namespace="ns1",
                            vector=embedding,
                            top_k=top_k,
                            include_metadata=True,
                            include_values=False
                        )
                        matches = query_response.matches
                    else:
                        query_response = index.query(
                            namespace="ns1",
                            vector=embedding,
                            top_k=top_k,
                            include_metadata=True
                        )
                        matches = query_response.get('matches', [])
                    
                    # Extract file paths from matches
                    chunk_ids = []
                    seen_paths = set()
                    
                    for match in matches:
                        # Get metadata based on API version
                        if PINECONE_NEW_API:
                            metadata = match.metadata if hasattr(match, 'metadata') else {}
                        else:
                            metadata = match.get('metadata', {})
                        
                        # Try to get chunk_id first, then fall back to file_path
                        chunk_id = metadata.get('chunk_id')
                        file_path = metadata.get('file_path')
                        
                        if chunk_id and chunk_id not in seen_paths:
                            chunk_ids.append(chunk_id)
                            seen_paths.add(chunk_id)
                        elif file_path and file_path not in seen_paths:
                            # Normalize path separators
                            file_path = file_path.replace('\\', '/')
                            chunk_ids.append(file_path)
                            seen_paths.add(file_path)
                    
                    if chunk_ids:
                        logger.info(f"Found {len(chunk_ids)} similar documents in Pinecone")
                        return chunk_ids
                    else:
                        logger.warning("No matches found in Pinecone, falling back to database")
                except Exception as e:
                    logger.error(f"Error searching Pinecone: {e}, falling back to database")
                    logger.debug(traceback.format_exc())
        except Exception as e:
            logger.error(f"Error with Pinecone: {e}, falling back to database")
            logger.debug(traceback.format_exc())
    else:
        logger.warning("Pinecone not available, falling back to database")
    
    # Fall back to database if available
    if DATABASE_AVAILABLE:
        try:
            # Get all chunks with embeddings
            chunks_with_embeddings = Chunk.objects.exclude(embedding__isnull=True)
            
            if not chunks_with_embeddings.exists():
                logger.warning("No chunks with embeddings found in database")
                return []
            
            # This is a simplified approach - in a real application, you would
            # implement vector similarity search using a database extension
            # like pgvector for PostgreSQL
            
            # For now, just return the most recent chunks as a fallback
            chunk_ids = list(chunks_with_embeddings.order_by('-created_at')[:top_k].values_list('chunk_id', flat=True))
            
            logger.info(f"Found {len(chunk_ids)} chunks in database (fallback)")
            return chunk_ids
        except Exception as e:
            logger.error(f"Error searching database: {e}")
            logger.debug(traceback.format_exc())
    
    # Fall back to empty list if all else fails
    logger.warning("No results found in Pinecone or database")
    return []

def get_chunk_content(chunk_ids):
    """
    Get the content of chunks by their IDs.
    
    Args:
        chunk_ids (list): A list of chunk IDs or file paths
        
    Returns:
        str: The combined content of all chunks
    """
    if not chunk_ids:
        return ""
    
    # Track seen content to avoid duplicates
    seen_content = set()
    all_content = []
    
    # Try database first if available
    if DATABASE_AVAILABLE:
        for chunk_id in chunk_ids:
            try:
                # Try to find the chunk by chunk_id
                chunk = Chunk.objects.filter(chunk_id=chunk_id).first()
                
                if chunk and chunk.content and chunk.content not in seen_content:
                    all_content.append(chunk.content)
                    seen_content.add(chunk.content)
                    continue
            except Exception as e:
                logger.error(f"Error retrieving chunk {chunk_id} from database: {e}")
    
    # Fall back to file system for any remaining chunk_ids
    for chunk_id in chunk_ids:
        if not isinstance(chunk_id, str):
            continue
            
        # Skip if it's a database chunk_id pattern (e.g., "chunk_001")
        if chunk_id.startswith("chunk_") and chunk_id[6:].isdigit():
            continue
            
        # Try to read from file system
        try:
            # Normalize path separators
            file_path = chunk_id.replace('\\', '/')
            
            # Try multiple strategies to find the file
            paths_to_try = [
                # Direct path
                file_path,
                # Path relative to BASE_DIR
                os.path.join(settings.BASE_DIR, file_path),
                # Path in data/chunks directory
                os.path.join(settings.BASE_DIR, "data", "chunks", os.path.basename(file_path)),
                # Path with 'chunks' directory
                os.path.join(settings.BASE_DIR, "data", "chunks", file_path)
            ]
            
            for path in paths_to_try:
                path_obj = Path(path)
                if path_obj.exists() and path_obj.is_file():
                    content = path_obj.read_text(encoding='utf-8')
                    if content and content not in seen_content:
                        all_content.append(content)
                        seen_content.add(content)
                        break
        except Exception as e:
            logger.error(f"Error reading chunk file {chunk_id}: {e}")
    
    # Join all content with double newlines
    return "\n\n".join(all_content)

def get_chunks_for_display(chunk_ids, max_chunks=20):
    """
    Get chunks formatted for display in the UI.
    
    Args:
        chunk_ids (list): A list of chunk IDs or file paths
        max_chunks (int, optional): Maximum number of chunks to return. Defaults to 10.
        
    Returns:
        list: A list of dictionaries with chunk information
    """
    if not chunk_ids:
        return []
    
    chunks_for_display = []
    seen_content = set()
    
    # Try database first if available
    if DATABASE_AVAILABLE:
        for chunk_id in chunk_ids[:max_chunks]:
            try:
                # Try to find the chunk by chunk_id
                chunk = Chunk.objects.filter(chunk_id=chunk_id).first()
                
                if chunk and chunk.content and chunk.content not in seen_content:
                    # Get document title if available
                    document_title = chunk.document.title if chunk.document else "Unknown Document"
                    
                    # Create a title from metadata or chunk_id
                    if chunk.metadata and 'document_title' in chunk.metadata:
                        title = f"{chunk.metadata['document_title']} - Chunk {chunk.metadata.get('chunk_number', '?')}"
                    else:
                        title = f"{document_title} - {chunk.chunk_id}"
                    
                    chunks_for_display.append({
                        "id": chunk.chunk_id,
                        "title": title,
                        "content": chunk.content,
                        "metadata": chunk.metadata or {}
                    })
                    
                    seen_content.add(chunk.content)
                    continue
            except Exception as e:
                logger.error(f"Error retrieving chunk {chunk_id} from database: {e}")
    
    # Fall back to file system for any remaining chunk_ids
    remaining_slots = max_chunks - len(chunks_for_display)
    if remaining_slots <= 0:
        return chunks_for_display
        
    for chunk_id in chunk_ids[:remaining_slots]:
        if not isinstance(chunk_id, str):
            continue
            
        # Skip if it's a database chunk_id pattern that we've already processed
        if chunk_id.startswith("chunk_") and chunk_id[6:].isdigit() and any(c["id"] == chunk_id for c in chunks_for_display):
            continue
            
        # Try to read from file system
        try:
            # Normalize path separators
            file_path = chunk_id.replace('\\', '/')
            
            # Try multiple strategies to find the file
            paths_to_try = [
                # Direct path
                file_path,
                # Path relative to BASE_DIR
                os.path.join(settings.BASE_DIR, file_path),
                # Path in data/chunks directory
                os.path.join(settings.BASE_DIR, "data", "chunks", os.path.basename(file_path)),
                # Path with 'chunks' directory
                os.path.join(settings.BASE_DIR, "data", "chunks", file_path)
            ]
            
            for path in paths_to_try:
                path_obj = Path(path)
                if path_obj.exists() and path_obj.is_file():
                    content = path_obj.read_text(encoding='utf-8')
                    if content and content not in seen_content:
                        # Create a title from the file path
                        filename = path_obj.name
                        parent_dir = path_obj.parent.name
                        
                        if parent_dir == "chunks":
                            title = filename
                        else:
                            title = f"{parent_dir}/{filename}"
                        
                        chunks_for_display.append({
                            "id": file_path,
                            "title": title,
                            "content": content,
                            "metadata": {"file_path": str(path_obj)}
                        })
                        
                        seen_content.add(content)
                        break
        except Exception as e:
            logger.error(f"Error reading chunk file {chunk_id}: {e}")
    
    return chunks_for_display 