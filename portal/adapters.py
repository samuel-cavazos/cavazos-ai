from urllib.parse import urlencode

from allauth.account.adapter import DefaultAccountAdapter
from allauth.core.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.urls import reverse


class PortalAccountAdapter(DefaultAccountAdapter):
    """Redirect account and social-account logins to the landing page."""

    def get_login_redirect_url(self, request):
        return reverse("portal:home")


class PortalSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Restrict Microsoft sign-in to an allowlist of pre-provisioned superusers."""

    def _extract_email(self, sociallogin) -> str:
        candidate = (
            sociallogin.user.email
            or sociallogin.account.extra_data.get("email")
            or sociallogin.account.extra_data.get("preferred_username")
            or sociallogin.account.extra_data.get("upn")
            or ""
        )
        return str(candidate).strip().lower()

    def _abort(self, message: str):
        query = urlencode({"social_error": message})
        target = f"{reverse('portal:home')}?{query}"
        raise ImmediateHttpResponse(HttpResponseRedirect(target))

    def pre_social_login(self, request, sociallogin):
        if sociallogin.account.provider != "microsoft":
            return

        email = self._extract_email(sociallogin)
        if not email:
            self._abort("Unable to read email from Microsoft identity.")

        allowed_emails = {email.lower() for email in settings.MICROSOFT_ALLOWED_EMAILS}
        if email not in allowed_emails:
            self._abort("This Microsoft account is not allowed for admin login.")

        user_model = get_user_model()
        matched_user = user_model.objects.filter(email__iexact=email).first()
        if matched_user is None:
            self._abort("No local portal account is provisioned for this Microsoft identity.")
        if not matched_user.is_superuser:
            self._abort("Only superuser accounts can use Microsoft login right now.")

        if sociallogin.is_existing:
            return
        sociallogin.connect(request, matched_user)

    def on_authentication_error(self, request, provider, error=None, exception=None, extra_context=None):
        self._abort("Microsoft authentication failed. Please try again.")
