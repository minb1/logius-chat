from django.core.management.base import BaseCommand
from documents.models import Document, Chunk

class Command(BaseCommand):
    help = 'List chunks stored in the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=10,
            help='Number of chunks to display (default: 10)',
        )
        parser.add_argument(
            '--document',
            type=str,
            help='Filter by document title (case-insensitive partial match)',
        )

    def handle(self, *args, **options):
        limit = options.get('limit')
        document_filter = options.get('document')
        
        # Get document count
        doc_count = Document.objects.count()
        self.stdout.write(self.style.SUCCESS(f'Total documents in database: {doc_count}'))
        
        # Get chunk count
        chunk_count = Chunk.objects.count()
        self.stdout.write(self.style.SUCCESS(f'Total chunks in database: {chunk_count}'))
        
        # Get chunks with embeddings count
        chunks_with_embeddings = Chunk.objects.exclude(embedding__isnull=True).count()
        self.stdout.write(self.style.SUCCESS(f'Chunks with embeddings: {chunks_with_embeddings}'))
        
        # Filter chunks if document filter is provided
        if document_filter:
            chunks = Chunk.objects.filter(document__title__icontains=document_filter)
            self.stdout.write(self.style.SUCCESS(f'Filtered chunks by document title containing "{document_filter}": {chunks.count()}'))
        else:
            chunks = Chunk.objects.all()
        
        # Display chunks
        self.stdout.write(self.style.SUCCESS(f'\nDisplaying {min(limit, chunks.count())} chunks:'))
        for i, chunk in enumerate(chunks[:limit]):
            self.stdout.write(self.style.SUCCESS(f'\n{i+1}. Chunk ID: {chunk.chunk_id}'))
            self.stdout.write(f'   Document: {chunk.document.title}')
            self.stdout.write(f'   Has embedding: {"Yes" if chunk.embedding else "No"}')
            self.stdout.write(f'   Content preview: {chunk.content[:100]}...')
            self.stdout.write(f'   Metadata: {chunk.metadata}') 