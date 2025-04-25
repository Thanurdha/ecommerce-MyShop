from django.utils.deprecation import MiddlewareMixin
from django.utils.cache import add_never_cache_headers

class DisableBrowserBackMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        add_never_cache_headers(response)
        return response
