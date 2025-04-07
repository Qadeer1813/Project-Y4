from django.shortcuts import redirect

EXEMPT_PATHS = ['/login/', '/logout/', '/create-user/', '/static/']

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            not request.path.startswith(tuple(EXEMPT_PATHS))
            and not request.session.get('username')
        ):
            return redirect('login')

        return self.get_response(request)
