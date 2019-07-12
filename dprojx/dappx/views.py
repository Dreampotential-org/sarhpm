import datetime
import hashlib
import json
import logging
import mimetypes
import os
import requests
import uuid

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.http import JsonResponse
from django.http.response import StreamingHttpResponse
# from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK
from wsgiref.util import FileWrapper

from . import email_utils
from . import video_utils
from .models import GpsCheckin
from .models import UserProfileInfo
from .models import VideoUpload
from dappx.forms import UserForm, UserProfileInfoForm
from utils import superuser_only
from utils import custom_render as render


logger = logging.getLogger(__name__)


def register(request):
    return render(request, 'dappx/index.html')


@superuser_only
def video(request):
    path = '/media/%s/%s' % (request.GET.get("user"), request.GET.get("id"))
    return stream_video(request, path)


@login_required
def video_monitor(request):
    logger.error("View video request from: %s" % request.user)
    path = '/media/%s/%s' % (request.GET.get("user"), request.GET.get("id"))
    video = VideoUpload.objects.filter(videoUrl=path).first()

    if not video:
        raise Http404

    if video and request.user.is_superuser:
        return stream_video(request, path)

    video_owner = UserProfileInfo.objects.filter(user=video.user).first()
    monitor_user = UserProfileInfo.objects.filter(
        user__email=video_owner.notify_email
    ).first()

    if monitor_user:
        logger.info("monitor user for video is: %s" % monitor_user)
    else:
        logger.info("no monitor user")

    if monitor_user and monitor_user.user.email != request.user.email:
        raise Http404

    return stream_video(request, path)


@login_required
def special(request):
    return HttpResponse("You are logged in !")


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


@login_required
def monitor(request):
    user_ids = [
        user.user.id for user in UserProfileInfo.objects.filter(
            notify_email=request.user.email)
    ]
    videos = VideoUpload.objects.filter(user__id__in=user_ids)

    return render(request, 'dappx/monitor.html', {'videos': videos})


def record_video_screen(request):
    return render(request, 'dappx/record.html')


def save_checkin(request):
    msg = request.POST.get("msg")
    lat = request.POST.get("lat")
    lng = request.POST.get("long")

    if not all([msg, lat, lng]):
        return False

    user = User.objects.get(id=request.user.id)
    GpsCheckin.objects.create(lat=lat, lng=lng, msg=msg, user=user)

    lat_long_url = 'https://www.google.com/maps/place/%s,%s' % (lat, lng)
    msg += "\n\n\n%s" % lat_long_url

    profile = get_user_profile(request)
    if hasattr(profile, 'notify_email') and profile.notify_email:
        email_utils.send_raw_email(
            profile.notify_email,  # send report here
            request.user.email,  # replies to goes here
            'GPS Checkin from %s' % profile.name,
            msg)

    url = 'https://hooks.slack.com/services/'
    url += 'TF6H12JQY/BFJHJFSN5/Zeodnz8HPIR4La9fq5J46dKF'
    data = "GspCheckin: %s - %s (%s, %s)" % (request.user.email, msg, lat, lng)
    data += "\nSite: %s" % request.META['HTTP_HOST']

    body = {"text": "%s" % data, 'username': 'pam-server'}
    requests.put(url, data=json.dumps(body))


@csrf_exempt
@login_required
def gps_check_in(request):

    if request.method == 'GET':
        return render(request, 'dappx/gps-event.html')

    if request.method == 'POST':
        save_checkin(request)
        return JsonResponse({'status': 'okay'}, status=200)


def get_user_profile(request):
    if not hasattr(request.user, 'email'):
        return False

    return UserProfileInfo.objects.filter(
        user__username=request.user.email
    ).first()


def days_sober(date_joined):
    date_joined = (str(date_joined).split(" "))[0].split("-")
    current = datetime.datetime.now()
    joined = datetime.datetime(int(date_joined[0]),
                               int(date_joined[1]),
                               int(date_joined[2]))
    return (current - joined).days


