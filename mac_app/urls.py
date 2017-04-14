from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^logout$', views.logout_view, name='logout'),
    url(r'^tickets/$', views.tickets, name='tickets'),
    url(r'^tickets/(?P<ticket_num>TK-[^/]+)/$', views.ticket_detail, name='ticket_detail'),
    url(r'^tickets/move/$', views.ticket_move, name='ticket_move'),
    url(r'^tickets/remove/$', views.ticket_remove, name='ticket_remove'),
    url(r'^tickets/new/$', views.ticket_new, name='ticket_new'),
]