from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed
from core.models.user import User
from django.contrib.auth import authenticate


# Custom TokenObtainPairSerializer to add custom claims in JWT tokens
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        # Get token from the superclass and add custom claims
        token = super().get_token(user)
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        return token

    def validate(self, attrs):
        # Override validate to provide custom authentication error handling
        email = attrs.get('email')
        password = attrs.get('password')

        try:
            user = User.objects.get(email=email)  # Check if user exists
        except User.DoesNotExist:
            raise AuthenticationFailed(detail="User does not exist", code='user_does_not_exist')

        user = authenticate(email=email, password=password)  # Authenticate user

        if user is None:
            raise AuthenticationFailed(detail="Incorrect password", code='incorrect_password')
        return super().validate(attrs)  # Call superclass validate method
