from django.http import HttpResponse


def superuser_only(function):
    def _inner(request, *args, **kwargs):
        if not request.user.is_superuser:
            return HttpResponse(
                'Admin access required <a href="/admin">Admin Login</a>')
        return function(request, *args, **kwargs)
    return _inner
