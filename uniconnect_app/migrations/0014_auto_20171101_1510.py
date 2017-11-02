# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-01 04:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('uniconnect_app', '0013_auto_20171101_1206'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='tags',
            field=models.ManyToManyField(related_name='tagged', to='uniconnect_app.Tag'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='profics',
            field=models.IntegerField(default=0),
        ),
    ]