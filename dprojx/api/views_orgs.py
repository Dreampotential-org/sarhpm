from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from api.serializers import (
    OrganizationMemberSerializer
)
from rest_framework import response, status
from dappx.models import UserProfileInfo
from dappx.models import UserMonitor
from dappx.models import OrganizationMember, OrganizationMemberMonitor
from dappx.models import Organization
from dappx.notify_utils import notify_monitor
from api.serializers import (UserMonitorSerializer)

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from django.db.models import Q


class OrganizationMemberView(generics.GenericAPIView):
    queryset = OrganizationMember.objects.all()
    serializer_class = OrganizationMemberSerializer

    @swagger_auto_schema(manual_parameters=[

        openapi.Parameter('search', openapi.IN_QUERY,
                          description="Search by name and email",
                          type=openapi.TYPE_STRING,
                          required=False, default=None),

    ])
    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_anonymous:
            return response.Response("Login first",
                                     status=status.HTTP_400_BAD_REQUEST)

        org = OrganizationMember.objects.filter(user_id=user.id).first()
        if not org:
            return Response("Member not in org",
                            status=status.HTTP_201_CREATED)

        search = request.GET.get('search')
        if search:
            org_member = OrganizationMember.objects.filter(
                (Q(user__first_name__icontains=search) |
                 Q(user__email__icontains=search)) & Q(
                organization_id=org.organization_id))
        else:
            org_member = OrganizationMember.objects.filter(
                organization_id=org.organization_id)

        paginated_response = self.paginate_queryset(org_member)
        serialized = self.get_serializer(paginated_response, many=True)
        return self.get_paginated_response(serialized.data)


class UserOrganizationIDView(generics.GenericAPIView):
    queryset = OrganizationMember.objects.all()
    serializer_class = OrganizationMemberSerializer

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_anonymous:
            return response.Response("Login first", status=status.HTTP_400_BAD_REQUEST)
        else:
            org = OrganizationMember.objects.filter(user_id=user.id).first()
            org_patient = UserMonitor.objects.filter(user_id=user.id).first()
            if org is None and org_patient is None:
                data = {"organization_id": None,
                        "Patient_org_id": None}
                return response.Response(data)
            elif org and org_patient:
                data = {"organization_id": org.organization_id,
                        "Patient_org_id": org_patient.organization_id}
                return response.Response(data)
            elif org is None and org_patient:
                data = {"organization_id": None,
                        "Patient_org_id": org_patient.organization_id}
                return response.Response(data)
            elif org and org_patient is None:
                data = {"organization_id": org.organization_id,
                        "Patient_org_id": None}

                return response.Response(data)


@api_view(['POST'])
def add_member(request):
    email = request.data['email']
    name = request.data['name']
    password = request.data['password']
    admin = request.data['admin']
    try:
        organization = request.data['organization_id']
    except:
        organization = None

    '''email = 'unitednuman@hotmail.com'
    name = 'numan'
    password = 'pass@123'
    admin = 'true'
    organization = 2'''
    email = email.lower()
    if email is None or name is None or password is None or admin is None:
        data = {
            'status': False,
            'error': 'Missing parameters'
        }
        return Response(data, status=status.HTTP_400_BAD_REQUEST)
    if admin == 'true':
        value = True
    else:
        value = False
    user = User.objects.filter(email=email).first()

    if not user:
        user = User.objects.create(
            username=email,
            email=email,
            first_name=name,
            password=make_password(password)

        )
        UserProfileInfo.objects.create(
            user=user,
            name=name
        )
    user = User.objects.filter(username=email).first()
    if user:
        User.objects.filter(email=email).update(is_staff=value, first_name=name)
        org_member = OrganizationMember.objects.filter(user=user).first()
        if not org_member:
            org_member = OrganizationMember()
            org_member.user = user
            org_member.admin = value
            org_member.organization_id = organization
            org_member.save()
        else:
            return Response({
                'message': 'User is already a organization member'})

    return Response("Member Added", status=status.HTTP_201_CREATED)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_member(request):
    data = {k: v for k, v in request.data.items()}

    print(data)
    if data['is_superuser'] == 'true':
        value = True
    else:
        value = False

    data.pop("is_superuser")
    if not data.get('email') or not data.get('first_name'):
        return Response({
            'message': 'Missing parameters. Email and password is required'
        })

    data['email'] = data['email'].lower()
    try:
        user = User.objects.filter(id=data['id']).first()
        if user:
            if not data.get('password'):

                User.objects.filter(id=user.id).update(email=data['email'],
                                                       username=data['email'],
                                                       first_name=data['first_name'],
                                                       is_staff=value)

            else:

                User.objects.filter(id=user.id).update(email=data['email'],
                                                       username=data['email'],
                                                       first_name=data['first_name'],
                                                       is_staff=value,
                                                       password=make_password(data['password']))

        org_member = OrganizationMember.objects.filter(user=user).first()
        if not org_member:
            org_member = OrganizationMember()
            org_member.user = user
            org_member.admin = value
            org_member.save()
            return Response({'status': 'Member Added'}, 200)
        if org_member:
            OrganizationMember.objects.filter(user=user).update(admin=value)
            return Response({'status': 'Member Updated'}, 200)
    except:
        return Response({'status': 'Not Found '}, 404)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_member(request, id):
    user = User.objects.filter(id=id).first()
    if user:
        org_member = OrganizationMember.objects.filter(user_id=user.id).first()
        if org_member:
            org_member.delete()
            return Response({'status': 'Deleted'}, 200)
        else:
            return Response({'status': 'Not  Found'}, 204)
    else:
        return Response({'status': 'Not  Found'}, 204)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_patient(request):
    email = request.data['email']
    name = request.data['name']
    password = request.data['password']
    try:
        organization = request.data['organization_id']
    except:
        organization = None

    '''email = 'smarttest@hotmail.com'
    name = 'smart'
    password = 'pass@123'
    '''
    email = email.lower()
    if email is None or name is None or password is None:
        data = {
            'status': False,
            'error': 'Missing parameters'
        }
        return Response(data, status=status.HTTP_400_BAD_REQUEST)
    user = User.objects.filter(email=email).first()
    if not user:
        user = User.objects.create(
            username=email,
            email=email,
            first_name=name,
            password=make_password(password)

        )
        UserProfileInfo.objects.create(
            user=user,
            name=name
        )

    user = User.objects.filter(email=email).first()
    if user:
        user_monitor = UserMonitor.objects.filter(user=user).first()
        if not user_monitor:
            user_monitor = UserMonitor()
            user_monitor.user = user
            user_monitor.notify_email = email
            user_monitor.organization_id = organization
            user_monitor.save()
            notify_monitor(request, email)
            return Response({
                'msg': '%s is added as a patient and notified',
            }, 201)
        else:
            return Response({
                'msg': '%s is already a monitor user for you',
            }, 201)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_patient(request):
    data = {k: v for k, v in request.data.items()}

    print(data)
    if not data.get('email') or not data.get('first_name'):
        return Response({
            'message': 'Missing parameters. Email and name is required'
        })

    data['email'] = data['email'].lower()
    try:
        try:
            user = User.objects.filter(id=data['id']).update(email=data['email'],
                                                             username=data['email'],
                                                             first_name=data['first_name'])
        except:
            pass
        try:
            u = UserMonitor.objects.filter(user_id=user.id).first()
            UserMonitor.objects.filter(id=u.id).update(notify_email=data['email'])
        except:
            pass

        return response.Response(status=status.HTTP_200_OK)
    except:
        return response.Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def remove_patient(request):
    user = User.objects.filter(username=request.user.email).first()
    notify_email = request.data.get('notify_email')
    monitors = UserMonitor.objects.filter(user=user,
                                          notify_email=notify_email).all()
    if monitors:
        UserMonitor.objects.filter(user=user,
                                   notify_email=notify_email).delete()

    return Response({
        'status': 'okay',
    }, 201)


