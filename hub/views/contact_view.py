from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from hub.models.contact import Contact
from hub.serializers.contact_serializer import ContactSerializer

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
