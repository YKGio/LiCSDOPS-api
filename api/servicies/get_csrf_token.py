from django.middleware import csrf

class GetCSRFToken:
    def __init__(self, request):
        self.request = request

    def call(self):
        csrf_cookie_name = csrf.get_token(self.request)

        csrf_token = self.request.COOKIES.get(csrf_cookie_name)

        return csrf_token
