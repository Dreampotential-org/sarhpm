from django.http import HttpResponse


def superuser_only(function):
    def _inner(request, *args, **kwargs):
        if not request.user.is_superuser:
            return HttpResponse('Admin access required')
        return function(request, *args, **kwargs)
    return _inner
