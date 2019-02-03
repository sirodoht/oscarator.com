from django.contrib.auth.models import User

from main import models


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def log_analytic(request):
    new_analytic = models.Analytic(
        querystring=request.GET.urlencode(),
        ip=get_client_ip(request),
        path=request.path,
    )
    if request.user.is_authenticated:
        new_analytic.user = User.objects.get(id=request.user.id)
    new_analytic.save()
