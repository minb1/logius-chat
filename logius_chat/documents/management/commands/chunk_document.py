import os
import uuid
from django.core.management.base import BaseCommand, CommandError
from documents.models import Document
from django.conf import settings

class Command(BaseCommand):
    help = 'Chunk a document by its ID'

    def add_arguments(self, parser):
        parser.add_argument('document_id', type=str, help='The ID of the document to chunk')
        parser.add_argument('--chunk-size', type=int, default=1000, help='Size of each chunk in characters')
        parser.add_argument('--overlap', type=int, default=200, help='Overlap between chunks in characters')

    def handle(self, *args, **options):
        document_id = options['document_id']
        chunk_size = options['chunk_size']
        overlap = options['overlap']
        
        try:
            # Try to parse as UUID first
            try:
                document_id = uuid.UUID(document_id)
            except ValueError:
                pass
                
            document = Document.objects.get(id=document_id)
        except Document.DoesNotExist:
            raise CommandError(f'Document with ID {document_id} does not exist')
        
        self.stdout.write(self.style.SUCCESS(f'Found document: {document.title}'))
        
        # Check if document has content
        if not document.content:
            raise CommandError(f'Document {document.title} has no content to chunk')
        
        # Chunk the document
        self.stdout.write(f'Chunking document with chunk size {chunk_size} and overlap {overlap}...')
        chunks = document.chunk_content(chunk_size=chunk_size, overlap=overlap)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully chunked document into {len(chunks)} chunks'))
        
        # Display chunk IDs
        for i, chunk in enumerate(chunks[:5], 1):
            self.stdout.write(f'  Chunk {i}: {chunk.id} ({len(chunk.content)} chars)')
        
        if len(chunks) > 5:
            self.stdout.write(f'  ... and {len(chunks) - 5} more chunks') 