from django.contrib import admin

from dappx.models import UserProfileInfo
from dappx.models import User
from dappx.models import VideoUpload

from django.utils.html import format_html

class CustomVideoUpload(admin.ModelAdmin):
    list_display = ['id', 'user', 'display_link']

    def display_link(self, obj):
        return format_html(
            '<a href="%s" target="_blank">%s</a>' % (
                obj.videoUrl, obj.videoUrl))

    display_link.mark_safe = True
    display_link.short_description = "URL"
    list_filter = ['user']
    model = VideoUpload




# Register your models here.
admin.site.register(UserProfileInfo)
admin.site.register(VideoUpload, CustomVideoUpload)