@csrf_exempt
def post_slack_errors(request):
    url = 'https://hooks.slack.com/services/'
    url += 'TF6H12JQY/BF6H2L0M6/RMuFLttV91aKvlUXydV2yJgv'
    data = (str(request.POST))
    data += '\nSite: %s' % request.META['HTTP_HOST']
    body = {"text": "%s" % data,
            'username': 'js-logger'}

    requests.put(url, data=json.dumps(body))

    return JsonResponse({'error': 'Some error'}, status=200)


def convert_file(uploaded_file_url):
    outfile = "%s.mp4" % uploaded_file_url.rsplit(".", 1)[0]
    command = (
        'avconv -i ./%s -codec copy ./%s' % (uploaded_file_url, outfile)
    )
    print(command)
    os.system(command)
    return outfile


def stream_video(request, path):
    path = settings.BASE_DIR + path
    range_header = request.META.get('HTTP_RANGE', '').strip()
    range_match = video_utils.range_re.match(range_header)
    size = os.path.getsize(path)
    content_type, encoding = mimetypes.guess_type(path)
    content_type = content_type or 'application/octet-stream'
    if range_match:
        first_byte, last_byte = range_match.groups()
        first_byte = int(first_byte) if first_byte else 0
        last_byte = int(last_byte) if last_byte else size - 1
        if last_byte >= size:
            last_byte = size - 1
        length = last_byte - first_byte + 1
        resp = StreamingHttpResponse(video_utils.RangeFileWrapper(
            open(path, 'rb'), offset=first_byte, length=length), status=206,
            content_type=content_type
        )
        resp['Content-Length'] = str(length)
        resp['Content-Range'] = 'bytes %s-%s/%s' % (first_byte, last_byte,
                                                    size)
    else:
        resp = StreamingHttpResponse(
            FileWrapper(open(path, 'rb')), content_type=content_type)
        resp['Content-Length'] = str(size)
    resp['Accept-Ranges'] = 'bytes'
    return resp


@csrf_exempt
@login_required
def upload(request):
    if request.method == 'POST' and request.FILES['file']:
        logger.info("Video upload: %s" % request.POST)
        save_checkin(request)

        # save file to disk
        myfile = request.FILES['file']
        fs = FileSystemStorage()
        user_hash = hashlib.sha1(
            request.user.email.encode('utf-8')
        ).hexdigest()
        uploaded_name = (
            "%s/%s-%s" % (user_hash, uuid.uuid4(), myfile.name)
        ).lower()

        filename = fs.save(uploaded_name, myfile)
        uploaded_file_url = fs.url(filename)
        print(uploaded_name)
        if uploaded_name[-4:] == '.mov':
            # ffmpeg!
            uploaded_file_url = convert_file(uploaded_file_url)

        print(uploaded_file_url)
        # now lets create the db entry
        user = User.objects.get(id=request.user.id)
        video = VideoUpload.objects.create(
            videoUrl=uploaded_file_url, user=user
        )

        profile = get_user_profile(request)
        msg = (
            'Click to play: https://%s' %
            video.video_monitor_link()
        )

        if hasattr(profile, 'notify_email') and profile.notify_email:
            email_utils.send_raw_email(
                profile.notify_email,  # send report here
                request.user.email,  # replies to goes here
                'Video Checkin from %s' % profile.name,
                msg
            )

        url = 'https://hooks.slack.com/services/'
        url += 'TF6H12JQY/BFJHJFSN5/Zeodnz8HPIR4La9fq5J46dKF'
        data = (
            str("VideoUpload: %s - https://%s%s" % (
                request.user.email,
                request.META['HTTP_HOST'],
                uploaded_file_url)
                ))
        body = {"text": "%s" % data, 'username': 'pam-server'}
        requests.put(url, data=json.dumps(body))

        return JsonResponse({'error': 'Some error'}, status=200)


# @csrf_exempt
@login_required
def record_video(request):
    print(request.user)
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


existing_monitor_message = (
    "Hi there, I have added you to monitor my recovery process "
    "and help keep me accountable using https://useiam.com. "
    "You will receieve video and gps checkins of my activity which "
    "you can reply to via email to help encourage me.")

