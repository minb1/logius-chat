from django.contrib import admin
from .models import Document, Chunk

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'filename', 'created_at', 'updated_at')
    search_fields = ('title', 'filename', 'content')
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Chunk)
class ChunkAdmin(admin.ModelAdmin):
    list_display = ('chunk_id', 'document', 'created_at')
    search_fields = ('chunk_id', 'content')
    list_filter = ('created_at', 'document')
    readonly_fields = ('created_at',)
