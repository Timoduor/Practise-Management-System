from django.shortcuts import render
from rest_framework import viewsets
from .models import Customer, Contact, Sales
from .serializers import CustomerSerializer, ContactSerializer, SalesSerializer

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

class SalesViewSet(viewsets.ModelViewSet):
    queryset = Sales.objects.all()
    serializer_class = SalesSerializer

