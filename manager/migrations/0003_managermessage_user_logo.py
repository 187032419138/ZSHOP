# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2019-04-27 16:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0002_auto_20190427_1624'),
    ]

    operations = [
        migrations.AddField(
            model_name='managermessage',
            name='user_logo',
            field=models.ImageField(default='', null=True, upload_to='media/uploads'),
        ),
    ]
