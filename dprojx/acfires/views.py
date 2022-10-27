from django.http import JsonResponse

from .models import MediA

from rest_framework.decorators import api_view
from rest_framework.decorators import authentication_classes
from rest_framework_simplejwt.authentication import JWTAuthentication


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
def get_mediA(request):
    mediaAs = MediA.objects.filter()

    return JsonResponse(mediaAs)
