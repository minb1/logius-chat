import os
from django.core.management.base import BaseCommand
from documents.services import import_document_from_file, chunk_document

class Command(BaseCommand):
    help = 'Import a markdown document and chunk it'

    def add_arguments(self, parser):
        parser.add_argument(
            'file_path',
            type=str,
            help='Path to the markdown file to import',
        )
        parser.add_argument(
            '--chunk-size',
            type=int,
            default=1000,
            help='Size of each chunk in characters (default: 1000)',
        )
        parser.add_argument(
            '--overlap',
            type=int,
            default=200,
            help='Overlap between chunks in characters (default: 200)',
        )

    def handle(self, *args, **options):
        file_path = options.get('file_path')
        chunk_size = options.get('chunk_size')
        overlap = options.get('overlap')
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
            return
        
        # Import the document
        self.stdout.write(self.style.SUCCESS(f'Importing document from {file_path}...'))
        document = import_document_from_file(file_path)
        self.stdout.write(self.style.SUCCESS(f'Successfully imported document: {document.title}'))
        
        # Chunk the document
        self.stdout.write(self.style.SUCCESS(f'Chunking document with chunk size {chunk_size} and overlap {overlap}...'))
        chunks = chunk_document(document, chunk_size=chunk_size, overlap=overlap)
        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(chunks)} chunks')) 