class UserMonitorView(generics.GenericAPIView):
    queryset = UserMonitor.objects.all()
    serializer_class = UserMonitorSerializer

    @swagger_auto_schema(manual_parameters=[

        openapi.Parameter('search', openapi.IN_QUERY,
                          description="Search by name and Email",
                          type=openapi.TYPE_STRING,
                          required=False, default=None),

    ])
    def get(self, request, *args, **kwargs):
        search = self.request.GET.get("search")
        user = request.user
        if user.is_anonymous:
            return response.Response("Login first",
                                     status=status.HTTP_400_BAD_REQUEST)

        if search:
            # xxx todo add search filter back..
            user_monitor = UserMonitor.objects.filter(
                notify_email=user.email)
        else:
            user_monitor = UserMonitor.objects.filter(
                notify_email=user.email)
        paginated_response = self.paginate_queryset(user_monitor)
        serialized = self.get_serializer(paginated_response, many=True)
        return self.get_paginated_response(serialized.data)


class UserMonitorViewDetails(generics.GenericAPIView):
    queryset = UserMonitor.objects.all()
    serializer_class = UserMonitorSerializer

    def delete(self, request, *args, **kwargs):
        if kwargs.get('id'):
            user_monitor = UserMonitor.objects.get(id=kwargs.get('id'))
            user_monitor.delete()
            return response.Response("Data Deleted",
                                     status=status.HTTP_202_ACCEPTED)
        return response.Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_org_clients(request):
    user = User.objects.filter(username=request.user.email).first()
    organization_member = OrganizationMember.objects.filter(user=user).first()
    if not organization_member:
        return Response("Member not in org",
                        status=status.HTTP_201_CREATED)

    clients = UserProfileInfo.objects.filter(
        user_org=organization_member.organization).values()

    return Response(clients)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_member_client(request):
    print("SDFDSF")
    user = User.objects.filter(username=request.user.email).first()
    organization_member = OrganizationMember.objects.filter(user=user).first()
    if not organization_member:
        return Response("Member not in org",
                        status=status.HTTP_201_CREATED)

    member_to_add_client = request.data['member_id']

    # look up member by id and see if they are in org
    user = User.objects.filter(id=int(member_to_add_client)).first()
    if not user:
        return Response("error not user", status=status.HTTP_201_CREATED)

    org_member_check = OrganizationMember.objects.filter(user=user).first()
    if org_member_check.organization.id != organization_member.organization.id:
        print("User not in org")
        return Response("error user not in org",
                        status=status.HTTP_201_CREATED)

    client = User.objects.filter(id=request.data['client_id']).first()

    organization_member_monitor = OrganizationMemberMonitor()
    organization_member_monitor.user = user
    organization_member_monitor.client = client
    organization_member_monitor.save()

    return Response("Success Added", status=status.HTTP_201_CREATED)
