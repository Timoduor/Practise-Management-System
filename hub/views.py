from django.shortcuts import render
from rest_framework import viewsets
from .models import Customer, Contact, Sales, Project, SalesTask, Task, Invoice, ProjectPhase, WorkEntries, Absence, Expense, LeaveType
from .serializers import CustomerSerializer, ContactSerializer, SalesSerializer, ProjectSerializer, SalesTaskSerializer, TaskSerializer, InvoiceSerializer, ProjectPhaseSerializer, WorkEntriesSerializer,AbsenceSerializer,ExpenseSerializer, LeaveTypeSerializer
from core.serializers import EmployeeSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import  status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.utils.timezone import now
from django.db.models import Q
from datetime import datetime, timedelta
from collections import defaultdict
from django.db.models import Sum


class CommonViewSet(viewsets.ModelViewSet):
    def create(self, request, *args, **kwargs):
        # Make a mutable copy of the request data
        data = request.data.copy()
        # Set the user field to the logged-in user

        data['last_updated_by_id'] = request.user.id
        data['created_by_id'] = request.user.id

        if 'entity' not in data or not data['entity']:
            if hasattr(request.user, 'employee_user') and request.user.employee_user.entity:
                data['entity'] = request.user.employee_user.entity.id
            else:
                data['entity'] = None

        if 'unit' not in data or not data['unit']:
            if hasattr(request.user, 'employee_user') and request.user.employee_user.unit:
                data['unit'] = request.user.employee_user.unit.id
            else:
                data['unit'] = None
        # Fetch the task instance

        # Pass the data to the serializer and validate it
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        # Save the data
        self.perform_create(serializer)

        # Return the response
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    

    def update(self, request, *args, **kwargs):
        # Get the instance to be updated using the primary key from URL kwargs
        instance = self.get_object()

        # Make a mutable copy of the request data
        data = request.data.copy()

        # Set the user fields to the logged-in user for tracking updates
        data['last_updated_by_id'] = request.user.id

        # Pass the data to the serializer along with the instance to update
        serializer = self.get_serializer(instance, data=data, partial=True)  # Use partial=True to allow partial updates
        serializer.is_valid(raise_exception=True)

        # Save the updated data
        self.perform_update(serializer)

        # Return the updated instance data as a response
        return Response(serializer.data, status=status.HTTP_200_OK)
    

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
        received_sales_financials = Sales.objects.filter(customer=customer, sales_status= "CLOSED_ACCEPTED" ,is_deleted=False).aggregate(total_value=Sum('project_value'))['total_value'] or 0




        tasks_count = Task.objects.filter(project__in=projects, is_deleted=False).count()
        sales_tasks_count = SalesTask.objects.filter(sale__in=sales, is_deleted=False).count()

            # Get counts for completed tasks
        completed_tasks_count = Task.objects.filter(project__in=projects, task_status="COMPLETED", is_deleted=False).count()
        completed_sales_tasks_count = SalesTask.objects.filter(sale__in=sales, task_status="COMPLETED", is_deleted=False).count()

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



