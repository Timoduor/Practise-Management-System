from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from hub.models.task import Task
from rest_framework import viewsets, status
from hub.models.expense import Expense
from hub.serializers.expense_serializer import ExpenseSerializer
from django.db.models import Q


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            match user.admin_user.admin_type.name:
                case "SUP":
                    return Expense.objects.all()
                case "INS":
                    return Expense.objects.filter(Q(project__entity__instance=user.employee_user.instance) |
                                                  Q(sale__entity__instance=user.employee_user.instance))
                case "ENT":
                    return Expense.objects.filter(Q(project__entity=user.employee_user.entity) |
                                                  Q(sale__entity=user.employee_user.entity))
                case "UNI":
                    return Expense.objects.filter(Q(project__unit=user.employee_user.unit) |              
                                                  Q(sale__unit=user.employee_user.unit))

        return Expense.objects.filter(employee=user.employee_user)

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
