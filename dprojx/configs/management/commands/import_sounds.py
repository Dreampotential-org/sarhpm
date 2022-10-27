import uuid
from django.core.management.base import BaseCommand
from configs.models import MediA
from django.core.files import File

from pytube import YouTube


def create_sound_file():
    directory = str(uuid.uuid4())

    yt = YouTube(
        "https://www.youtube.com/watch?v=PGc9n6BiWXA&list=RDyjki-9Pthh0&index=9")
    yt.streams.filter(
        progressive=True, file_extension='mp4'
    ).order_by('resolution').desc().first().download(
        "/tmp/%s/" % directory
    )
    video = "/tmp/%s/%s" % (directory, yt.title)
    sound = MediA()
    sound.file = File(video)
    sound.path = video
    sound.name = yt.title
    sound.save()


class Command(BaseCommand):
    help = 'fetch and parse iwlist'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        create_sound_file()
