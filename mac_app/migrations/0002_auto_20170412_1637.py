# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-12 16:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mac_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='city',
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.AddField(
            model_name='employee',
            name='postal_code',
            field=models.CharField(blank=True, max_length=16),
        ),
        migrations.AddField(
            model_name='employee',
            name='state',
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.AlterField(
            model_name='employee',
            name='department',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='mac_app.EmployeeDept'),
        ),
    ]
