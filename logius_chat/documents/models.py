from django.db import models
import uuid
from pathlib import Path

class Document(models.Model):
    """
    Model representing a document (e.g., a markdown file).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    filename = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    def chunk_content(self, chunk_size=1000, overlap=200):
        """
        Chunk the document content into smaller pieces.
        
        Args:
            chunk_size (int): Size of each chunk in characters
            overlap (int): Overlap between chunks in characters
            
        Returns:
            list: List of created Chunk objects
        """
        # Delete existing chunks for this document
        self.chunks.all().delete()
        
        # Get the document content
        content = self.content
        
        # If content is empty, return empty list
        if not content:
            return []
        
        # Create chunks
        chunks = []
        start = 0
        chunk_number = 1
        
        while start < len(content):
            # Calculate end position
            end = min(start + chunk_size, len(content))
            
            # Extract chunk text
            chunk_text = content[start:end]
            
            # Create chunk ID
            chunk_id = f"chunk_{chunk_number:03d}"
            
            # Create metadata
            metadata = {
                "document_title": self.title,
                "chunk_number": chunk_number,
                "start_char": start,
                "end_char": end
            }
            
            # Create chunk
            chunk = Chunk.objects.create(
                document=self,
                chunk_id=chunk_id,
                content=chunk_text,
                metadata=metadata
            )
            
            chunks.append(chunk)
            
            # Move to next chunk position, accounting for overlap
            start = end - overlap if end < len(content) else len(content)
            chunk_number += 1
        
        return chunks
    
    class Meta:
        ordering = ['title']

class Chunk(models.Model):
    """
    Model representing a chunk of a document for RAG.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='chunks')
    chunk_id = models.CharField(max_length=255, unique=True)
    content = models.TextField()
    embedding = models.JSONField(null=True, blank=True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Chunk {self.chunk_id}"
    
    @property
    def title(self):
        """Generate a readable title for the chunk."""
        # Try to get document name from metadata or document title
        doc_name = self.document.title if self.document else None
        
        # Try to get section from metadata
        section = self.metadata.get('section', '')
        
        # Create a readable title
        if doc_name and section:
            return f"{doc_name} - {section}"
        elif doc_name:
            return doc_name
        else:
            return self.chunk_id
    
    class Meta:
        ordering = ['chunk_id']
