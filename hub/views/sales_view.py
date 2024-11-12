from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from rest_framework import  status
from rest_framework.decorators import action
from .common_viewset import CommonViewSet
from hub.serializers.sales_serializer import SalesSerializer
from django.utils.timezone import now
from hub.models.sales import Sales
from hub.models.sales_task import SalesTask


class SalesViewSet(CommonViewSet):
    queryset = Sales.objects.all()
    serializer_class = SalesSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            match user.admin_user.admin_type.name:
                case "SUP":
                  return Sales.objects.all()
                case "INS":
                  return Sales.objects.filter(entity__instance = user.employee_user.instance)
                case "ENT":
                    return Sales.objects.filter(entity= user.employee_user.entity)  
                case "UNI":
                    return Sales.objects.filter(unit= user.employee_user.unit)

        return Sales.objects.filter(entity= user.employee_user.entity)
    
        
    @action(detail=True, methods=['get'], url_path='members')
    def get_sales_member(self, request, pk=None):
        try:
            # Fetch the sale by its primary key (pk)
            sale = self.get_object()
            # Get the members associated with the sale
            members = sale.members.all()
            # Serialize the members
            serializer = EmployeeSerializer(members, many=True)
            # Return the serialized data
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Sales.DoesNotExist:
            return Response({'detail': 'Sale not found.'}, status=status.HTTP_404_NOT_FOUND)
    

    @action(detail=False, methods=['get'], url_path='dashboard')
    def get_sales_dashboard(self, request, *args, **kwargs):

        current_date = now()
        current_month = current_date.month
        current_year = current_date.year
        
        user = self.request.user

                # Set the filtering based on admin type
        sales_filter = {}
        tasks_filter = {}

        if user.is_staff:
            match user.admin_user.admin_type.name:
                case "SUP":
                    # No additional filter needed for "SUP" as they can see all sales
                    pass
                case "INS":
                    sales_filter = {"entity__instance": user.employee_user.instance}
                    tasks_filter = {"sale__entity__instance": user.employee_user.instance}
                case "ENT":
                    sales_filter = {"entity": user.employee_user.entity}
                    tasks_filter = {"sale__entity": user.employee_user.entity}
                case "UNI":
                    sales_filter = {"unit": user.employee_user.unit}
                    tasks_filter = {"sale__unit": user.employee_user.unit}
        else:
            # For non-staff users, default to their specific entity
            sales_filter = {"entity": user.employee_user.entity}
            tasks_filter = {"sale__entity": user.employee_user.entity}


        # Filter sales and tasks based on the current month
        sales_this_month = Sales.objects.filter(
            expected_order_date__month=current_month,
            expected_order_date__year=current_year,
            sales_status="CLOSED_ACCEPTED",
            is_deleted=False,
            **sales_filter
        ).aggregate(total_sales=Sum('project_value'))['total_sales'] or 0

        estimated_sales = Sales.objects.filter(
            expected_order_date__month=current_month,
            expected_order_date__year=current_year,
            sales_status="OPPORTUNITY",
            is_deleted=False,
            **sales_filter,
        ).aggregate(total_estimated=Sum('project_value'))['total_estimated'] or 0

        # Sales with tasks needing attention (IN_PROGRESS or PENDING)
        cases_needing_attention = SalesTask.objects.filter(
            sale__expected_order_date__month=current_month,
            sale__expected_order_date__year=current_year,
            task_status__in=["IN_PROGRESS", "PENDING"],
            sale__is_deleted=False,
            **tasks_filter
        ).count()

        # Total sales opportunities this month
        total_sales_opportunities = Sales.objects.filter(
            expected_order_date__month=current_month,
            expected_order_date__year=current_year,
            is_deleted=False,
            **sales_filter
        ).count()

        # Calculate hit rate
        closed_sales_count = Sales.objects.filter(
            expected_order_date__month=current_month,
            expected_order_date__year=current_year,
            sales_status="CLOSED_ACCEPTED",
            is_deleted=False,
            **sales_filter
        ).count()
        hit_rate = (closed_sales_count / total_sales_opportunities * 100) if total_sales_opportunities else 0

        return Response({
            "sales_this_month": f"{sales_this_month:.2f} €",
            "estimated_sales_this_month": f"{estimated_sales:.2f} €",
            "cases_needing_attention": cases_needing_attention,
            "hit_rate_this_month": f"{hit_rate:.0f} %",
            "entity" : user.employee_user.entity,
        })

