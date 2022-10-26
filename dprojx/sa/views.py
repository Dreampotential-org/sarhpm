import datetime
from django.http import JsonResponse

from .models import Session, SessionPoint
from math import sin, cos, sqrt, atan2, radians

from rest_framework.decorators import api_view
from rest_framework.decorators import authentication_classes
from rest_framework.decorators import permission_classes

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated


def get_distance(lat1, lon1, lat2, lon2):
    R = 6373.0
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
def set_profile_info(request):
    pass


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
def start(request):
    session = Session.objects.create()

    return JsonResponse({'status': 'okay',
                         'session_id': session.id}, safe=False)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
def session_point(request):
    session_point = SessionPoint()
    session_point.latitude = request.data.get("latitude")
    session_point.longitude = request.data.get("longitude")
    session_point.save()

    return JsonResponse({'status': 'okay'}, safe=False)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def stop(request):
    session_create = Session.objects.filter().last()
    session_create.ended_at = datetime.datetime.now()
    session_create.save()
    return JsonResponse({'status': 'k'},  safe=False)
