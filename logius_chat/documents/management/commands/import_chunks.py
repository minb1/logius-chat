import os
from django.core.management.base import BaseCommand
from django.conf import settings
from documents.services import import_chunks_from_directory

class Command(BaseCommand):
    help = 'Import chunks from the data directory into the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--directory',
            type=str,
            help='Directory containing chunk files (default: DATA_DIR/chunks)',
        )

    def handle(self, *args, **options):
        # Get the directory from options or use default
        directory = options.get('directory')
        if not directory:
            directory = os.path.join(settings.DATA_DIR, 'chunks')
        
        self.stdout.write(self.style.SUCCESS(f'Importing chunks from {directory}...'))
        
        # Import chunks
        count = import_chunks_from_directory(directory)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully imported {count} chunks.')) 