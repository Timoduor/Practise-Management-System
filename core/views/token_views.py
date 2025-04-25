from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from core.serializers.token_serializers import CustomTokenObtainPairSerializer
from rest_framework.permissions import AllowAny

class CustomTokenObtainPairView(TokenObtainPairView):
    """View for obtaining JWT token pair (access and refresh tokens)"""
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request: Request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        data = response.data

        # Set access token cookie (2 hour expiry)
        response.set_cookie(
            'access_token',
            data["access"],
            httponly=False,
            samesite='Strict',
            secure=True,
            max_age=60 * 60 * 2
        )

        # Set refresh token cookie (24 hour expiry)
        response.set_cookie(
            'refresh_token',
            data["refresh"],
            httponly=True,
            samesite='Strict',
            secure=True,
            max_age=60 * 60 * 24
        )

        return response

class CustomTokenRefreshView(TokenRefreshView):
    """View for refreshing expired access tokens using refresh token"""

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response(
                {"error": "No refresh token provided"},
                status=status.HTTP_400_BAD_REQUEST
            )

        request.data["refresh"] = refresh_token

        try:
            response = super().post(request, *args, **kwargs)
            if response.status_code == 200:
                response.set_cookie(
                    'access_token',
                    response.data['access'],
                    httponly=False,
                    samesite='Strict',
                    secure=True,
                    max_age=60 * 60 * 2
                )
            return response
        except Exception as e:
            return Response(
                {"error": "Invalid refresh token"},
                status=status.HTTP_401_UNAUTHORIZED
            )

class CustomTokenVerifyView(TokenVerifyView):
    """View for verifying access tokens"""

    def post(self, request, *args, **kwargs):
        access_token = request.COOKIES.get("access_token")
        if not access_token:
            return Response(
                {"error": "No access token provided"},
                status=status.HTTP_400_BAD_REQUEST
            )

        request.data['token'] = access_token
        return super().post(request, *args, **kwargs)

class LogoutView(APIView):
    """View for logging out users and blacklisting their refresh token"""
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            refresh_token = request.COOKIES.get('refresh_token')
            if not refresh_token:
                return Response(
                    {"error": "No refresh token provided"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Blacklist the refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()

            response = Response(status=status.HTTP_205_RESET_CONTENT)
            
            # Delete cookies
            response.delete_cookie('access_token')
            response.delete_cookie('refresh_token')
            
            return response

        except Exception as e:
            return Response(
                {"error": "Invalid refresh token"},
                status=status.HTTP_400_BAD_REQUEST
            )
