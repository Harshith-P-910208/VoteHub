import traceback
from django.http import HttpResponse

class GlobalErrorHandlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception:
            # Catch ALL errors and show traceback
            error_msg = traceback.format_exc()
            return HttpResponse(
                f"<html><body><h1>CRITICAL SERVER ERROR (Debug Mode - Status 200)</h1><pre>{error_msg}</pre></body></html>",
                status=200 # Force 200 to bypass Vercel's 500 page
            )

    def process_exception(self, request, exception):
        # Also catch view exceptions
        error_msg = traceback.format_exc()
        return HttpResponse(
            f"<html><body><h1>VIEW EXCEPTION (Debug Mode)</h1><pre>{error_msg}</pre></body></html>",
            status=500
        )
