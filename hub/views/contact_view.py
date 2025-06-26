from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from hub.models.contact import Contact
from hub.serializers.contact_serializer import ContactSerializer
from core.models.user import User


class ContactViewSet(viewsets.ModelViewSet):
    """
    Any authenticated user has full CRUD access to Contacts.
    """
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Contact.objects.all()
        return Contact.objects.none()


@csrf_exempt  # Optional, depends on whether you're calling this internally/admin-side
def get_user_details(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
        return JsonResponse({
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
        })
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)
