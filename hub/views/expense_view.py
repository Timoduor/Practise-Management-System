from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status
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

    def get_queryset(self):
        user = self.request.user
        # Remove role-based filtering; return all for authenticated users
        if user.is_authenticated:
            return Expense.objects.all()
        return Expense.objects.none()

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['user'] = request.user.id
        data['last_updated_by_id'] = request.user.id
        data['created_by_id'] = request.user.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data.copy()
        data['last_updated_by_id'] = request.user.id

        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)
