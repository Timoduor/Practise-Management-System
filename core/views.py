# Import necessary modules for Django views and REST framework
from django.shortcuts import render, get_object_or_404
from rest_framework.request import Request
from .models import *  # Import all models from the current app
from .serializers import *  # Import all serializers from the current app
from rest_framework import generics, viewsets, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

# Define a viewset for managing User objects
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()  # Retrieve all User objects
    serializer_class = UserSerializer  # Use UserSerializer for serialization


    def get_queryset(self):
        user = self.request.user

        # Check if the user is staff and has an admin profile
        if user.is_staff and hasattr(user, 'admin_user'):
            admin_user = user.admin_user
            admin_type_name = admin_user.admin_type.name
            jurisdiction = admin_user.jurisdiction  # Can be Instance, Entity, or Unit

            if admin_type_name == "SUP":
                # Superuser admin - return all users
                return User.objects.all()
            elif admin_type_name == "INS" and isinstance(jurisdiction, Instance):
                # Instance admin - return users in the same instance
                instance = jurisdiction
                return User.objects.filter(
                    models.Q(employee_user__instance=instance) |
                    models.Q(admin_user__jurisdiction_content_type=ContentType.objects.get_for_model(Instance),
                      admin_user__jurisdiction_object_id=instance.id)
                ).distinct()
            elif admin_type_name == "ENT" and isinstance(jurisdiction, Entity):
                # Entity admin - return users in the same entity and child entities
                entity = jurisdiction
                # Get all descendant entities
                all_entities = self.get_all_entities(entity)
                entity_ids = [e.id for e in all_entities]

                return User.objects.filter(
                    models.Q(employee_user__entity__in=all_entities) |
                    models.Q(admin_user__jurisdiction_content_type=ContentType.objects.get_for_model(Entity),
                      admin_user__jurisdiction_object_id__in=entity_ids)
                ).distinct()
            elif admin_type_name == "UNI" and isinstance(jurisdiction, Unit):
                # Unit admin - return users in the same unit
                unit = jurisdiction
                return User.objects.filter(
                    models.Q(employee_user__unit=unit) |
                    models.Q(admin_user__jurisdiction_content_type=ContentType.objects.get_for_model(Unit),
                      admin_user__jurisdiction_object_id=unit.id)
                ).distinct()
            else:
                return User.objects.none()
        else:
            # Non-staff users can only see themselves
            return User.objects.filter(pk=user.pk)

    def get_all_entities(self, parent_entity):
        # Recursive function to get all descendant entities
        entities = [parent_entity]
        child_entities = Entity.objects.filter(parent_entity=parent_entity)
        for child in child_entities:
            entities.extend(self.get_all_entities(child))
        return entities

# Define a viewset for managing Admin objects
class AdminViewSet(viewsets.ModelViewSet):
    queryset = Admin.objects.all()
    serializer_class = AdminSerializer

    def create(self, request):
        # Handle user creation with validation and response
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # Raise exception if data is invalid
        self.perform_create(serializer)  # Save new user
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        user = self.request.user

        # Check if the user is staff and has an admin profile
        if user.is_staff and hasattr(user, 'admin_user'):
            admin_user = user.admin_user
            admin_type_name = admin_user.admin_type.name
            jurisdiction = admin_user.jurisdiction  # Can be Instance, Entity, or Unit

            if admin_type_name == "SUP":
                # Superuser admin - return all admins
                return Admin.objects.all()
            elif admin_type_name == "INS" and isinstance(jurisdiction, Instance):
                # Instance admin - return admins in the same instance
                instance = jurisdiction
                return Admin.objects.filter(
                    models.Q(jurisdiction_content_type=ContentType.objects.get_for_model(Instance),
                      jurisdiction_object_id=instance.id) |
                    models.Q(user__employee_user__instance=instance)
                ).distinct()
            elif admin_type_name == "ENT" and isinstance(jurisdiction, Entity):
                # Entity admin - return admins in the same entity and child entities
                entity = jurisdiction
                # Get all descendant entities
                all_entities = self.get_all_entities(entity)
                entity_ids = [e.id for e in all_entities]

                return Admin.objects.filter(
                    models.Q(jurisdiction_content_type=ContentType.objects.get_for_model(Entity),
                      jurisdiction_object_id__in=entity_ids) |
                    models.Q(user__employee_user__entity__in=all_entities)
                ).distinct()
            elif admin_type_name == "UNI" and isinstance(jurisdiction, Unit):
                # Unit admin - return admins in the same unit
                unit = jurisdiction
                return Admin.objects.filter(
                    models.Q(jurisdiction_content_type=ContentType.objects.get_for_model(Unit),
                      jurisdiction_object_id=unit.id) |
                    models.Q(user__employee_user__unit=unit)
                ).distinct()
            else:
                return Admin.objects.none()
        else:
            # Non-staff users should not see any admins
            return Admin.objects.none()

    def get_all_entities(self, parent_entity):
        # Recursive function to get all descendant entities
        entities = [parent_entity]
        child_entities = Entity.objects.filter(parent_entity=parent_entity)
        for child in child_entities:
            entities.extend(self.get_all_entities(child))
        return entities

