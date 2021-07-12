from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from dappx.models import OrganizationMember
from dappx.models import Organization
from dappx.views import _create_user
from common import config

from django.contrib.auth import get_user_model


logger = config.get_logger()

user = get_user_model()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_organization_member(request):
    data = {k: v for k, v in request.data.items()}
    if not data.get('email') or not data.get('password'):
        return Response({
            'message': 'Missing parameters. Email and password is required'
        })

    data['email'] = data['email'].lower()
    user = User.objects.filter(username=data['email']).first()

    if not user:
        _create_user(**data)

    user = User.objects.filter(username=data['email']).first()
    if user:
        org_member = OrganizationMember.objects.filter(user=user).first()
        if not org_member:
            org_member = OrganizationMember()
            org_member.user = user
            org_member.save()

        return Response({'message': 'User already exists'})

    data.pop('password')
    data['message'] = "User created"

    return Response(data)


@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def get_organization_member(request):
    orgs = OrganizationMember.objects.all()
    resp = []
    for org in orgs:
        user = User.objects.filter(id=org.user_id).first()
        resp.append({'id': org.id,
                     'user_id': org.user_id,
                     'Admin ': org.admin,
                     'Email': user.email,
                     'Name': user.first_name})

    results = sorted(resp, key=lambda i: i['id'], reverse=True)
    paginator = PageNumberPagination()
    paginator.page_size = 10
    page = paginator.paginate_queryset(results, request)
    if page is not None:
        return paginator.get_paginated_response(page)
    return Response(results)


# XXX api list clients in org
# UserProfileInfo.user_org

# XXX api map client to OrganizationMemberMonitor(s)
# API for adding
# API for Removing


# XXX API for creating Organization
# XXX api for setting logo image file

# mapping apis to page here - https://m.useiam.com/organization.html
