from django.shortcuts import render
from rest_framework.request import Request
from .models import *
from .serializers import *
from rest_framework import generics,viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
# Create your views here.

class UserViewSet(viewsets.ModelViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer

 

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        # user = serializer.save()

        # if user.is_staff:
        #     admin_type, created = AdminType.objects.get_or_create(name="INS")
        #     Admin.objects.create(user=user, admin_type=admin_type)

        # return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    # def retrieve(self, request, pk=None):
    #     user = get_object_or_404(User, pk=pk)
    #     serializer = self.get_serializer(user)
    #     return Response(serializer.data)

    # def update(self, request, pk=None):
    #     pass

    # def partial_update(self, request, pk=None):
    #     pass

    # def destroy(self, request, pk=None):
    #     # Delete a specific user
    #     user = get_object_or_404(User, pk=pk)
    #     user.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)


class AdminViewSet(viewsets.ModelViewSet):
    queryset = Admin.objects.all()
    serializer_class = AdminSerializer

class EmployeeViewSet(viewsets.ModelViewSet): 
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer  

    def destroy(self, request, pk= None):
        user = get_object_or_404(Admin, pk= pk)


class InstanceViewSet(viewsets.ModelViewSet):
    queryset = Instance.objects.all()
    serializer_class = InstanceSerializer

    

class EntityViewSet(viewsets.ModelViewSet):
    queryset = Entity.objects.all()
    serializer_class = EntitySerializer

class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request: Request, *args, **kwargs):
        response =  super().post(request, *args, **kwargs)

        data = response.data

        #Rememeber to switch http only back to true, you only set it to false to test on postman
        response.set_cookie(
            'access_token' , data["access"], httponly= True, samesite='Strict', max_age= 60* 60 * 1
        )

        response.set_cookie(
            'refresh_token' , data["refresh"], httponly= True, samesite='Strict', max_age = 60*60* 24
        )
        print(response)

        return response

class CustomTokenRefreshView(TokenRefreshView):
    def post(self,request,*args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')

        if refresh_token:
            request.data["refresh"] = refresh_token

        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            access_token = response.data.get('access')
            
            response.set_cookie(
                'access_token' , access_token, httponly= False, samesite='Strict', max_age= 60* 60 *3
            )

            print(response)
        
        return response

class CustomTokenVerifyView(TokenVerifyView):
    def post(self,request, *args, **kwargs):
        access_token = request.COOKIES.get("access_token")

        if access_token:
            request.data['token'] = access_token

        return super().post(request,*args, **kwargs)

class LogoutView(APIView):
    # def post(self,request):
    #     try:
    #         refresh_token = request.data['refresh_token']
    #         token = RefreshToken(refresh_token)
    #         token.blacklist()

    #         return Response(status= status.HTTP_205_RESET_CONTENT)
        
    #     except Exception as e:
    #         return Response(status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        response = Response(status= status.HTTP_204_NO_CONTENT)
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return response