class ProjectViewSet(CommonViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            match user.admin_user.admin_type.name:
                case "SUP":
                  return Project.objects.all()
                case "INS":
                  return Project.objects.filter(entity__instance = user.employee_user.instance)
                case "ENT":
                    return Project.objects.filter(project__entity= user.employee_user.entity)  
                case "UNI":
                    return Project.objects.filter(project__unit= user.employee_user.unit)

        return Project.objects.filter(entity= user.employee_user.entity) 
    
    @action(detail=True, methods=['get'], url_path='members')
    def get_project_members(self, request, pk=None):
        try:
            # Fetch the sale by its primary key (pk)
            project = self.get_object()
            # Get the members associated with the sale
            members = project.members.all()
            # Serialize the members
            serializer = EmployeeSerializer(members, many=True)
            # Return the serialized data
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Project.DoesNotExist:
            return Response({'detail': 'Project not found.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'], url_path='work-entries')
    def get_work_entries(self, request, pk=None):
        try:
            # Fetch the project by its primary key (pk)
            project = self.get_object()
            # Get the work entries related to the project
            work_entries = WorkEntries.objects.filter(project=project)

            # Aggregate the total duration of all work entries for the project
            total_duration = work_entries.aggregate(total_duration=Sum('duration'))['total_duration'] or timedelta(0)

            # If total_duration is a timedelta, convert it to total seconds
            if isinstance(total_duration, timedelta):
                total_seconds = int(total_duration.total_seconds())
            else:
                total_seconds = total_duration  # Assume it's already in seconds if not a timedelta

            # Convert total duration from seconds to hours and minutes
            total_duration_in_hours = total_seconds // 3600
            total_duration_in_minutes = (total_seconds % 3600) // 60
            formatted_total_duration = f"{int(total_duration_in_hours)}h {int(total_duration_in_minutes)}m"

            # Serialize the work entries
            serializer = WorkEntriesSerializer(work_entries, many=True)

            # Prepare the response data
            response_data = {
                'work_entries': serializer.data,
                'total_duration': formatted_total_duration
            }

            # Return the response with the serialized data and the total duration
            return Response(response_data, status=status.HTTP_200_OK)
        except Project.DoesNotExist:
            return Response({'detail': 'Project not found.'}, status=status.HTTP_404_NOT_FOUND)

    


    @action(detail=False, methods=['get'], url_path='dashboard')
    def get_projects_dashboard(self, request, *args, **kwargs):
        user = self.request.user
        
        # Get the current date and extract month and year
        current_date = now()
         # Initialize filter dictionary based on admin type
        project_filter = {}

        # Apply filtering based on user’s admin level
        if user.is_staff:
            match user.admin_user.admin_type.name:
                case "SUP":
                    # SUP has access to all projects
                    pass
                case "INS":
                    project_filter = {"entity__instance": user.employee_user.instance}
                case "ENT":
                    project_filter = {"entity": user.employee_user.entity}
                case "UNI":
                    project_filter = {"unit": user.employee_user.unit}
        else:
            # Default filter for non-staff users
            project_filter = {"entity": user.employee_user.entity}


        # Ongoing projects (current date is between start_date and end_date)
        ongoing_projects = Project.objects.filter(
            Q(start_date__lte=current_date) & (Q(end_date__gte=current_date) | Q(end_date__isnull=True)),
            is_deleted=False,
            **project_filter
        ).count()

        # Estimated project value for ongoing projects in the current month
        estimated_project_value = Project.objects.filter(
            Q(start_date__lte=current_date) & (Q(end_date__gte=current_date) | Q(end_date__isnull=True)),
            is_deleted=False,
            **project_filter
        ).aggregate(total_value=Sum('project_value'))['total_value'] or 0

        # Projects with tasks needing attention (IN_PROGRESS or PENDING) for ongoing projects
        projects_needing_attention = Task.objects.filter(
            project__in=Project.objects.filter(
                Q(start_date__lte=current_date) & (Q(end_date__gte=current_date) | Q(end_date__isnull=True)),
                is_deleted=False,
                **project_filter
            ),
            task_status__in=["IN_PROGRESS", "PENDING"],
            is_deleted=False
        ).count()

        # Total projects opportunities this month (ongoing projects)
        total_projects_opportunities = ongoing_projects

        # Completed projects count this month (projects with end date in the current month)
        completed_projects_count = Project.objects.filter(
            end_date__month=current_date.month,
            end_date__year=current_date.year,
            is_deleted=False,
            **project_filter
        ).count()

        # Calculate completion rate
        completion_rate = (completed_projects_count / total_projects_opportunities * 100) if total_projects_opportunities else 0

        return Response({
            "projects_ongoing_this_month": ongoing_projects,
            "estimated_project_value": f"{estimated_project_value:.2f} €",
            "projects_needing_attention": projects_needing_attention,
            "completion_rate_this_month": f"{completion_rate:.0f} %"
        })



class ProjectPhaseViewSet(CommonViewSet):
    queryset = ProjectPhase.objects.all()
    serializer_class = ProjectPhaseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            match user.admin_user.admin_type.name:
                case "SUP":
                  return ProjectPhase.objects.all()
                case "INS":
                  return ProjectPhase.objects.filter(entity__instance = user.employee_user.instance)
                case "ENT":
                    return ProjectPhase.objects.filter(project__entity= user.employee_user.entity)  
                case "UNI":
                    return ProjectPhase.objects.filter(project__unit= user.employee_user.unit)

        return ProjectPhase.objects.filter(project__project_members = user.employee_user) 
    
    @action(detail=True, methods=['get'], url_path='members')
    def get_project_members(self, request, pk=None):
        try:
            # Fetch the sale by its primary key (pk)
            phase = self.get_object()
            # Get the members associated with the sale
            members = phase.members.all()
            # Serialize the members
            serializer = EmployeeSerializer(members, many=True)
            # Return the serialized data
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ProjectPhase.DoesNotExist:
            return Response({'detail': 'Project phase not found.'}, status=status.HTTP_404_NOT_FOUND)
    

    @action(detail=True, methods=['get'], url_path='work-entries')
    def get_work_entries(self, request, pk=None):
        try:
            # Fetch the project by its primary key (pk)
            project = self.get_object()
            # Get the work entries related to the project
            work_entries = WorkEntries.objects.filter(project=project)

            # Aggregate the total duration (in seconds) of all work entries for the project
            total_duration = work_entries.aggregate(total_duration=Sum('duration'))['total_duration'] or 0


            # Convert total duration from seconds to hours and minutes
            total_duration_in_hours = total_duration // 3600
            total_duration_in_minutes = (total_duration % 3600) // 60
            formatted_total_duration = f"{int(total_duration_in_hours)}h {int(total_duration_in_minutes)}m"

            # Serialize the work entries
            serializer = WorkEntriesSerializer(work_entries, many=True)

            # Prepare the response data
            response_data = {
                'work_entries': serializer.data,
                'total_duration': formatted_total_duration
            }

            # Return the response with the serialized data and the total duration
            return Response(response_data, status=status.HTTP_200_OK)
        except Project.DoesNotExist:
            return Response({'detail': 'Project not found.'}, status=status.HTTP_404_NOT_FOUND)

class TaskViewSet(CommonViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            match user.admin_user.admin_type.name:
                case "SUP":
                  return Task.objects.all()
                case "INS":
                  return Task.objects.filter(entity__instance = user.employee_user.instance)
                case "ENT":
                    return Task.objects.filter(project__entity= user.employee_user.entity)  
                case "UNI":
                    return Task.objects.filter(project__unit= user.employee_user.unit)

        return Task.objects.filter(project = user.employee_user.project_members)
    
class SalesTaskViewSet(CommonViewSet):
    queryset = SalesTask.objects.all()
    serializer_class = SalesTaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            match user.admin_user.admin_type.name:
                case "SUP":
                  return SalesTask.objects.all()
                case "INS":
                  return SalesTask.objects.filter(entity__instance = user.employee_user.instance)
                case "ENT":
                    return SalesTask.objects.filter(sales__entity= user.employee_user.entity)  
                case "UNI":
                    return SalesTask.objects.filter(sales__unit= user.employee_user.unit)

        return SalesTask.objects.filter(project = user.employee_user.sales_members)

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

class WorkEntriesViewSet(viewsets.ModelViewSet):
    queryset = WorkEntries.objects.all()
    serializer_class = WorkEntriesSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            match user.admin_user.admin_type.name:
                case "SUP":
                  return WorkEntries.objects.all()
                case "INS":
                  return WorkEntries.objects.filter(entity__instance = user.employee_user.instance)
                case "ENT":
                    return WorkEntries.objects.filter(project__entity= user.employee_user.entity)  
                case "UNI":
                    return WorkEntries.objects.filter(project__unit= user.employee_user.unit)

        return WorkEntries.objects.filter(employee = user.employee_user)
    
    def create(self, request, *args, **kwargs):
            # Make a mutable copy of the request data
            data = request.data.copy()

            # Set the user field to the logged-in user
            data['user'] = request.user.id
            data['last_updated_by_id'] = request.user.id
            data['created_by_id'] = request.user.id

            task_id = data.get("task")

            # # Fetch the task instance
            # if(data.get("task")):
                
            #     try:
            #         task = Task.objects.get(pk=task_id)
            #     except Task.DoesNotExist:
            #         return Response({'error': 'Invalid task.'}, status=status.HTTP_400_BAD_REQUEST)
            
            #     # data['project'] = task.project.project_id
            #     data['phase'] = task.phase.phase_id

            # Pass the data to the serializer and validate it
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)

            # Save the data
            self.perform_create(serializer)

            # Return the response
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request, *args, **kwargs):
        # Get the instance to be updated using the primary key from URL kwargs
        instance = self.get_object()

        # Make a mutable copy of the request data
        data = request.data.copy()

        # Set the user fields to the logged-in user for tracking updates
        data['last_updated_by_id'] = request.user.id

        # Check if the task exists and set the related project and phase fields
        task_id = data.get("task")
        
        if task_id:
            try:
                task = Task.objects.get(pk=task_id)
            except Task.DoesNotExist:
                return Response({'error': 'Invalid task.'}, status=status.HTTP_400_BAD_REQUEST)

            # Update project and phase based on the task
            # data['project'] = task.project.project_id
            data['phase'] = task.phase.phase_id

        # Pass the data to the serializer along with the instance to update
        serializer = self.get_serializer(instance, data=data, partial=True)  # Use partial=True to allow partial updates
        serializer.is_valid(raise_exception=True)

        # Save the updated data
        self.perform_update(serializer)

        # Return the updated instance data as a response
        return Response(serializer.data, status=status.HTTP_200_OK)
            

