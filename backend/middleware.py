# myapp/middleware.py
from django.urls import resolve
from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.utils.deprecation import MiddlewareMixin
from django.utils.timezone import now

from backend.models import CustomUser

class AuthRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    # def __call__(self, request):
    #     # Allow access to login and register pages without authentication
    #     if request.path not in [reverse('login'), reverse('register')] and not request.user.is_authenticated:
    #         return redirect('login')
    #
    #     response = self.get_response(request)
    #     return response

    def __call__(self, request):
        try:
            # Check if the URL can be resolved
            resolve(request.path)
        except:
            # If the URL is invalid, redirect to login if the user is not authenticated
            if not request.user.is_authenticated:
                # return redirect_to_login(request.path, settings.LOGIN_URL)
                return redirect_to_login(request.path, settings.BASE_URL)
        response = self.get_response(request)
        return response


class SetLastVisitMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if request.user.is_authenticated:
            # Update last visit time after request finished processing.
            CustomUser.objects.filter(pk=request.user.pk).update(last_login=now())
        return response
    

