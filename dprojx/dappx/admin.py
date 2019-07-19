from django.contrib import admin

from dappx.models import UserProfileInfo
from dappx.models import GpsCheckin
from dappx.models import User
from dappx.models import VideoUpload

from django.utils.html import format_html


class CustomVideoUpload(admin.ModelAdmin):
    list_display = ['id', 'user', 'display_link', 'uploaded_at']

    def display_link(self, obj):
        user_hash = obj.videoUrl.split("/media/")[1].split("/")[0]
        video_id = obj.videoUrl[7:].split("/", 1)[1]
        url = '/video?id=%s&user=%s' % (video_id, user_hash)
        return format_html(
            '<video controls="" name="media" width="320" height="240">'
            '<source src="/video/?id=%s&amp;user=%s" type="video/mp4"></video>'
            % (video_id, user_hash)
        )

        return format_html(
            '<a href="%s" target="_blank">Play Video</a>' % (url)
        )

    display_link.mark_safe = True
    display_link.short_description = "URL"
    list_filter = ['user']
    model = VideoUpload


class CustomGpsCheckin(admin.ModelAdmin):
    list_display = ['id', 'msg', 'user']
    list_filter = ['user']
    model = GpsCheckin

    def user(self, obj):
        return obj.user.name

    def view_map(self, obj):
        print(obj.lat)
        print(obj.lng)

        map_url = 'https://www.google.com/maps/place/'
        map_url += "%s,%s" % (obj.lat, obj.lng)

        return format_html(
            '<a href="%s" target="_blank">View Map</a>' % map_url
        )


class UserProfileInfoAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'notify_email', 'created_at'
    ]
    ordering = ('-id',)


# Register your models here.
admin.site.register(UserProfileInfo, UserProfileInfoAdmin)
admin.site.register(GpsCheckin, CustomGpsCheckin)
admin.site.register(VideoUpload, CustomVideoUpload)
