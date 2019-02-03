from django.utils.deprecation import MiddlewareMixin

from main.helpers import log_analytic


class AnalyticsMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if "admin" not in request.path:
            log_analytic(request)
