from django.urls import path
from .views import ChatView, ChatSessionView, ChatHistoryView

urlpatterns = [
    path('chat/', ChatView.as_view(), name='chat'),
    path('chat/session/', ChatSessionView.as_view(), name='chat_session'),
    path('chat/history/<str:chat_id>/', ChatHistoryView.as_view(), name='chat_history'),
]
