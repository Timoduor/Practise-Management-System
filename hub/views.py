from django.shortcuts import render
from rest_framework import viewsets
from .models import Customer, Contact, Sales, Project, Task, Invoice, ProjectPhase, WorkEntries, Absence, Expense, LeaveType
from .serializers import CustomerSerializer, ContactSerializer, SalesSerializer, ProjectSerializer, TaskSerializer, InvoiceSerializer, ProjectPhaseSerializer, WorkEntriesSerializer,AbsenceSerializer,ExpenseSerializer, LeaveTypeSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import  status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.timezone import now
from datetime import datetime, timedelta
from collections import defaultdict
from django.db.models import Sum

class CustomerViewSet(viewsets.ModelViewSet):
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
                  return Contact.objects.filter(entity__instance = user.employee_user.instance)
                case "ENT":
                    return Contact.objects.filter(entity= user.employee_user.entity)  
                case "UNI":
                    return Contact.objects.filter(unit= user.employee_user.unit)

        return Contact.objects.filter(unit = user.employee_user.unit)

class SalesViewSet(viewsets.ModelViewSet):
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

        return Sales.objects.filter(sales_members = user.employee_user)


class ProjectViewSet(viewsets.ModelViewSet):
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

        return Project.objects.filter(project_members = user.employee_user) 

class ProjectPhaseViewSet(viewsets.ModelViewSet):
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

class TaskViewSet(viewsets.ModelViewSet):
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

class InvoiceViewSet(viewsets.ModelViewSet):
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

            # Fetch the task instance
            try:
                task = Task.objects.get(pk=task_id)
            except Task.DoesNotExist:
                return Response({'error': 'Invalid task.'}, status=status.HTTP_400_BAD_REQUEST)
            
            data['project'] = task.project.project_id
            data['phase'] = task.phase.phase_id

            # Pass the data to the serializer and validate it
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)

            # Save the data
            self.perform_create(serializer)

            # Return the response
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    
        

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

        task_id = data.get("task")

        # Fetch the task instance
        try:
            task = Task.objects.get(pk=task_id)
        except Task.DoesNotExist:
            return Response({'error': 'Invalid task.'}, status=status.HTTP_400_BAD_REQUEST)
        
        data['project'] = task.project.project_id
        data['phase'] = task.phase.phase_id

        # Pass the data to the serializer and validate it
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        # Save the data
        self.perform_create(serializer)

        # Return the response
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    


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
        ).values('work_entries_id','date', 'start_time', 'end_time','duration','task_type' ,'task__task_name','task__project','task__project__project_name', 'description')

        absences = Absence.objects.filter(
            user=user, absence_date__range=[week_start,week_end]
        ).values('absence_id','absence_date', 'start_time', 'end_time','duration','leave_type__name' ,'project_id','project__project_name', 'absence_description')
        
        expenses = Expense.objects.filter(
            user = user, date__range=[week_start,week_end]
        ).values('expense_id', 'date', 'value', 'description','task_id','task__task_name')

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
            day_name = entry['date'].strftime('%A')

            # Add an editable flag
            expense['editable'] = expense['date'] >= editable_date
            data[day_name]['expenses'].append(expense)


        total_work_hours = work_entries.aggregate(total_duration= Sum('duration'))['total_duration'] or 0
        total_absence_hours = absences.aggregate(total_duration=Sum('duration'))['total_duration'] or 0
        total_expenses = expenses.aggregate(total_expenses = Sum('value'))['total_expenses'] or 0




        # Use the function to format the total durations
        formatted_work_duration = convert_timedelta_to_hours_minutes(total_work_hours)
        formatted_absence_duration = convert_timedelta_to_hours_minutes(total_absence_hours)


        response_data = {
            'week_start' : week_start,
            'week_end': week_end,
            'total_work_duration': formatted_work_duration,
            'total_absence_duration': formatted_absence_duration,
            'total_expenses': total_expenses,
            'days': data
        }

        return Response(response_data)
    