class LeaveTypeViewSet(viewsets.ModelViewSet):
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer


class AbsenceViewSet(viewsets.ModelViewSet):
    queryset = Absence.objects.all()
    serializer_class = AbsenceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            match user.admin_user.admin_type.name:
                case "SUP":
                  return Absence.objects.all()
                case "INS":
                  return Absence.objects.filter(entity__instance = user.employee_user.instance)
                case "ENT":
                    return Absence.objects.filter(project__entity= user.employee_user.entity)  
                case "UNI":
                    return Absence.objects.filter(project__unit= user.employee_user.unit)

        return Absence.objects.filter(employee = user.employee_user)
    
    def create(self, request, *args, **kwargs):
        # Make a mutable copy of the request data
        data = request.data.copy()

        # Set the user field to the logged-in user
        data['user'] = request.user.id
        data['last_updated_by_id'] = request.user.id
        data['created_by_id'] = request.user.id

    
        # Pass the data to the serializer and validate it
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        # Save the data
        self.perform_create(serializer)

        # Return the response
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    
    def update(self, request, *args, **kwargs):
        # Get the instance to be updated using the primary key from URL kwargs
        instance = self.get_object()

        # Make a mutable copy of the request data
        data = request.data.copy()

        # Set the user fields to the logged-in user for tracking updates
        data['last_updated_by_id'] = request.user.id


        # Pass the data to the serializer along with the instance to update
        serializer = self.get_serializer(instance, data=data, partial=True)  # Use partial=True to allow partial updates
        serializer.is_valid(raise_exception=True)

        # Save the updated data
        self.perform_update(serializer)

        # Return the updated instance data as a response
        return Response(serializer.data, status=status.HTTP_200_OK)
            

    
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
                  return Expense.objects.filter(entity__instance = user.employee_user.instance)
                case "ENT":
                    return Expense.objects.filter(project__entity= user.employee_user.entity)  
                case "UNI":
                    return Expense.objects.filter(project__unit= user.employee_user.unit)

        return Expense.objects.filter(employee = user.employee_user)
    
    def create(self, request, *args, **kwargs):
        # Make a mutable copy of the request data
        data = request.data.copy()

        # Set the user field to the logged-in user
        data['user'] = request.user.id
        data['last_updated_by_id'] = request.user.id
        data['created_by_id'] = request.user.id

        # task_id = data.get("task")

        # if task_id:
        # # Fetch the task instance
        #     try:
        #         task = Task.objects.get(pk=task_id)
        #     except Task.DoesNotExist:
        #         return Response({'error': 'Invalid task.'}, status=status.HTTP_400_BAD_REQUEST)
            
        #     data['phase'] = task.phase.phase_id

        # Pass the data to the serializer and validate it
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        # Save the data
        self.perform_create(serializer)

        # Return the response
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request, *args, **kwargs):
        # Get the instance to be updated using the primary key from URL kwargs
        instance = self.get_object()

        # Make a mutable copy of the request data
        data = request.data.copy()

        # Set the user fields to the logged-in user for tracking updates
        data['last_updated_by_id'] = request.user.id

        # Check if the task exists and set the related project and phase fields
        task_id = data.get("task")
        
        if task_id:
            try:
                task = Task.objects.get(pk=task_id)
            except Task.DoesNotExist:
                return Response({'error': 'Invalid task.'}, status=status.HTTP_400_BAD_REQUEST)

            # Update project and phase based on the task
            data['project'] = task.project.project_id
            data['phase'] = task.phase.phase_id

        # Pass the data to the serializer along with the instance to update
        serializer = self.get_serializer(instance, data=data, partial=True)  # Use partial=True to allow partial updates
        serializer.is_valid(raise_exception=True)

        # Save the updated data
        self.perform_update(serializer)

        # Return the updated instance data as a response
        return Response(serializer.data, status=status.HTTP_200_OK)
            
    


