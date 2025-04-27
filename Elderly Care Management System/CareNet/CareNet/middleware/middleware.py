from django.shortcuts import redirect
from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin

EXEMPT_PATHS = ['/login/', '/logout/', '/create_user/', '/static/']

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith(tuple(EXEMPT_PATHS)):
            return self.get_response(request)

        if not request.session.get('username'):
            if not request.path.startswith('/login/'):
                messages.warning(request, "Your session has expired. Please log in again.")
            return redirect('login')

        return self.get_response(request)

class NoCacheMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response