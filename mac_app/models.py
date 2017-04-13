# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from datetime import datetime
import uuid

def get_new_ticket_number():
    id = str(uuid.uuid4()).replace('-','').upper()
    i = 6
    while 0 < Ticket.objects.filter(number=id[0:i]).count():
        i += 1
        if i > 32:
            id = str(uuid.uuid4()).replace('-','').upper()
            i = 6
    return "TK"+id[0:i]

# Create your models here.
class Ticket(models.Model):
    number = models.CharField(max_length=32, default=get_new_ticket_number)
    creation_date = models.DateTimeField('date created', 
            default=datetime.now)
    
    author = models.ForeignKey("Employee", 
            related_name='tickets_started')
    target = models.ForeignKey("Employee", 
            related_name='tickets')
    state = models.ForeignKey("TicketState")

    parent_ticket = models.ForeignKey("self", on_delete=models.CASCADE, blank=True, 
            null=True)

    modification_date = models.DateTimeField()
    modification_user = models.ForeignKey("Employee", blank=True, 
            related_name='tickets_touched')

    def __str__(self):
        return self.number

class Mail(models.Model):
    receiver = models.ForeignKey("Employee", 
            related_name='mail_received')
    sender = models.ForeignKey("Employee", 
            related_name='mail_sent')
    sent_date = models.DateTimeField(default=datetime.now)
    is_read = models.IntegerField(default=0)
    subject = models.CharField(max_length=1024)
    message = models.CharField(max_length=1024)

    def __str__(self):
        return "{} To: {} From: {} {}".format(sent_date, receiver, 
            sender, subject)

class TicketState(models.Model):
    name = models.CharField(max_length=16)
    friendly_name = models.CharField(max_length=256)
    details = models.TextField()

    substate = models.ManyToManyField("self", blank=True)

    roles = models.ManyToManyField("EmployeeRole", blank=True)

    def __str__(self):
        return self.name

class TicketStateNext(models.Model):
    state = models.ForeignKey("TicketState", on_delete=models.CASCADE)
    title = models.CharField(max_length=128)
    sort_field = models.IntegerField(default=0)
    css = models.ForeignKey("TicketStateNextCss", blank=True)
    next_state = models.ForeignKey("TicketState", related_name="next", blank=True)

    def __str__(self):
        return "[{}] {} [{}]".format(self.state, self.title, self.next_state)

class TicketStateNextCss(models.Model):
    name = models.CharField(max_length=32)
    css = models.CharField(max_length=128)

    def __str__(self):
        return self.name

class Employee(models.Model):
    domain = models.CharField(max_length=128, default='corp')
    username = models.CharField(max_length=16)
    firstname = models.CharField(max_length=128)
    lastname = models.CharField(max_length=128)
    address = models.CharField(max_length=256, blank=True)
    city = models.CharField(max_length=128, blank=True)
    state = models.CharField(max_length=128, blank=True)
    postal_code = models.CharField(max_length=16, blank=True)
    phone = models.CharField(max_length=16, blank=True)
    department = models.ForeignKey("EmployeeDept", blank=True, null=True)
    roles = models.ManyToManyField("EmployeeRole", blank=True)
    creation_date = models.DateTimeField('date created', 
        default=datetime.now)

    def __str__(self):
        return "{}.{} [{}]".format(self.domain, self.username, 
                self.department)

class EmployeeRole(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name
    
class EmployeeDept(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name

class LogEntry(models.Model):
    description = models.TextField(blank=True)
    creation_date = models.DateTimeField('date created', 
            default=datetime.now)
    user = models.ForeignKey("Employee")
    state_from = models.ForeignKey("TicketState", blank=True, related_name="+")
    state_to = models.ForeignKey("TicketState", blank=True, related_name="+")
    ticket = models.ForeignKey("Ticket")


    def __str__(self):
        return "[{}] {} ({} -> {})".format(self.ticket, self.creation_date, 
                self.state_from, self.state_to)