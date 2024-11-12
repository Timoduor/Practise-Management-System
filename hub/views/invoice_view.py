from rest_framework.permissions import IsAuthenticated
from hub.models.invoice import Invoice
from .common_viewset import CommonViewSet
from hub.serializers.invoice_serializer import InvoiceSerializer


class InvoiceViewSet(CommonViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            match user.admin_user.admin_type.name:
                case "SUP":
                  return Invoice.objects.all()
                case "INS":
                  return Invoice.objects.filter(entity__instance = user.employee_user.instance)
                case "ENT":
                    return Invoice.objects.filter(project__entity= user.employee_user.entity)  
                case "UNI":
                    return Invoice.objects.filter(project__unit= user.employee_user.unit)

        return Invoice.objects.filter(project = user.employee_user.project_members)