class TimesheetView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request,*args, **kwargs):
        user = request.user
        current_date = now().date()
        editable_date = current_date - timedelta(days=7)


        week_start = request.query_params.get('week',None)

         # If no week is provided, use current week starting Monday
        if week_start:
            week_start = datetime.strptime(week_start, '%Y-%m-%d') -timedelta(days=current_date.weekday())
        else:
            week_start = current_date - timedelta(days=current_date.weekday())  # Get Monday of the current week

        
        week_end = week_start + timedelta(days=6)

        # Group work_entries, absences, and expenses by day
        data = defaultdict(lambda: {
            'work_entries': [],
            'absences': [],
            'expenses': []
        })

        work_entries = WorkEntries.objects.filter(
            user=user, date__range=[week_start,week_end]
        ).values('work_entries_id','date', 'start_time', 'end_time','duration','task_type','customer__customer_name' , 'task_id' ,'task__task_name','project__project_name','phase__phase_name','sale', 'sale__sales_name','sales_task__task_name' ,'description')

        absences = Absence.objects.filter(
            user=user, absence_date__range=[week_start,week_end]
        ).values('absence_id','absence_date', 'start_time', 'end_time','duration','leave_type','leave_type__name' ,'project_id','project__project_name', 'sale', 'sale__sales_name', 'absence_description')
        
        expenses = Expense.objects.filter(
            user = user, date__range=[week_start,week_end]
        ).values('expense_id', 'date', 'value', 'description', 'task_id' ,'task__task_name','customer__customer_name' ,'project__project_name','phase__phase_name','sale', 'sale__sales_name', 'sales_task_id', 'sales_task__task_name')

                # Convert timedelta to hours and minutes
        def convert_timedelta_to_hours_minutes(duration):
            if duration != 0:
                total_seconds = duration.total_seconds()
            else:
                total_seconds = duration
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60) or "00"
            return f"{hours}:{minutes} "
    

        #Group entries by task_date

        for entry in work_entries:
            day_name = entry['date'].strftime('%A')
            # Convert duration to hours and minutes
            entry['duration'] = convert_timedelta_to_hours_minutes(entry['duration'])

            # Add an editable flag
            entry['editable'] = entry['date'] >= editable_date
            data[day_name]['work_entries'].append(entry)

        # Group absences by date

        for absence in absences:
            day_name = absence['absence_date'].strftime('%A')
            # Convert duration to hours and minutes
            absence['duration'] =convert_timedelta_to_hours_minutes(absence['duration'])

            # Add an editable flag
            absence['editable'] = absence['absence_date'] >= editable_date
            data[day_name]['absences'].append(absence)

        
        #Group expenses by date

        for expense in expenses:
            day_name = expense['date'].strftime('%A')

            # Add an editable flag
            expense['editable'] = expense['date'] >= editable_date
            data[day_name]['expenses'].append(expense)


        total_work_hours = work_entries.aggregate(total_duration= Sum('duration'))['total_duration'] or 0
        total_absence_hours = absences.aggregate(total_duration=Sum('duration'))['total_duration'] or 0
        total_expenses = expenses.aggregate(total_expenses = Sum('value'))['total_expenses'] or 0




        # Use the function to format the total durations
        formatted_work_duration = convert_timedelta_to_hours_minutes(total_work_hours)
        formatted_absence_duration = convert_timedelta_to_hours_minutes(total_absence_hours)
        
        #Fill data with all days of the week
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for day in days_of_week:
            if day not in data:
                data[day] = {'work_entries': [], 'absences': [], 'expenses': []}


        response_data = {
            'week_start' : week_start,
            'week_end': week_end,
            'total_work_duration': formatted_work_duration,
            'total_absence_duration': formatted_absence_duration,
            'total_expenses': total_expenses,
            'days': data
        }

        return Response(response_data)
    
