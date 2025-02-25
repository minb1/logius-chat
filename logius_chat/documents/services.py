import os
import uuid
from pathlib import Path
from .models import Document, Chunk
from model_layer.embedding_service import get_embedding

def import_document_from_file(file_path):
    """
    Import a document from a file into the database.
    
    Args:
        file_path (str): Path to the document file
        
    Returns:
        Document: The created document object
    """
    path = Path(file_path)
    
    # Read the file content
    with open(path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Create the document
    document = Document.objects.create(
        title=path.stem.replace('_', ' ').replace('-', ' ').title(),
        filename=path.name,
        content=content
    )
    
    return document

def chunk_document(document, chunk_size=1000, overlap=200):
    """
    Split a document into chunks and store them in the database.
    
    Args:
        document (Document): The document to chunk
        chunk_size (int): Size of each chunk in characters
        overlap (int): Overlap between chunks in characters
        
    Returns:
        list: List of created Chunk objects
    """
    content = document.content
    chunks = []
    
    # Simple chunking by character count with overlap
    for i in range(0, len(content), chunk_size - overlap):
        chunk_content = content[i:i + chunk_size]
        if not chunk_content.strip():
            continue
            
        # Generate a unique chunk ID
        chunk_id = f"{document.filename.split('.')[0]}_chunk_{len(chunks) + 1}"
        
        # Create metadata
        metadata = {
            'document_id': str(document.id),
            'document_title': document.title,
            'chunk_index': len(chunks) + 1,
            'section': f"Section {len(chunks) + 1}"
        }
        
        # Create the chunk
        chunk = Chunk.objects.create(
            document=document,
            chunk_id=chunk_id,
            content=chunk_content,
            metadata=metadata
        )
        
        # Generate embedding for the chunk
        embedding = get_embedding(chunk_content)
        if embedding:
            chunk.embedding = embedding
            chunk.save()
            
        chunks.append(chunk)
    
    return chunks

def import_chunks_from_directory(directory_path):
    """
    Import chunks from a directory into the database.
    
    Args:
        directory_path (str): Path to the directory containing chunk files
        
    Returns:
        int: Number of chunks imported
    """
    path = Path(directory_path)
    count = 0
    
    # Walk through the directory
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('.txt'):
                file_path = os.path.join(root, file)
                
                # Read the file content
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract document name from path or filename
                parts = Path(file_path).parts
                doc_name = None
                for part in parts:
                    if '_' in part and not part.startswith('chunk_'):
                        doc_name = part.replace('_', ' ').replace('-', ' ').title()
                        break
                
                if not doc_name:
                    doc_name = "Unknown Document"
                
                # Find or create the document
                document, created = Document.objects.get_or_create(
                    title=doc_name,
                    defaults={
                        'filename': f"{doc_name.lower().replace(' ', '_')}.md",
                        'content': f"Document for chunk {file}"
                    }
                )
                
                # Create metadata
                metadata = {
                    'document_id': str(document.id),
                    'document_title': document.title,
                    'file_path': file_path,
                    'section': Path(file_path).stem
                }
                
                # Create the chunk
                chunk, created = Chunk.objects.get_or_create(
                    chunk_id=Path(file_path).stem,
                    defaults={
                        'document': document,
                        'content': content,
                        'metadata': metadata
                    }
                )
                
                # Generate embedding for the chunk if it doesn't have one
                if created or not chunk.embedding:
                    embedding = get_embedding(content)
                    if embedding:
                        chunk.embedding = embedding
                        chunk.save()
                
                count += 1
    
    return count

def search_chunks(query_embedding, top_k=50):
    """
    Search for chunks similar to the query embedding.
    
    Args:
        query_embedding (list): The embedding vector of the query
        top_k (int): Number of similar chunks to retrieve
        
    Returns:
        list: List of Chunk objects
    """
    # Get all chunks with embeddings
    chunks = Chunk.objects.exclude(embedding__isnull=True)
    
    # Calculate similarity scores (dot product)
    chunk_scores = []
    for chunk in chunks:
        # Convert embedding from JSON to list if needed
        chunk_embedding = chunk.embedding
        
        # Calculate dot product
        score = sum(a * b for a, b in zip(query_embedding, chunk_embedding))
        chunk_scores.append((chunk, score))
    
    # Sort by score and get top_k
    chunk_scores.sort(key=lambda x: x[1], reverse=True)
    return [chunk for chunk, score in chunk_scores[:top_k]]

def get_chunk_by_id(chunk_id):
    """
    Get a chunk by its ID.
    
    Args:
        chunk_id (str): The ID of the chunk
        
    Returns:
        Chunk: The chunk object or None if not found
    """
    try:
        return Chunk.objects.get(chunk_id=chunk_id)
    except Chunk.DoesNotExist:
        return None 