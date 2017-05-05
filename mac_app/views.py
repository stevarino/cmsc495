# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.core.exceptions import PermissionDenied

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


from .models import Ticket, TicketType, TicketNote, Department
from .forms import NewUserTicket, UserSearchForm

def index(request):
    '''Unauthenticated login view'''
    context = {'no_sidebar': True}
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
    '''Logout view. Unauthenticates user.'''
    logout(request)
    return redirect('index')


# ticket list view
@login_required(login_url='/')
def tickets(request):
    '''Ticket Overview page (multiple tickets)'''
    context = {}

    user_dept = request.user.profile.department.name.lower()

    context['is_hr'] = request.user.is_superuser or user_dept == 'hr'

    context['departments'] = []
    for d in ['dsk', 'fac', 'net']:
        dept = {
            'department': Department.objects.get(name=d.upper()),
            'user_in_dept': request.user.is_superuser or user_dept == d,
            'tickets': [],
        }
        for t in Ticket.objects.filter(**{d+'_stage__in': ['w', 'p']}):
            dept['tickets'].append({
                'ticket': t,
                'state': getattr(t, d+'_stage'),
                'state_text': getattr(t, d+'_stage_text'),
            })
        context['departments'].append(dept)
    context['tickets'] = Ticket.objects.order_by('-modification_date')

    return render(request, 'mac_app/tickets.html', context)

# User view
@login_required(login_url='/')
def user_view(request, username):
    '''View user info.'''
    context = {}
    user = get_object_or_404(User, username=username)

    context['user'] = user
    context['tickets'] = Ticket.objects.filter(target=user).order_by(
        '-creation_date')
    context['notes'] = TicketNote.objects.filter(author=user).order_by(
        '-creation_date')

    user_dept = request.user.profile.department.name.lower()

    context['is_hr'] = request.user.is_superuser or user_dept == 'hr'

    return render(request, 'mac_app/user.html', context)


# Ticket detail view
@login_required(login_url='/')
def ticket_detail(request, ticket_num):
    '''Ticket detail page (single ticket)'''
    context = {}
    ticket = get_object_or_404(Ticket, number=ticket_num)
    is_super = request.user.is_superuser or request.user.profile.department.name == 'admin'

    if request.method == 'POST':
        department = Department.objects.get(name=request.POST['dept'].upper())

        require_dept(department)

        state = getattr(ticket, request.POST['dept']+'_stage')
        note = TicketNote(ticket=ticket, author=request.user,
                          department=department,
                          from_state=state, to_state=request.POST['state'],
                          content=request.POST['notes'])
        note.save()

        ticket.set_dept_stage(request.POST['dept'], request.POST['state'])

        return redirect('ticket_detail', ticket_num=ticket.number)

    context['ticket'] = ticket

    context['is_hr'] = is_super or request.user.profile.department.name == 'HR'
    context['is_fac'] = is_super or request.user.profile.department.name == 'FAC'
    context['is_net'] = is_super or request.user.profile.department.name == 'NET'
    context['is_dsk'] = is_super or request.user.profile.department.name == 'DSK'

    context['departments'] = [
        {
            'name': "Facilities",
            'status': ticket.fac_stage,
            'status_text': ticket.fac_stage_text(),
        },
        {
            'name': "Desktop Support",
            'status': ticket.dsk_stage,
            'status_text': ticket.dsk_stage_text(),
        },
        {
            'name': "Network Admin",
            'status': ticket.net_stage,
            'status_text': ticket.net_stage_text(),
        },
    ]

    return render(request, 'mac_app/ticket_detail.html', context)

# New ticket view
@login_required(login_url='/')
def ticket_new(request):
    '''Creates a ticket for a new user.'''
    require_dept('HR')

    if request.method == 'POST':
        form = NewUserTicket(request.POST)
        if form.is_valid():
            user = User.objects.create_user(form.cleaned_data['username'], '',
                                            form.cleaned_data['password'])
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
                              content=request.POST['notes'])
            note.save()

            ticket.enter_stage()

            return redirect('ticket_detail', ticket_num=ticket.number)
    else:
        form = NewUserTicket()

    return render(request, 'mac_app/ticket_new.html', {'form': form})

@login_required(login_url='/')
def ticket_edit(request, action):
    '''Creates a user edit ticket with a sepcific action (move, remove)'''
    require_dept('HR')
    if action not in ['move_user', 'remove_user']:
        raise Http404("Action not found")
    users = []
    form = UserSearchForm()
    if request.method == 'GET':
        form = UserSearchForm(request.GET)
        if form.is_valid():
            users = form.get_users()
    return render(request, 'mac_app/user_search.html',
                  {'form': form, 'users': users, 'action': action})


@login_required(login_url='/')
def ticket_user(request, action, username):
    '''Creates a user edit ticket with a specific action and user'''
    require_dept('HR')
    types = {'move_user': 'mv', 'remove_user': 'rm'}
    user = get_object_or_404(User, username=username)
    if action not in types.keys():
        raise Http404("Action not found")

    if request.method == 'POST' and 'notes' in request.POST:
        return create_ticket(request.user, types[action], user,
                             notes=request.POST['notes'])

    return render(request, 'mac_app/ticket_user.html', {
        'user': user,
        'type': TicketType.objects.get(code=types[action])
    })



# function to create a ticket for all three paths.
def create_ticket(req_user, type_code, user, notes='', dept='HR'):
    '''Helper function to create a ticket.'''
    new_type = TicketType.objects.get(code=type_code)
    ticket = Ticket(author=req_user, target=user, ticket_type=new_type)
    ticket.save()

    note = TicketNote(ticket=ticket, author=req_user,
                      department=Department.objects.get(name=dept),
                      from_state='n', to_state='c',
                      content=notes)
    note.save()

    ticket.enter_stage()

    return redirect('ticket_detail', ticket_num=ticket.number)

def require_dept(dept):
    '''Helper function to check the authenticated user belongs to the given
    department (or is a super user)'''
    is_super = request.user.is_superuser or request.user.profile.department.name == 'admin'
    if not is_super and request.user.profile.department.name != dept:
        raise PermissionDenied


@login_required(login_url='/')
def users_view(request):
    '''User search form.'''
    users = []
    form = UserSearchForm()
    if request.method == 'GET':
        form = UserSearchForm(request.GET)
        if form.is_valid():
            users = form.get_users()
    return render(request, 'mac_app/user_search.html', 
            {'form': form, 'users': users})