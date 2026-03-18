from rest_framework import authentication, exceptions

from .models import AuthToken


class BearerTokenAuthentication(authentication.BaseAuthentication):
    keyword = 'Bearer'

    def authenticate(self, request):
        header = authentication.get_authorization_header(request).decode('utf-8')
        if not header:
            return None

        parts = header.split()
        if len(parts) != 2 or parts[0] != self.keyword:
            return None

        try:
            token = AuthToken.objects.select_related('user').get(key=parts[1])
        except AuthToken.DoesNotExist as exc:
            raise exceptions.AuthenticationFailed('Invalid authentication token.') from exc

        return (token.user, token)
