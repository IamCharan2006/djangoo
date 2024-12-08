from django.shortcuts import redirect
from django.urls import resolve

class UserRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            current_url = resolve(request.path_info).url_name
            if current_url == 'HomePage':
                if hasattr(request.user, 'restaurantprofile'):
                    return redirect('restaurant:dashboard')
                else:
                    return redirect('user:dashboard')
        return self.get_response(request) 