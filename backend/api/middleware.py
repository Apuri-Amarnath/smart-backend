from django.utils.deprecation import MiddlewareMixin


class CollegeContextMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            request.college = request.user.college
        else:
            request.college = None
