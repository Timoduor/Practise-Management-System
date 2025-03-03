from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser, FormParser  # Enables file uploads
from django.db.models import Q

from hub.models.expense import Expense
from hub.serializers.expense_serializer import ExpenseSerializer

class ExpenseViewSet(viewsets.ModelViewSet):
    """
    Any authenticated user can CRUD Expenses.
    """
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)  # Allows handling of file uploads

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Expense.objects.all()
        return Expense.objects.none()

    def create(self, request, *args, **kwargs):
        """
        Overridden create method that copies request.data to preserve file uploads.
        """
        # Make a copy of request.data so that file data is preserved
        mutable_data = request.data.copy()
        mutable_data['user'] = request.user.id
        mutable_data['last_updated_by_id'] = request.user.id
        mutable_data['created_by_id'] = request.user.id

        serializer = self.get_serializer(data=mutable_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        """
        Overridden update method that copies request.data to preserve file uploads.
        """
        instance = self.get_object()
        mutable_data = request.data.copy()
        mutable_data['last_updated_by_id'] = request.user.id

        serializer = self.get_serializer(instance, data=mutable_data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)
