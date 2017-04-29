# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

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
    return "TK-"+id[0:i]

ticket_state = (
    ('n', 'Pending'), # new
    ('w', 'Awaiting Response'), # waiting
    ('p', 'In Progress'), # in progress
    ('c', 'Complete'), # complete
)

# Create your models here.
class Ticket(models.Model):
    number = models.CharField(max_length=32, default=get_new_ticket_number)
    creation_date = models.DateTimeField('date created', 
            default=datetime.now)

    modification_date = models.DateTimeField(auto_now=True)
    
    author = models.ForeignKey(User, related_name='tickets_started')
    target = models.ForeignKey(User, related_name='tickets')
    ticket_type = models.ForeignKey("TicketType")
    
    stage = models.IntegerField(default=0, verbose_name='Current Step')
    is_complete = models.BooleanField(default=False)

    dsk_stage = models.CharField(max_length=1, choices=ticket_state, default='n', 
            verbose_name='Desktop Support Stage')
    net_stage = models.CharField(max_length=1, choices=ticket_state, default='n', 
            verbose_name='Network Admin Stage')
    fac_stage = models.CharField(max_length=1, choices=ticket_state, default='n', 
            verbose_name='Facilities Stage')

    def __str__(self):
        return self.number

    def dsk_stage_text(self):
        return dict(ticket_state)[self.dsk_stage]

    def net_stage_text(self):
        return dict(ticket_state)[self.net_stage]

    def fac_stage_text(self):
        return dict(ticket_state)[self.fac_stage]

    # department stage updated
    def set_dept_stage(self, dept, state):
        setattr(self, dept+'_stage', state)
        self.process_stage()
                
    # determines if the current stage is done and if so increment
    def process_stage(self):
        if (self.dsk_stage == 'c' and self.net_stage == 'c' 
                and self.fac_stage == 'c'):
            self.is_complete = True
            self.save()
            return
        next_stage = True
        for dept in ['dsk', 'net', 'fac']:
            department = Department.objects.get(name=dept.upper())
            if getattr(self.ticket_type, dept+'_seq') == self.stage:
                next_stage = next_stage and getattr(self, dept+'_stage') == 'c'

        if next_stage: 
            self.stage += 1
            self.enter_stage()

        self.save()

    # handled at beginning of each stage
    def enter_stage(self):
        for dept in ['dsk', 'net', 'fac']:
            department = Department.objects.get(name=dept.upper())

            # mark non-required departments  as complete
            if getattr(self.ticket_type, dept+'_seq') == -1:
                setattr(self, dept+'_stage', 'c')

            if getattr(self.ticket_type, dept+'_seq') == self.stage:
                if getattr(self, dept+'_stage') == 'n':
                # mark new steps as pending
                    setattr(self, dept+'_stage', 'w')
                    users = Profile.objects.filter(department=department)
                    # TODO: email users
        self.save()


class TicketType(models.Model):
    name = models.CharField(max_length=16)
    code = models.CharField(max_length=4, default='')

    dsk_seq = models.IntegerField(default=0, 
        verbose_name='Desktop Sequence')
    dsk_msg = models.TextField(verbose_name='Desktop Message', blank=True)

    net_seq = models.IntegerField(default=0,
        verbose_name='Network Sequence')
    net_msg = models.TextField(verbose_name='Network Message', blank=True)

    fac_seq = models.IntegerField(default=0, 
        verbose_name='Facilities Sequence')
    fac_msg = models.TextField(verbose_name='Facilities Message', blank=True)

    def __str__(self):
        return self.name

class TicketNote(models.Model):
    ticket = models.ForeignKey("Ticket")
    author = models.ForeignKey(User)
    # department added as superuser will have multiple departments
    department = models.ForeignKey("Department", blank=True)
    creation_date = models.DateTimeField('date created', 
            default=datetime.now)

    from_state = models.CharField(max_length=1, choices=ticket_state, blank=True)
    to_state = models.CharField(max_length=1, choices=ticket_state, blank=True)

    content = models.TextField(blank=True)

    def from_state_text(self):
        return dict(ticket_state)[self.from_state]

    def to_state_text(self):
        return dict(ticket_state)[self.to_state]

    def __str__(self):
        return "{} - {} [{}] {}".format(self.ticket.number, self.author, 
                self.department.name, self.creation_date)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    domain = models.CharField(max_length=128, default='corp')
    address = models.CharField(max_length=256, blank=True)
    city = models.CharField(max_length=128, blank=True)
    state = models.CharField(max_length=128, blank=True)
    postal_code = models.CharField(max_length=16, blank=True)
    phone = models.CharField(max_length=16, blank=True)
    department = models.ForeignKey("Department", blank=True, null=True)

    def __str__(self):
        return "{}".format(self.user)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Department(models.Model):
    name = models.CharField(max_length=10)
    description = models.CharField(max_length=128, default='')

    def __str__(self):
        return "{} [{}]".format(self.description, self.name)