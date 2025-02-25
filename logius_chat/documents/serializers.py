from rest_framework import serializers
from .models import Document, Chunk

class ChunkSerializer(serializers.ModelSerializer):
    has_embedding = serializers.SerializerMethodField()
    
    class Meta:
        model = Chunk
        fields = ['id', 'document', 'content', 'metadata', 'has_embedding', 'created_at', 'updated_at']
    
    def get_has_embedding(self, obj):
        return obj.embedding is not None

class ChunkListSerializer(serializers.ModelSerializer):
    has_embedding = serializers.SerializerMethodField()
    content_preview = serializers.SerializerMethodField()
    
    class Meta:
        model = Chunk
        fields = ['id', 'document', 'content_preview', 'metadata', 'has_embedding', 'created_at', 'updated_at']
    
    def get_has_embedding(self, obj):
        return obj.embedding is not None
    
    def get_content_preview(self, obj):
        max_length = 100
        content = obj.content
        if len(content) > max_length:
            return content[:max_length] + '...'
        return content

class DocumentSerializer(serializers.ModelSerializer):
    chunk_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = ['id', 'title', 'filename', 'content', 'chunk_count', 'created_at', 'updated_at']
    
    def get_chunk_count(self, obj):
        return obj.chunks.count()

class DocumentListSerializer(serializers.ModelSerializer):
    chunk_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = ['id', 'title', 'filename', 'chunk_count', 'created_at', 'updated_at']
    
    def get_chunk_count(self, obj):
        return obj.chunks.count()

class DocumentDetailSerializer(serializers.ModelSerializer):
    chunks = ChunkListSerializer(many=True, read_only=True)
    chunk_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = ['id', 'title', 'filename', 'content', 'chunks', 'chunk_count', 'created_at', 'updated_at']
    
    def get_chunk_count(self, obj):
        return obj.chunks.count()

class DocumentCreateSerializer(serializers.ModelSerializer):
    file = serializers.FileField(required=False, write_only=True)
    content = serializers.CharField(required=False)
    
    class Meta:
        model = Document
        fields = ['title', 'filename', 'content', 'file']
    
    def validate(self, data):
        if 'file' not in data and 'content' not in data:
            raise serializers.ValidationError("Either file or content must be provided")
        return data 