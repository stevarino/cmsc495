# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


from .models import Ticket, TicketType, TicketNote, Department, ticket_state
from .forms import NewUserTicket

def index(request):
    context = {}
    if 'username' in request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
        else:
            context['error'] = "Unrecognized Username/Password combination."
    if request.user.is_authenticated():
        return redirect('tickets')

    return render(request, 'mac_app/login.html', context)

def logout_view(request):
    logout(request)
    return redirect('index')


# ticket list view
@login_required(login_url='/')
def tickets(request):
    context = {}

    context['is_hr'] = request.user.is_superuser or request.user.profile.department.name == 'HR'
    context['is_fac'] = request.user.is_superuser or request.user.profile.department.name == 'FAC'
    context['is_net'] = request.user.is_superuser or request.user.profile.department.name == 'NET'
    context['is_dsk'] = request.user.is_superuser or request.user.profile.department.name == 'DSK'

    context['dsk_tickets'] = Ticket.objects.filter(dsk_stage__in=['w', 'p'])
    context['fac_tickets'] = Ticket.objects.filter(fac_stage__in=['w', 'p'])
    context['net_tickets'] = Ticket.objects.filter(net_stage__in=['w', 'p'])
    context['tickets'] = Ticket.objects.order_by('-modification_date')

    return render(request, 'mac_app/tickets.html', context)

# Ticket detail view
@login_required(login_url='/')
def ticket_detail(request, ticket_num):
    context = {}
    ticket = get_object_or_404(Ticket, number=ticket_num)
    if request.method == 'POST':
        department = Department.objects.get(name=request.POST['dept'].upper())
        state = getattr(ticket, request.POST['dept']+'_stage')
        note = TicketNote(ticket=ticket, author=request.user, 
            department=department, 
            from_state=state, to_state=request.POST['state'], 
            content = request.POST['notes'])
        note.save()
        
        ticket.set_dept_stage(request.POST['dept'], request.POST['state'])

        return redirect('ticket_detail', ticket_num=ticket.number)
    context['ticket'] = ticket
    states = dict(ticket_state)

    context['is_hr'] = request.user.is_superuser or request.user.profile.department.name == 'HR'
    context['is_fac'] = request.user.is_superuser or request.user.profile.department.name == 'FAC'
    context['is_net'] = request.user.is_superuser or request.user.profile.department.name == 'NET'
    context['is_dsk'] = request.user.is_superuser or request.user.profile.department.name == 'DSK'

    context['dsk_stage'] = states[ticket.dsk_stage]
    context['net_stage'] = states[ticket.net_stage]
    context['fac_stage'] = states[ticket.fac_stage]

    return render(request, 'mac_app/ticket_detail.html', context)

# New ticket view
@login_required(login_url='/')
def ticket_new(request):
    if request.method == 'POST':
        form = NewUserTicket(request.POST)
        if form.is_valid():
            user = User.objects.create_user(form.cleaned_data['username'], '', form.cleaned_data['password'])
            user.first_name = form.cleaned_data['firstname']
            user.last_name = form.cleaned_data['lastname']
            for f in 'address city state postal_code phone department'.split(' '):
                setattr(user.profile, f, form.cleaned_data[f])
            user.save()

            new_type = TicketType.objects.get(code='nw')
            ticket = Ticket(author=request.user, target=user, ticket_type=new_type)
            ticket.save()

            note = TicketNote(ticket=ticket, author=request.user, 
                department=Department.objects.get(name='HR'), 
                from_state='n', to_state='c', 
                content = request.POST['notes'])
            note.save()

            ticket.enter_stage()

            return redirect('ticket_detail', ticket_num=ticket.number)
    else:
        form = NewUserTicket()

    return render(request, 'mac_app/ticket_new.html', {'form': form})

# move ticket
@login_required(login_url='/')
def ticket_move(request):
    return render(request, 'mac_app/blank.html')

# remove ticket
@login_required(login_url='/')
def ticket_remove(request):
    return render(request, 'mac_app/blank.html')


