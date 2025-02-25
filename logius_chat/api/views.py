from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from context_layer.rag_service import process_query
from context_layer.redis_service import create_chat_session, get_chat_history

class ChatSessionView(APIView):
    """
    API view for creating a new chat session.
    """
    
    def post(self, request):
        """
        Create a new chat session.
        
        Returns:
            {
                "chat_id": "uuid-string"
            }
        """
        chat_id = create_chat_session()
        return Response({"chat_id": chat_id})

class ChatHistoryView(APIView):
    """
    API view for retrieving chat history.
    """
    
    def get(self, request, chat_id):
        """
        Get the chat history for a specific chat session.
        
        Returns:
            {
                "history": [
                    {"role": "user", "content": "How do I create a new branch in Git?", "timestamp": "..."},
                    {"role": "assistant", "content": "To create a new branch...", "timestamp": "..."}
                ]
            }
        """
        history = get_chat_history(chat_id)
        return Response({"history": history})

class ChatView(APIView):
    """
    API view for handling chat requests.
    """
    
    def post(self, request):
        """
        Process a chat request.
        
        Request body:
            {
                "query": "How do I create a new branch in Git?",
                "chat_id": "uuid-string" (optional)
            }
            
        Returns:
            {
                "response": "To create a new branch in Git, use the command 'git branch <branch-name>'...",
                "chunks": [
                    {
                        "id": "chunk_001.txt",
                        "title": "chunk_001.txt",
                        "path": "data/chunks/chunk_001.txt",
                        "content": "Content of the chunk..."
                    },
                    ...
                ]
            }
        """
        query = request.data.get('query')
        chat_id = request.data.get('chat_id')
        
        if not query:
            return Response(
                {"error": "Query is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Process the query through the RAG pipeline
        result = process_query(query, chat_id)
        
        return Response(result)
