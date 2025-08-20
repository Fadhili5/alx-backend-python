# chats/auth.py
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from django.contrib.auth import get_user_model

class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        User = get_user_model()
        user_id = validated_token.get('user_id')  # Matches USER_ID_CLAIM
        if user_id is None:
            raise InvalidToken("Token contained no recognizable user identification")

        try:
            user = User.objects.get(id=user_id)  # Explicitly use user_id
            if not user.is_active:
                raise AuthenticationFailed("User is inactive", code="user_inactive")
            return user
        except User.DoesNotExist:
            raise AuthenticationFailed("User not found", code="user_not_found")