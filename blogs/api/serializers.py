from rest_framework import serializers
from ..models import Blog
from django.conf import settings


class BlogSerializer(serializers.ModelSerializer):
    featured_image_url = serializers.SerializerMethodField()
    created_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    slug = serializers.SlugField(read_only=True)

    class Meta:
        model = Blog
        fields = [
            'id', 'title', 'slug', 'featured_image', 'featured_image_url',
            'content', 'summary', 'category', 'status', 'tags',
            'created_at', 'updated_at', 'published_date', 'created_by', 'created_time'
        ]
        read_only_fields = [
            'slug', 'created_at', 'updated_at',
            'created_by', 'created_time', 'featured_image_url'
        ]

    def get_featured_image_url(self, obj):
        if obj.featured_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.featured_image.url)
            return f"{settings.MEDIA_URL}{obj.featured_image.name}"
        return None


class BlogListSerializer(serializers.ModelSerializer):
    featured_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Blog
        fields = ['id', 'title', 'slug', 'summary', 'status', 'category', 'created_at', 'featured_image_url']
        read_only_fields = ['slug', 'featured_image_url']

    def get_featured_image_url(self, obj):
        if obj.featured_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.featured_image.url)
            return f"{settings.MEDIA_URL}{obj.featured_image.name}"
        return None