# Define a viewset for managing Admin objects
# Define a viewset for managing Employee objects
class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()  # Retrieve all Employee objects
    serializer_class = EmployeeSerializer  # Use EmployeeSerializer for serialization

    def get_queryset(self):
        # Customize queryset based on the user's role and permissions
        user = self.request.user
        if user.is_staff:
            # Filter based on the admin type of the user if they are staff
            match user.admin_user.admin_type.name:
                case "SUP":
                    return Employee.objects.all()
                case "INS":
                    return Employee.objects.filter(instance=user.employee_user.instance)
                case "ENT":
                    return Employee.objects.filter(entity=user.employee_user.entity)
                case "UNI":
                    return Employee.objects.filter(unit=user.employee_user.unit)
        # Default filtering for non-staff users
        return Employee.objects.filter(entity=user.employee_user.entity)

    def destroy(self, request, pk=None):
        # Handle deletion of a specific Employee object by primary key
        user = get_object_or_404(Admin, pk=pk)

# Define a viewset for managing Instance objects
class InstanceViewSet(viewsets.ModelViewSet):
    queryset = Instance.objects.all()  # Retrieve all Instance objects
    serializer_class = InstanceSerializer  # Use InstanceSerializer for serialization

# Define a viewset for managing Entity objects
class EntityViewSet(viewsets.ModelViewSet):
    queryset = Entity.objects.all()  # Retrieve all Entity objects
    serializer_class = EntitySerializer  # Use EntitySerializer for serialization

    def get_queryset(self):
        # Customize queryset based on user's role and permissions
        user = self.request.user
        if user.is_staff:
            match user.admin_user.admin_type.name:
                case "SUP":
                    return Entity.objects.all()
                case "INS":
                    return Entity.objects.filter(instance=user.employee_user.instance)
                case "ENT":
                    return Entity.objects.filter(
                        models.Q(id=user.employee_user.entity.id) | models.Q(parent_entity=user.employee_user.entity)
                    )
                case "UNI":
                    return Entity.objects.filter(entity=user.employee_user.entity)
        return Unit.objects.filter(entity=user.employee_user.entity)

# Define a viewset for managing Unit objects
class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.all()  # Retrieve all Unit objects
    serializer_class = UnitSerializer  # Use UnitSerializer for serialization

    def get_queryset(self):
        # Customize queryset based on user's role and permissions
        user = self.request.user
        if user.is_staff:
            match user.admin_user.admin_type.name:
                case "SUP":
                    return Unit.objects.all()
                case "INS":
                    return Unit.objects.filter(entity__instance=user.employee_user.instance)
                case "ENT":
                    return Unit.objects.filter(entity=user.employee_user.entity)
                case "UNI":
                    return Unit.objects.filter(unit=user.employee_user.unit)
        return Unit.objects.filter(entity=user.employee_user.entity)

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