new_monitor_message = (
    "Hi there, I have added you to monitor my recovery process "
    "and help keep me accountable using https://useiam.com. "
    "You will receieve video and gps checkins of my activity which "
    "you can reply to via email to help encourage me. "

    )


def _create_user(request):
    data = request.POST.copy()
    data['username'] = request.POST.get('email')
    # check if notify email has an account
    notify_email = request.POST.get('notify_email', '')
    monitor_user = None
    if notify_email != '':
        monitor_user = User.objects.filter(
            username=request.POST.get("notify_email", "")
        ).first()

    user_form = UserForm(data)
    profile_form = UserProfileInfoForm(data=request.POST)
    if user_form.is_valid() and profile_form.is_valid():
        user = user_form.save()
        print("UERERERE %s" % user)
        user.set_password(user.password)
        user.save()
        profile = profile_form.save(commit=False)
        profile.user = user
        profile.phone = request.POST.get("phone", "")
        profile.days_sober = request.POST.get("days_sober", 0)
        profile.name = request.POST.get("name", "")
        profile.notify_email = request.POST.get("notify_email", "")
        profile.save()

        # log user in!
        username = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if monitor_user:
            logger.info("I HAVE MONITOR USER")
            email_utils.send_raw_email(
                to_email=request.POST["notify_email"],
                reply_to=request.POST['email'],
                subject='useIAM: %s added you as a monitor'
                        % request.POST['name'],
                message=existing_monitor_message)
        elif notify_email != '':
            url = "https://" + request.META['HTTP_HOST']
            url += "/create_notify_user/" + profile.user_hash
            mail_text = new_monitor_message + url
            email_utils.send_raw_email(
                to_email=request.POST["notify_email"],
                reply_to=request.POST['email'],
                subject='useIAM: %s added you as a monitor'
                        % request.POST['name'],
                message=mail_text)

        if user:
            login(request, user)
            return HttpResponseRedirect(reverse('index'))

    elif (user_form.errors):
        return 'error'


def index(request):
    registered = False
    user_taken = False
    name = ''
    if request.method == 'POST':
        user = _create_user(request)
        if user == 'error':
            user_taken = True
        else:
            return user

    user_form = UserForm()
    profile_form = UserProfileInfoForm()
    # need to get the name XXX fix this
    profile = get_user_profile(request)
    sober_days = 0
    if profile:
        name = profile.name
        print(dir(profile))
        print(profile.days_sober)
        sober_days = (profile.days_sober +
                      days_sober(profile.user.date_joined))

    return render(request, 'dappx/index.html',
                  {'user_form': user_form,
                   'profile_form': profile_form,
                   'user_taken': user_taken,
                   'sober_days': sober_days,
                   'name': name,
                   'registered': registered})


def create_notify_user(request, user_hash):
    profile = get_object_or_404(UserProfileInfo, user_hash=user_hash)
    if request.method == 'POST':
        # username = request.POST.get('email')
        username = profile.notify_email
        password = request.POST.get('password')

        user = User.objects.filter(username=username).first()
        if user:
            return HttpResponse('Email already exists')

        user = User()
        user.email = username
        user.username = username
        user.set_password(password)
        user.save()

        profile = UserProfileInfo()
        profile.user = user
        profile.save()

        user = authenticate(username=username, password=password)
        login(request, user)

        return HttpResponseRedirect(reverse('monitor'))

    return render(
        request, 'dappx/create_notify_user.html',
        {'username': profile.notify_email}
    )


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('email')
        password = request.POST.get('password')
        notify_email = request.POST.get('notify_email', '')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                if notify_email:
                    profile = get_user_profile(request)
                    profile.notify_email = notify_email
                    profile.save()
                # update notify_email

                if request.GET.get('next'):
                    full_path = request.get_full_path()
                    val = full_path.split('next=')
                    redirect_uri = val[1]
                else:
                    redirect_uri = reverse('index')

                return HttpResponseRedirect(redirect_uri)
            else:
                return HttpResponse("Your account was inactive.")
        else:
            print("Someone tried to login and failed.")
            print("They used username: {} and password: {}".format(
                username, password))
            return HttpResponse("Invalid login details given")

    return render(request, 'dappx/login.html', {})
