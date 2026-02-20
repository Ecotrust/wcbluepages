from django.conf import settings
from django.http import HttpResponseRedirect


class LoginRequiredMiddleware:
    """
    Middleware that requires authentication for all pages except for login-related URLs
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # URLs that should be accessible without authentication
        exempt_urls = [
            "/accounts/login/",
            "/accounts/logout/",
            "/accounts/register/",
            "/accounts/forgot/",
            "/accounts/reset/",
            "/accounts/password_reset/",
            "/accounts/password_reset/done/",
            "/admin/login/",
        ]

        is_exempt = any(request.path.startswith(url) for url in exempt_urls)

        is_static = (
            request.path.startswith(settings.STATIC_URL)
            if hasattr(settings, "STATIC_URL")
            else False
        )
        is_media = (
            request.path.startswith(settings.MEDIA_URL)
            if hasattr(settings, "MEDIA_URL")
            else False
        )
        is_admin_static = request.path.startswith("/static/admin/")

        # If user is not authenticated and trying to access a protected URL
        if (
            not request.user.is_authenticated
            and not is_exempt
            and not is_static
            and not is_media
            and not is_admin_static
        ):
            login_url = "/accounts/login/"
            return HttpResponseRedirect(login_url)

        response = self.get_response(request)
        return response
