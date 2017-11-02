# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-01 01:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('uniconnect_app', '0012_auto_20171031_0006'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='tagged', to='uniconnect_app.Tag'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='profics',
            field=models.IntegerField(default=1),
        ),
    ]
