from django.urls import path
from .api_views import NewsAPIViewSet

# Define the URL patterns directly
urlpatterns = [
    # List and create
    path('', NewsAPIViewSet.as_view({'get': 'list', 'post': 'create'}), name='news-list'),
    
    # Retrieve, update, delete
    path('<int:pk>/', NewsAPIViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='news-detail'),
    
    # Custom actions
    path('<int:pk>/preview/', NewsAPIViewSet.as_view({'get': 'preview'}), name='news-preview'),
    path('<int:pk>/archive/', NewsAPIViewSet.as_view({'post': 'archive'}), name='news-archive'),
    path('<int:pk>/unarchive/', NewsAPIViewSet.as_view({'post': 'unarchive'}), name='news-unarchive'),
]
