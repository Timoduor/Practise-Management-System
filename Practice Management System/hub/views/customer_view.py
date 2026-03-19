from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from rest_framework.decorators import action

from hub.models.customer import Customer
from hub.models.project import Project
from hub.models.sales import Sales
from hub.models.task import Task
from hub.models.sales_task import SalesTask
from hub.models.expense import Expense

from hub.serializers.customer_serializer import CustomerSerializer
from .common_viewset import CommonViewSet


class CustomerViewSet(CommonViewSet):
    """
    Allows any authenticated user to have full CRUD access on Customer.
    No special restrictions for staff or superadmins.
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]  # Everyone must be logged in, but all have full access

    def get_queryset(self):
        # Return ALL customer records for any logged-in user
        user = self.request.user
        if user.is_authenticated:
            return Customer.objects.all()
        return Customer.objects.none()

    @action(detail=True, methods=["get"], url_path="summary")
    def get_ribbon(self, request, *args, **kwargs):
        """
        Example custom action that returns a summary of the Customer's projects, sales, tasks, etc.
        Now accessible to any logged-in user.
        """
        pk = kwargs.get("pk")

        try:
            customer = Customer.objects.get(customer_id=pk)
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=404)

        projects = Project.objects.filter(customer=customer, is_deleted=False)
        sales = Sales.objects.filter(customer=customer, is_deleted=False)

        project_count = projects.count()
        sales_count = sales.count()

        expected_project_financials = projects.aggregate(total_value=Sum("project_value"))["total_value"] or 0
        expected_sales_financials = sales.aggregate(total_value=Sum("project_value"))["total_value"] or 0
        received_sales_financials = Sales.objects.filter(
            customer=customer, sales_status__name="CLOSED_ACCEPTED", is_deleted=False
        ).aggregate(total_value=Sum("project_value"))["total_value"] or 0

        tasks_count = Task.objects.filter(project__in=projects, is_deleted=False).count()
        sales_tasks_count = SalesTask.objects.filter(sale__in=sales, is_deleted=False).count()

        completed_tasks_count = Task.objects.filter(
            project__in=projects, task_status__name="COMPLETED", is_deleted=False
        ).count()
        completed_sales_tasks_count = SalesTask.objects.filter(
            sale__in=sales, task_status__name="COMPLETED", is_deleted=False
        ).count()

        active_tasks_count = tasks_count - completed_tasks_count
        active_sales_tasks_count = sales_tasks_count - completed_sales_tasks_count
        total_expenses = Expense.objects.filter(customer=customer).aggregate(
            total_expense=Sum("value")
        )["total_expense"] or 0

        return Response({
            "projects": project_count,
            "sales": sales_count,
            "sales_tasks": {
                "active": active_sales_tasks_count,
                "completed": completed_sales_tasks_count,
                "total": sales_tasks_count,
            },
            "tasks": {
                "active": active_tasks_count,
                "completed": completed_tasks_count,
                "total": tasks_count,
            },
            "financials": {
                "projects": {
                    "expected_projects_value": expected_project_financials,
                },
                "sales": {
                    "expected_sales_value": expected_sales_financials,
                    "accepted_sales_value": received_sales_financials,
                },
                "total_expenses": total_expenses,
            },
        })
