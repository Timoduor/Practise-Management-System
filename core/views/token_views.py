from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from core.serializers.token_serializers import CustomTokenObtainPairSerializer
from rest_framework.permissions import AllowAny

# Define a custom token obtain pair view to handle authentication token issuance
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer  # Use custom serializer for tokens

    def post(self, request: Request, *args, **kwargs):
        # Handle POST request to obtain tokens and set cookies for access and refresh tokens
        response = super().post(request, *args, **kwargs)
        data = response.data

        # Set access token as a cookie with 2-hour max age
        response.set_cookie(
            'access_token', data["access"], httponly=False, samesite='Strict', max_age=60 * 60 * 2
        )
        # Set refresh token as a cookie with 24-hour max age
        response.set_cookie(
            'refresh_token', data["refresh"], httponly=True, samesite='Strict', max_age=60 * 60 * 24
        )
        return response

# Define a custom token refresh view to handle refreshing of access tokens
class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        # Retrieve refresh token from cookies and refresh access token if valid
        refresh_token = request.COOKIES.get('refresh_token')
        if refresh_token:
            request.data["refresh"] = refresh_token  # Use refresh token from cookie

        response = super().post(request, *args, **kwargs)

        # If refresh is successful, set new access token as cookie
        if response.status_code == 200:
            access_token = response.data.get('access')
            response.set_cookie(
                'access_token', access_token, httponly=False, samesite='Strict', max_age=60 * 60 * 3
            )
        return response

# Define a custom token verification view to verify the validity of access tokens
class CustomTokenVerifyView(TokenVerifyView):
    def post(self, request, *args, **kwargs):
        # Retrieve access token from cookies to verify its validity
        access_token = request.COOKIES.get("access_token")
        if access_token:
            request.data['token'] = access_token  # Add token to request data
        return super().post(request, *args, **kwargs)

# Define a logout view to handle user logout and token blacklisting
class LogoutView(APIView):
    permission_classes = (AllowAny,)  # Allow any user to access this view
    
    def post(self, request):
        try:
            # Blacklist the refresh token to prevent further use
            refresh_token = request.data['refresh_token']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
