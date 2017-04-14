# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.

from mac_app.models import Ticket, TicketType, TicketNote, Profile, Department

admin.site.register(Ticket)
admin.site.register(TicketType)
admin.site.register(TicketNote)

admin.site.register(Profile)
admin.site.register(Department)