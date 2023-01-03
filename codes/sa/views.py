import json
import datetime
from django.http import JsonResponse

from .models import Session, SessionPoint, Device, Dot
from math import sin, cos, sqrt, atan2, radians

from rest_framework.decorators import api_view
from rest_framework.decorators import authentication_classes
from rest_framework.decorators import permission_classes

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.core.serializers import serialize
from .serializer import *

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
def set_profile_info(request):
    pass


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
def get_distances(request):

    # here we calculate on server side..
    dots = Dot.objects.filter()
    session_point = SessionPoint.objects.filter().last()
    print("session point...%s" % session_point)

    if not session_point:
        return JsonResponse({'dots': []}, safe=False)

    res = []
    for dot in dots:
        res.append({'id': dot.id,
                    'distance': get_distance(dot.latitude, dot.longitude,
                                             session_point.latitude,
                                             session_point.longitude)})

    print("Number of dots: %s" % len(dots))
    return JsonResponse({'dots': res}, safe=False)




def get_sp_distance(session_points):
    if not session_points:
        return 0

    session_distance = 0
    for i in range(0, len(session_points) - 1):
        print(session_points[i].latitude, session_points[i].longitude)
        session_distance += get_distance(
            session_points[i].latitude, session_points[i].longitude,
            session_points[i + 1 ].latitude, session_points[i +1].longitude
        )

    return session_distance


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
def get_session_stats(request):

    total_session_points = SessionPoint.objects.filter().count()

    device = Device.objects.filter(
        key=request.GET.get("device_id")
    ).first()

    sessions = Session.objects.filter(
        device=device
    ).order_by("-id")

    session_response = []

    for session in sessions:
        print("HELLO WE ARE HERE>..")
        print(session)
        #session_response['id'] = session.id


        session_points_device = SessionPoint.objects.filter(
            device__key=request.GET.get("device_id")
        ).order_by("-id")

        session_points_device_info = SessionPointserializer(session_points_device , partial = True)
        
        session_points = SessionPoint.objects.filter(
            session=session
        ).order_by("-id")

        print(session_points)

        km_for_session = get_sp_distance(session_points)                 
        session_miles_meter = {'miles' : km_for_session*0.62137, 'meter': km_for_session *1000}

        km_for_device = get_sp_distance(session_points_device)
        device_miles_meter = {'miles' : km_for_device*0.62137, 'meter': km_for_device *1000}

        session_response.append({
            'session_points_device_count': session_points_device_info.data,
            'session_points': [{'lat': session_point.latitude,
                                'lng': session_point.longitude}
                                for session_point in session_points],
            'session_distance': session_miles_meter,
            "device_distances":  device_miles_meter,
            "session_id": session.id,
            "points_count": len(session_points),
            "session_time": session.started_at
        })


    # session_points = serialize("json", session_points)
    # session_points = json.loads(session_points)

    return JsonResponse({
        'status': 'okay',
        'query_device_id': request.GET.get("device_id"),
        "system_session_points": total_session_points,
        "device_session_points": len(sessions),
        'sessions_stats': session_response}, safe=False
    )



@api_view(['POST'])
@authentication_classes([JWTAuthentication])
def start(request):
    session = Session.objects.create()
    session.save()

    # if device does not exist when session is started
    # it is created here
    print(request.data)
    device_id = request.data.get("device_id")
    print(device_id)
    print(type(device_id))
    device = Device.objects.filter(key=device_id).first()
    if not device:
        device = Device()
        device.key = device_id
        device.save()

    session.device = device
    session.save()

    return JsonResponse({'status': 'okay',
                         'session_id': session.id}, safe=False)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
def session_point(request):

    # XXX optimize this lookup.
    # print(request.data.get("session_id"))
    session = Session.objects.get(id=request.data.get("session_id"))
    # print("found session %s" % session)
    device = Device.objects.filter(
       key=request.data.get("device_id"))[0]

    session_point = SessionPoint()
    session_point.session = session
    session_point.device = device

    session_point.latitude = request.data.get("latitude")
    session_point.longitude = request.data.get("longitude")
    session_point.save()


    print("creating session_point %s" % session_point.id)

    return JsonResponse({'status': 'okay'}, safe=False)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def stop(request):
    session_create = Session.objects.filter().last()
    session_create.ended_at = datetime.datetime.now()
    session_create.save()
    return JsonResponse({'status': 'k'},  safe=False)
