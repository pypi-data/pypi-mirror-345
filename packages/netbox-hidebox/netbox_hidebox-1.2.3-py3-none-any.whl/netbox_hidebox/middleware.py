from asgiref.local import Local

request_local = Local()


class RequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_local.request = request
        response = self.get_response(request)
        return response


def get_current_request():
    return getattr(request_local, 'request', None)
