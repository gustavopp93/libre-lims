from django.shortcuts import redirect
from django.urls import reverse

from .models import Company


class CompanyRequiredMiddleware:
    """
    Middleware to ensure a company exists before allowing access to the application.
    If user is authenticated and no company exists, redirect to company creation page.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip check for unauthenticated users
        if not request.user.is_authenticated:
            return self.get_response(request)

        # Paths that should be accessible even without a company
        allowed_paths = [
            reverse("company_create"),
            reverse("logout"),
        ]

        # Check if current path is in allowed paths
        current_path = request.path
        is_allowed = any(current_path.startswith(path) for path in allowed_paths)

        if is_allowed:
            return self.get_response(request)

        # Check if company exists
        if not Company.objects.exists():
            # Redirect to company creation if not already there
            if current_path != reverse("company_create"):
                return redirect("company_create")

        response = self.get_response(request)
        return response
