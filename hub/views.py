from django.shortcuts import render
from rest_framework import viewsets
from .models import Customer, Contact, Sales, Project, Task, Invoice, ProjectPhase, WorkEntries, Absence, Expense
from .serializers import CustomerSerializer, ContactSerializer, SalesSerializer, ProjectSerializer, TaskSerializer, InvoiceSerializer, ProjectPhaseSerializer, WorkEntriesSerializer,AbsenceSerializer,ExpenseSerializer

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

class SalesViewSet(viewsets.ModelViewSet):
    queryset = Sales.objects.all()
    serializer_class = SalesSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

class ProjectPhaseViewSet(viewsets.ModelViewSet):
    queryset = ProjectPhase.objects.all()
    serializer_class = ProjectPhaseSerializer

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer

class WorkEntriesViewSet(viewsets.ModelViewSet):
    queryset = WorkEntries.objects.all()
    serializer_class = WorkEntriesSerializer

class AbsenceViewSet(viewsets.ModelViewSet):
    queryset = Absence.objects.all()
    serializer_class = AbsenceSerializer

class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer