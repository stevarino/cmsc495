# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from mac_app.models import Employee, EmployeeRole, EmployeeDept
from mac_app.models import Ticket, TicketState, TicketStateNext, TicketStateNextCss
    

# Register your models here.

admin.site.register(TicketState)
admin.site.register(TicketStateNext)
admin.site.register(TicketStateNextCss)

admin.site.register(EmployeeRole)
admin.site.register(EmployeeDept)
