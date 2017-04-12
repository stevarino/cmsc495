from mac_app.models import Ticket, Employee, EmployeeDept
from rest_framework import serializers


class TicketSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Ticket
        fields = ('url', 'modification_user', 'target', 'state', 
                'creation_date', 'modification_date')


class EmployeeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Employee
        fields = ('url', 'domain', 'username', 'department')

class EmployeeDeptSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EmployeeDept
        fields = ('url', 'name')