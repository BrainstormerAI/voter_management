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
from rest_framework.permissions import AllowAny


# Set up logging
logger = logging.getLogger(__name__)


@staff_member_required
@require_GET
def get_filter_options(request):
    try:
        mlc_constituency = request.GET.get('mlc_constituency', '')
        assembly = request.GET.get('assembly', '')
        mandal = request.GET.get('mandal', '')

        # Base queryset
        queryset = Voter.objects.all()

        # Apply cascading filters
        if mlc_constituency:
            queryset = queryset.filter(mlc_constituency=mlc_constituency)
        if assembly:
            queryset = queryset.filter(assembly=assembly)
        if mandal:
            queryset = queryset.filter(mandal=mandal)

        # Get distinct values for each level
        data = {
            'mlc_constituencies': list(Voter.objects.values_list('mlc_constituency', flat=True).distinct()),
            'assemblies': list(queryset.values_list('assembly', flat=True).distinct()) if mlc_constituency else [],
            'mandals': list(queryset.values_list('mandal', flat=True).distinct()) if assembly else [],
            'villages': list(queryset.values_list('village', flat=True).distinct()) if mandal else [],
        }

        return JsonResponse({
            'success': True,
            'data': data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@staff_member_required
@require_GET
def filter_voters(request):
    try:
        mlc_constituency = request.GET.get('mlc_constituency', '')
        assembly = request.GET.get('assembly', '')
        mandal = request.GET.get('mandal', '')
        village = request.GET.get('village', '')

        queryset = Voter.objects.all()

        if mlc_constituency:
            queryset = queryset.filter(mlc_constituency=mlc_constituency)
        if assembly:
            queryset = queryset.filter(assembly=assembly)
        if mandal:
            queryset = queryset.filter(mandal=mandal)
        if village:
            queryset = queryset.filter(village=village)

        voters_data = list(queryset.values('id', 'mlc_constituency', 'assembly', 'mandal', 'village'))

        return JsonResponse({
            'success': True,
            'count': len(voters_data),
            'data': voters_data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

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