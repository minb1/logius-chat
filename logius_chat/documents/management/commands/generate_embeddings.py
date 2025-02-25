from django.core.management.base import BaseCommand
from documents.models import Chunk
from model_layer.embedding_service import get_embedding
import time

class Command(BaseCommand):
    help = 'Generate embeddings for chunks that do not have them'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Maximum number of chunks to process',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=10,
            help='Number of chunks to process in a batch before pausing',
        )
        parser.add_argument(
            '--pause',
            type=int,
            default=1,
            help='Pause in seconds between batches to avoid rate limiting',
        )

    def handle(self, *args, **options):
        limit = options.get('limit')
        batch_size = options.get('batch_size')
        pause = options.get('pause')
        
        # Get chunks without embeddings
        chunks_without_embeddings = Chunk.objects.filter(embedding__isnull=True)
        total_chunks = chunks_without_embeddings.count()
        
        if limit:
            chunks_without_embeddings = chunks_without_embeddings[:limit]
            self.stdout.write(self.style.SUCCESS(f'Processing up to {limit} chunks out of {total_chunks} chunks without embeddings'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Processing all {total_chunks} chunks without embeddings'))
        
        # Process chunks in batches
        processed = 0
        successful = 0
        failed = 0
        
        for i, chunk in enumerate(chunks_without_embeddings):
            try:
                # Generate embedding
                self.stdout.write(f'Generating embedding for chunk {chunk.chunk_id}...')
                embedding = get_embedding(chunk.content)
                
                if embedding:
                    # Save embedding to chunk
                    chunk.embedding = embedding
                    chunk.save()
                    successful += 1
                    self.stdout.write(self.style.SUCCESS(f'Successfully generated embedding for chunk {chunk.chunk_id}'))
                else:
                    failed += 1
                    self.stdout.write(self.style.ERROR(f'Failed to generate embedding for chunk {chunk.chunk_id}'))
            except Exception as e:
                failed += 1
                self.stdout.write(self.style.ERROR(f'Error processing chunk {chunk.chunk_id}: {e}'))
            
            processed += 1
            
            # Pause after each batch
            if processed % batch_size == 0:
                self.stdout.write(f'Processed {processed} chunks. Pausing for {pause} seconds...')
                time.sleep(pause)
        
        self.stdout.write(self.style.SUCCESS(f'Finished processing {processed} chunks'))
        self.stdout.write(self.style.SUCCESS(f'Successfully generated embeddings for {successful} chunks'))
        if failed > 0:
            self.stdout.write(self.style.ERROR(f'Failed to generate embeddings for {failed} chunks')) 