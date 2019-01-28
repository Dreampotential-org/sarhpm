import uuid
import requests
import logging
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render

from dappx.forms import UserForm, UserProfileInfoForm
from dappx.forms import email_utils
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import VideoUpload
from .models import GpsCheckin
from .models import UserProfileInfo
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_200_OK
)
from rest_framework.response import Response

logger = logging.getLogger(__name__)


def register(request):
    return render(request, 'dappx/index.html')


@login_required
def special(request):
    return HttpResponse("You are logged in !")


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


def record_video_screen(request):
    return render(request, 'dappx/record.html')


@csrf_exempt
def gps_check_in(request):
    if request.method == 'GET':
        return render(request, 'dappx/gps-event.html')

    if request.method == 'POST':
        print ("A CHECKIN HAS OCC")
        print (request.POST)

        msg = request.POST.get("msg")
        lat = request.POST.get("lat")
        lng = request.POST.get("long")

        user = User.objects.get(id=request.user.id)
        GpsCheckin.objects.create(lat=lat, lng=lng, msg=msg,
                                  user=user)

        profile = _get_user_profile(request)
        print (profile.notify_email)

        email_utils.send_email(
            profile.notify_email,
            'Hi there', msg)

        url = 'https://hooks.slack.com/services/'
        url += 'TF6H12JQY/BFJHJFSN5/Zeodnz8HPIR4La9fq5J46dKF'
        data = (str("GspCheckin: %s - %s (%s, %s)" %
                (request.user.email, msg, lat, lng)))
        body = {"text": "%s" % data,
                'username': 'pam-server'}
        requests.put(url, data=json.dumps(body))

        return JsonResponse({'status': 'okay'}, status=200)


def _get_user_profile(request):
    users = (UserProfileInfo.objects.all())
    if request.user and getattr(request.user, 'email', None):
        for user in users:
            if user.user.email == request.user.email:
                return user


@csrf_exempt
def post_slack_errors(request):
    url = 'https://hooks.slack.com/services/'
    url += 'TF6H12JQY/BF6H2L0M6/RMuFLttV91aKvlUXydV2yJgv'
    data = (str(request.POST))
    body = {"text": "%s" % data,
            'username': 'js-logger'}
    requests.put(url, data=json.dumps(body))

    return JsonResponse({'error': 'Some error'}, status=200)


@csrf_exempt
@login_required
def upload(request):

    if request.method == 'POST' and request.FILES['file']:
        # save file to disk
        myfile = request.FILES['file']
        fs = FileSystemStorage()
        filename = fs.save("%s-%s" % (uuid.uuid4(), myfile.name), myfile)
        uploaded_file_url = fs.url(filename)
        print (uploaded_file_url)
        # now lets create the db entry

        user = User.objects.get(id=request.user.id)
        VideoUpload.objects.create(videoUrl=uploaded_file_url,
                                   user=user)

        url = 'https://hooks.slack.com/services/'
        url += 'TF6H12JQY/BFJHJFSN5/Zeodnz8HPIR4La9fq5J46dKF'
        data = (str("VideoUpload: %s - https://app.usepam.com%s" %
                (request.user.email, uploaded_file_url)))
        body = {"text": "%s" % data,
                'username': 'pam-server'}
        requests.put(url, data=json.dumps(body))

        return JsonResponse({'error': 'Some error'}, status=200)


# @csrf_exempt
@login_required
def record_video(request):
    print (request.user)
    files = request.data.get("file")
    userId = request.data.get('userId')
    fs = FileSystemStorage()
    try:
        filename = fs.save(files.name, files)
        uploaded_file_url = fs.url(filename)
    except Exception:
        logger.exception("Error")
        return Response({'error': 'Error uploading file'},
                        status=HTTP_400_BAD_REQUEST)
    print(type(files))
    print(uploaded_file_url)

    user = User.objects.get(id=userId)
    try:
        VideoUpload.objects.create(videoUrl=uploaded_file_url,
                                   user=user)
    except Exception:
        logger.exception("Error")
        return Response({'error': 'Error uploading file'},
                        status=HTTP_400_BAD_REQUEST)

    return Response({
        'message', 'Success'
    }, status=HTTP_200_OK)


def index(request):
    print (request.user.id)
    registered = False
    name = ''
    if request.method == 'POST':
        #request.POST['username'] = request.POST.get('email')
        print ("Create user request!!!")
        print (request.POST)
        data = request.POST.copy()
        data['username'] = request.POST.get('email')
        print ('after')
        print (data)
        user_form = UserForm(data)
        profile_form = UserProfileInfoForm(data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.phone = request.POST.get("phone", "")
            profile.name = request.POST.get("name", "")
            profile.notify_email = request.POST.get("notify_email", "")
            profile.save()
            registered = True

            # log user in!
            username = request.POST.get('email')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return HttpResponseRedirect(reverse('index'))

        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileInfoForm()
        # need to get the name XXX fix this
        profile = _get_user_profile(request)
        name = profile.name

    return render(request, 'dappx/index.html',
                           {'user_form': user_form,
                            'profile_form': profile_form,
                            'name': name,
                            'registered': registered})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                return HttpResponse("Your account was inactive.")
        else:
            print("Someone tried to login and failed.")
            print("They used username: {} and password: {}".format(
                username, password))
            return HttpResponse("Invalid login details given")
    else:
        return render(request, 'dappx/login.html', {})
