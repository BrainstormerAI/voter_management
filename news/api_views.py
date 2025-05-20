from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.template.loader import render_to_string
from django.http import HttpResponse
from .models import News, ArchivedNews
from .serializers import NewsSerializer
import logging

logger = logging.getLogger(__name__)

class NewsAPIViewSet(viewsets.ModelViewSet):
    """
    API endpoints for managing news items.
    
    list:
        GET /api/news/ - Get all news items
        
    retrieve:
        GET /api/news/{id}/ - Get a specific news item
        
    create:
        POST /api/news/ - Create a new news item
        
    update:
        PUT /api/news/{id}/ - Update entire news item
        PATCH /api/news/{id}/ - Partially update news item
        
    delete:
        DELETE /api/news/{id}/ - Delete a news item
        
    preview:
        GET /api/news/{id}/preview/ - Get preview in HTML or JSON format
        GET /api/news/{id}/preview/?format=html - Explicit HTML format
    """
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """
        Override to allow public access to preview endpoint.
        """
        if self.action in ['preview', 'retrieve', 'list']:
            logger.debug(f"Allowing access to {self.action} without authentication")
            return [AllowAny()]
        return super().get_permissions()

    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        """
        Get a preview of the news item in either HTML or JSON format.
        Add ?format=html to the URL for HTML format.
        """
        try:
            news = self.get_object()
            
            # Check if HTML format is explicitly requested
            if request.query_params.get('format') == 'html':
                logger.debug(f"Rendering HTML preview for news ID: {pk}")
                html_content = render_to_string('admin/news/preview.html', {'news': news})
                return HttpResponse(html_content, content_type='text/html')
                
            serializer = self.get_serializer(news)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error in preview: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        """
        Delete a news item and create an archive entry.
        """
        instance = self.get_object()
        ArchivedNews.objects.create(news=instance)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """
        Archive a news item.
        POST /api/news/{id}/archive/
        """
        news = self.get_object()
        news.archived = True
        news.save()
        ArchivedNews.objects.get_or_create(news=news)
        return Response({'status': 'archived'})

    @action(detail=True, methods=['post'])
    def unarchive(self, request, pk=None):
        """
        Unarchive a news item.
        POST /api/news/{id}/unarchive/
        """
        news = self.get_object()
        news.archived = False
        news.save()
        ArchivedNews.objects.filter(news=news).delete()
        return Response({'status': 'unarchived'}) 