from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework import generics,viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

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


