from rest_framework.permissions import IsAuthenticated
from .common_viewset import CommonViewSet
from hub.models.invoice import Invoice
from hub.serializers.invoice_serializer import InvoiceSerializer

class InvoiceViewSet(CommonViewSet):
    """
    Any authenticated user can CRUD Invoices.
    """
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Invoice.objects.all()
        return Invoice.objects.none()
