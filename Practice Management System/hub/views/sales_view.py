from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.db.models import Sum
from django.utils.timezone import now

from .common_viewset import CommonViewSet
from hub.serializers.sales_serializer import SalesSerializer
from hub.models.sales import Sales
from hub.models.sales_task import SalesTask
from core.serializers.employee_serializers import EmployeeSerializer


class SalesViewSet(CommonViewSet):
    queryset = Sales.objects.all()
    serializer_class = SalesSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Any authenticated user can see all sales
        user = self.request.user
        if user.is_authenticated:
            return Sales.objects.all()
        return Sales.objects.none()

    @action(detail=True, methods=['get'], url_path='members')
    def get_sales_member(self, request, pk=None):
        try:
            sale = self.get_object()  # from CommonViewSet
            members = sale.members.all()
            serializer = EmployeeSerializer(members, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Sales.DoesNotExist:
            return Response({'detail': 'Sale not found.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'], url_path='dashboard')
    def get_sales_dashboard(self, request, *args, **kwargs):
        current_date = now()
        current_month = current_date.month
        current_year = current_date.year

        # Since all authenticated users have the same access now,
        # we remove role-based filtering entirely.
        # Filter for the current month and year, but no user restrictions.
        sales_filter = {
            'expected_order_date__month': current_month,
            'expected_order_date__year': current_year,
            'is_deleted': False,
        }

        # Sales accepted this month
        sales_this_month = Sales.objects.filter(
            sales_status__name="CLOSED_ACCEPTED",
            **sales_filter
        ).aggregate(total_sales=Sum('project_value'))['total_sales'] or 0

        # Estimated sales (opportunities) this month
        estimated_sales = Sales.objects.filter(
            sales_status__name="OPPORTUNITY",
            **sales_filter
        ).aggregate(total_estimated=Sum('project_value'))['total_estimated'] or 0

        # Cases needing attention (IN_PROGRESS or PENDING tasks)
        cases_needing_attention = SalesTask.objects.filter(
            sale__expected_order_date__month=current_month,
            sale__expected_order_date__year=current_year,
            sale__is_deleted=False,
            task_status__name__in=["IN_PROGRESS", "PENDING"]
        ).count()

        # All sales opportunities this month
        total_sales_opportunities = Sales.objects.filter(**sales_filter).count()

        # Calculate hit rate
        closed_sales_count = Sales.objects.filter(
            sales_status__name="CLOSED_ACCEPTED",
            **sales_filter
        ).count()
        hit_rate = (closed_sales_count / total_sales_opportunities * 100) if total_sales_opportunities else 0

        return Response({
            "sales_this_month": f"{sales_this_month:.2f} €",
            "estimated_sales_this_month": f"{estimated_sales:.2f} €",
            "cases_needing_attention": cases_needing_attention,
            "hit_rate_this_month": f"{hit_rate:.0f} %",
            # "entity": user.employee_user.entity, # removed since all users have full access now
        })
