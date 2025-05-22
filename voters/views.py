from django.shortcuts import render
from django.http import JsonResponse
from .models import Voter, VoterField
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
import json
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q
from .models import Voter
from .serializers import VoterSerializer
from notifications.models import NotificationTemplate, NotificationLog
from django.utils import timezone
import requests
from django.conf import settings
import logging
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# Set up logging
logger = logging.getLogger(__name__)


@api_view(['GET'])
def get_filter_options(request):
    try:
        mlc_constituncy = request.GET.get('mlc_constituncy', '')
        assembly = request.GET.get('assembly', '')
        mandal = request.GET.get('mandal', '')

        # Base queryset
        queryset = Voter.objects.all()

        # Apply cascading filters
        if mlc_constituncy:
            queryset = queryset.filter(data__contains={'MLC CONSTITUNCY': mlc_constituncy})
        if assembly:
            queryset = queryset.filter(data__contains={'ASSEMBLY': assembly})
        if mandal:
            queryset = queryset.filter(data__contains={'MANDAL': mandal})

        # Get unique values based on applied filters
        assemblies = list(queryset.values_list('data__ASSEMBLY', flat=True).distinct())
        mandals = list(queryset.values_list('data__MANDAL', flat=True).distinct())
        locations = list(queryset.values_list('data__LOCATION', flat=True).distinct())

        return Response({
            'success': True,
            'data': {
                'assemblies': assemblies,
                'mandals': mandals,
                'locations': locations
            }
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        })


@api_view(['GET'])
@csrf_protect
@login_required
@permission_classes([IsAuthenticated])
def filter_voters(request):
    try:
        # Get filter parameters
        mlc_constituncy = request.GET.get('mlc_constituncy', '')
        assembly = request.GET.get('assembly', '')
        mandal = request.GET.get('mandal', '')
        location = request.GET.get('location', '')

        # Start with all voters
        queryset = Voter.objects.all()

        # Apply filters if they exist
        if mlc_constituncy:
            queryset = queryset.filter(data__contains={'MLC CONSTITUNCY': mlc_constituncy})
        if assembly:
            queryset = queryset.filter(data__contains={'ASSEMBLY': assembly})
        if mandal:
            queryset = queryset.filter(data__contains={'MANDAL': mandal})
        if location:
            queryset = queryset.filter(data__contains={'LOCATION': location})

        # Serialize the filtered data
        serializer = VoterSerializer(queryset, many=True)

        return Response({
            'success': True,
            'data': serializer.data
        })
    except Exception as e:
        import traceback
        return Response({
            'success': False,
            'error': str(e),
            'trace': traceback.format_exc()
        }, status=500)

def voter_list(request):
    voters = Voter.objects.all()
    return JsonResponse({
        'count': voters.count(),
        'fields': list(VoterField.objects.values('name', 'field_type'))
    })


@require_POST
@staff_member_required
def send_notification(request):
    try:
        data = json.loads(request.body)
        template_id = data.get('template_id')
        channel = data.get('channel')
        voter_ids = data.get('voter_ids', [])

        if not all([template_id, channel, voter_ids]):
            return JsonResponse({
                'success': False,
                'error': 'Missing required parameters'
            })

        # Forward the request to notifications app
        response = requests.post(
            f"{request.scheme}://{request.get_host()}/notifications/send/",
            json={
                'template_id': template_id,
                'channel': channel,
                'recipients': voter_ids
            }
        )

        return JsonResponse(response.json())
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})