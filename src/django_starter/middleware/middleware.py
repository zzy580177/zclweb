# 在你的中间件中
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

class CustomMiddleware(MiddlewareMixin):
    def process_request(self, request):
        user = request.user
        if user.is_authenticated:
            setattr(settings, 'LOGGED_IN_USER', user)