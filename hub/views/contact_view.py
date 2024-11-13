from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from hub.models.contact import Contact
from hub.serializers.contact_serializer import ContactSerializer


class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]
   
    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            match user.admin_user.admin_type.name:
                case "SUP":
                    return Contact.objects.all()
                case "INS":
                  return Contact.objects.filter(customer__entity__instance = user.employee_user.instance)
                case "ENT":
                    return Contact.objects.filter(customer__entity= user.employee_user.entity)  
                case "UNI":
                    return Contact.objects.filter(customer__unit= user.employee_user.unit)

        return Contact.objects.filter(customer__unit = user.employee_user.unit)