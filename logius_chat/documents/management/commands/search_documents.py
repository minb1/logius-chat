import os
import logging
from django.core.management.base import BaseCommand
from documents.models import Document, Chunk
from model_layer.embedding_service import get_embedding, cosine_similarity
import numpy as np

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Search for documents in the database using semantic search'

    def add_arguments(self, parser):
        parser.add_argument('query', type=str, help='The search query')
        parser.add_argument('--limit', type=int, default=10, help='Maximum number of results to return')
        parser.add_argument('--document-id', type=str, help='Limit search to a specific document ID')
        parser.add_argument('--threshold', type=float, default=0.5, help='Similarity threshold (0-1)')

    def handle(self, *args, **options):
        query = options['query']
        limit = options['limit']
        document_id = options.get('document_id')
        threshold = options['threshold']
        
        self.stdout.write(f"Searching for: '{query}'")
        
        # Generate embedding for the query
        query_embedding = get_embedding(query)
        if not query_embedding:
            self.stdout.write(self.style.ERROR("Failed to generate embedding for query"))
            return
        
        # Get chunks with embeddings
        chunks_query = Chunk.objects.exclude(embedding__isnull=True)
        
        # Filter by document if specified
        if document_id:
            try:
                document = Document.objects.get(id=document_id)
                chunks_query = chunks_query.filter(document=document)
                self.stdout.write(f"Limiting search to document: {document.title}")
            except Document.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Document with ID {document_id} not found"))
                return
        
        # Get all chunks with embeddings
        chunks = list(chunks_query)
        if not chunks:
            self.stdout.write(self.style.WARNING("No chunks with embeddings found"))
            return
        
        self.stdout.write(f"Comparing query against {len(chunks)} chunks...")
        
        # Calculate similarity scores
        results = []
        for chunk in chunks:
            if not chunk.embedding:
                continue
                
            similarity = cosine_similarity(query_embedding, chunk.embedding)
            if similarity >= threshold:
                results.append((chunk, similarity))
        
        # Sort by similarity score (descending)
        results.sort(key=lambda x: x[1], reverse=True)
        
        # Limit results
        results = results[:limit]
        
        if not results:
            self.stdout.write(self.style.WARNING(f"No results found with similarity >= {threshold}"))
            return
        
        # Display results
        self.stdout.write(self.style.SUCCESS(f"Found {len(results)} results:"))
        for i, (chunk, similarity) in enumerate(results, 1):
            document_title = chunk.document.title if chunk.document else "Unknown Document"
            self.stdout.write(f"\n{i}. {document_title} - Chunk {chunk.chunk_id} (Score: {similarity:.4f})")
            self.stdout.write(f"   {chunk.content[:200]}..." if len(chunk.content) > 200 else chunk.content) 