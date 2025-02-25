from django.urls import path
from .views import DocumentListView, DocumentDetailView, ChunkDocumentView

urlpatterns = [
    path('documents/', DocumentListView.as_view(), name='document_list'),
    path('documents/<uuid:document_id>/', DocumentDetailView.as_view(), name='document_detail'),
    path('documents/<uuid:document_id>/chunk/', ChunkDocumentView.as_view(), name='chunk_document'),
] 