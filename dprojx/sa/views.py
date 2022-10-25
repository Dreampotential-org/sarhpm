import datetime
from django.http import JsonResponse

from .models import Member
from .models import MemberSession, MemberGpsEntry
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
def set_member_info(request):
    pass


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
def member_session_start(request):
    try:
        member = Member.objects.get(name=request.user)

        if not member:
            member = Member()
            member.user = request.user
            member.save()

        session_create = MemberSession.objects.create(member=member)
        member_session_start.mge = MemberGpsEntry.objects.create(
            member_session=session_create,
            latitude=request.data.get("latitude"),
            longitude=request.data.get("longitude")
        )
        return JsonResponse({'status': 'okay'}, safe=False)
    except Exception as e:
        print("e", e)
        return JsonResponse({'status': 'error'}, safe=False)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def member_session_stop(request):
    try:
        member = Member.objects.get(name=request.user)
        session_create = MemberSession.objects.filter(
            member=member
        ).last()
        session_create.ended_at = datetime.datetime.now()
        session_create.save()
        mge = MemberGpsEntry.objects.create(
            member_session=session_create,
            latitude=request.data.get("latitude"),
            longitude=request.data.get("longitude"))

        distance = get_distance(
            float(member_session_start.mge.latitude),
            float(member_session_start.mge.longitude),
            float(mge.latitude), float(mge.longitude))
        total_time = session_create.ended_at.replace(tzinfo=None) \
            - session_create.started_at.replace(tzinfo=None)
        avg_speed = (distance * 1000) / total_time.seconds

        data = {
            'distance': distance,
            'avg_speed': avg_speed,
            'total_time': total_time.seconds
        }
        return JsonResponse(data, safe=False)
    except Exception as e:
        print("🚀 ~ file: views.py ~ member_session_stop ~ e", e)
        return JsonResponse({'status': 'error'}, safe=False)
