from django.shortcuts import render
from rest_framework import viewsets
from .models import Customer, Contact, Sales, Project, Task, Invoice, ProjectPhase, WorkEntries, Absence, Expense, LeaveType
from .serializers import CustomerSerializer, ContactSerializer, SalesSerializer, ProjectSerializer, TaskSerializer, InvoiceSerializer, ProjectPhaseSerializer, WorkEntriesSerializer,AbsenceSerializer,ExpenseSerializer, LeaveTypeSerializer
from rest_framework.permissions import IsAuthenticated

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