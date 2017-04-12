# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets
from serializers import TicketSerializer, EmployeeSerializer, EmployeeDeptSerializer
from models import Ticket, Employee, EmployeeDept

# Create your views here.

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all().order_by('-modification_date')
    serializer_class = TicketSerializer

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all().order_by('username')
    serializer_class = EmployeeSerializer

class EmployeeDeptViewSet(viewsets.ModelViewSet):
    queryset = EmployeeDept.objects.all().order_by('name')
    serializer_class = EmployeeDeptSerializer