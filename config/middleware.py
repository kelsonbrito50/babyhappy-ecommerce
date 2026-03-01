"""
Custom middleware for BabyHappy e-commerce.

SecurityHeadersMiddleware — adds enterprise-grade HTTP security headers.
"""
import logging

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware:
    """
    Inject security-related HTTP response headers.

    Headers added:
    - X-Content-Type-Options: nosniff
    - X-Frame-Options: DENY
    - Referrer-Policy: strict-origin-when-cross-origin
    - Permissions-Policy: restrict sensitive browser APIs
    - Strict-Transport-Security: HSTS (only in production / HTTPS)
    - X-XSS-Protection: 1; mode=block (legacy compatibility)

    These complement Django's own SecurityMiddleware but ensure headers are
    always present regardless of DEBUG mode.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        self._set_headers(request, response)
        return response

    def _set_headers(self, request, response):
        # Prevent MIME-type sniffing
        response.setdefault("X-Content-Type-Options", "nosniff")

        # Deny embedding in iframes (clickjacking protection)
        response.setdefault("X-Frame-Options", "DENY")

        # Control referrer information
        response.setdefault(
            "Referrer-Policy",
            "strict-origin-when-cross-origin",
        )

        # Restrict browser feature APIs
        response.setdefault(
            "Permissions-Policy",
            (
                "accelerometer=(), "
                "camera=(), "
                "geolocation=(), "
                "gyroscope=(), "
                "magnetometer=(), "
                "microphone=(), "
                "payment=(), "
                "usb=()"
            ),
        )

        # Legacy XSS protection header (IE/Edge)
        response.setdefault("X-XSS-Protection", "1; mode=block")

        # Content-Security-Policy — prevent XSS and injection attacks
        response.setdefault(
            "Content-Security-Policy",
            (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com; "
                "img-src 'self' data: https:; "
                "connect-src 'self'; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self';"
            ),
        )

        # HSTS — only add when the request came in over HTTPS
        is_secure = (
            request.is_secure()
            or request.META.get("HTTP_X_FORWARDED_PROTO") == "https"
        )
        if is_secure:
            response.setdefault(
                "Strict-Transport-Security",
                "max-age=31536000; includeSubDomains; preload",
            )
