from django.contrib import admin

from dappx.models import UserProfileInfo
from dappx.models import GpsCheckin
from dappx.models import User
from dappx.models import VideoUpload

from django.utils.html import format_html

class CustomVideoUpload(admin.ModelAdmin):
    list_display = ['id', 'user', 'display_link', 'uploaded_at']

    def display_link(self, obj):
        return format_html(
            '<a href="%s" target="_blank">%s</a>' % (
                obj.videoUrl, obj.videoUrl))

    display_link.mark_safe = True
    display_link.short_description = "URL"
    list_filter = ['user']
    model = VideoUpload

class CustomGpsCheckin(admin.ModelAdmin):
    list_display = ['user', 'lat', 'lng', 'user']
    list_filter = ['user']
    model = GpsCheckin




# Register your models here.
admin.site.register(UserProfileInfo)
admin.site.register(GpsCheckin, CustomGpsCheckin)
admin.site.register(VideoUpload, CustomVideoUpload)


