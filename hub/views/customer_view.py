from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from hub.models.customer import Customer
from hub.models.project import Project
from hub.models.sales import Sales
from hub.models.task import Task
from hub.models.sales_task import SalesTask
from hub.models.expense import Expense
from django.db.models import Sum
from rest_framework.decorators import action
from .common_viewset import CommonViewSet
from hub.serializers.customer_serializer import CustomerSerializer


class CustomerViewSet(CommonViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            match user.admin_user.admin_type.name:
                case "SUP":
                    return Customer.objects.all()
                case "INS":
                  return Customer.objects.filter(entity__instance = user.employee_user.instance)
                case "ENT":
                    return Customer.objects.filter(entity= user.employee_user.entity)  
                case "UNI":
                    return Customer.objects.filter(unit= user.employee_user.unit)

        return Customer.objects.filter(unit = user.employee_user.unit)
    
    @action(detail=True, methods=['get'], url_path='summary')
    def get_ribbon(self,request, *args, **kwargs):
        pk = kwargs.get('pk')
        print("PK.",pk)
        # entity = self.request.user.employee_user.entity.id
        try:
            customer = Customer.objects.get(customer_id=pk)
            print("Customer", customer)
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=404)
        
        projects = Project.objects.filter(customer=customer, is_deleted=False)
        sales = Sales.objects.filter(customer=customer, is_deleted=False)

        
        project_count = projects.count()
        sales_count = sales.count()

        expected_project_financials = Project.objects.filter(customer=customer, is_deleted=False).aggregate(total_value=Sum('project_value'))['total_value'] or 0
        expected_sales_financials = Sales.objects.filter(customer=customer, is_deleted=False).aggregate(total_value=Sum('project_value'))['total_value'] or 0
        received_sales_financials = Sales.objects.filter(customer=customer, sales_status__name= "CLOSED_ACCEPTED" ,is_deleted=False).aggregate(total_value=Sum('project_value'))['total_value'] or 0




        tasks_count = Task.objects.filter(project__in=projects, is_deleted=False).count()
        sales_tasks_count = SalesTask.objects.filter(sale__in=sales, is_deleted=False).count()

            # Get counts for completed tasks
        completed_tasks_count = Task.objects.filter(project__in=projects, task_status__name="COMPLETED", is_deleted=False).count()
        completed_sales_tasks_count = SalesTask.objects.filter(sale__in=sales, task_status__name="COMPLETED", is_deleted=False).count()

        active_tasks_count = tasks_count - completed_tasks_count
        active_sales_tasks_count = sales_tasks_count - completed_sales_tasks_count
        total_expenses = Expense.objects.filter(customer=customer).aggregate(total_expense=Sum('value'))['total_expense'] or 0



        return Response({
            'projects': project_count,
            'sales' : sales_count,
            "sales_tasks" : {
                "active" : active_sales_tasks_count,
                "completed" : completed_sales_tasks_count,
                "total": sales_tasks_count,},
            "tasks" : {
                "active" : active_tasks_count ,
                "completed": completed_tasks_count,
                "total": tasks_count ,
            },

            "financials" : {
                "projects" : {
                    "expected_projects_value" : expected_project_financials,
                },
                "sales" : {
                    "expected_sales_value " : expected_sales_financials,
                    "accepted_sales_value" : received_sales_financials,
                },
                "total_expenses" : total_expenses,
                
            },

        })
   