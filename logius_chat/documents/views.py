import os
import tempfile
import uuid
from django.http import JsonResponse
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Document, Chunk
from .serializers import (
    DocumentSerializer, 
    DocumentListSerializer, 
    DocumentDetailSerializer,
    DocumentCreateSerializer,
    ChunkSerializer,
    ChunkListSerializer
)

class DocumentListView(APIView):
    """
    List all documents or create a new document.
    """
    def get(self, request):
        documents = Document.objects.all()
        serializer = DocumentListSerializer(documents, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        # Handle file upload
        if 'file' in request.FILES:
            file_obj = request.FILES['file']
            
            # Create a temporary file to store the uploaded content
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                for chunk in file_obj.chunks():
                    temp_file.write(chunk)
                temp_path = temp_file.name
            
            try:
                # Read the file content
                with open(temp_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Create document data
                data = {
                    'title': request.data.get('title', os.path.splitext(file_obj.name)[0]),
                    'filename': file_obj.name,
                    'content': content
                }
                
                serializer = DocumentCreateSerializer(data=data)
                if serializer.is_valid():
                    document = Document.objects.create(
                        title=data['title'],
                        filename=data['filename'],
                        content=data['content']
                    )
                    
                    # Return the created document
                    response_serializer = DocumentSerializer(document)
                    return Response(response_serializer.data, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            finally:
                # Clean up the temporary file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
        
        # Handle direct content submission
        else:
            serializer = DocumentCreateSerializer(data=request.data)
            if serializer.is_valid():
                document = Document.objects.create(
                    title=serializer.validated_data.get('title', 'Untitled Document'),
                    filename=serializer.validated_data.get('filename', 'untitled.md'),
                    content=serializer.validated_data.get('content', '')
                )
                
                # Return the created document
                response_serializer = DocumentSerializer(document)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DocumentDetailView(APIView):
    """
    Retrieve, update or delete a document instance.
    """
    def get_object(self, document_id):
        try:
            return Document.objects.get(id=document_id)
        except Document.DoesNotExist:
            return None
    
    def get(self, request, document_id):
        document = self.get_object(document_id)
        if document is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = DocumentDetailSerializer(document)
        return Response(serializer.data)
    
    def put(self, request, document_id):
        document = self.get_object(document_id)
        if document is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = DocumentSerializer(document, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, document_id):
        document = self.get_object(document_id)
        if document is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        document.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ChunkDocumentView(APIView):
    """
    Chunk a document.
    """
    def get_object(self, document_id):
        try:
            return Document.objects.get(id=document_id)
        except Document.DoesNotExist:
            return None
    
    def post(self, request, document_id):
        document = self.get_object(document_id)
        if document is None:
            return Response({"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Get chunking parameters
        chunk_size = request.data.get('chunk_size', 1000)
        overlap = request.data.get('overlap', 200)
        
        try:
            # Chunk the document
            chunks = document.chunk_content(chunk_size=chunk_size, overlap=overlap)
            
            # Return the chunks
            serializer = ChunkListSerializer(chunks, many=True)
            return Response({
                "message": f"Document chunked successfully into {len(chunks)} chunks",
                "chunks": serializer.data
            })
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
