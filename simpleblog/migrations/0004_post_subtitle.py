# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-11-13 16:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('simpleblog', '0003_auto_20171112_1838'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='subtitle',
            field=models.CharField(blank=True, max_length=120, null=True),
        ),
    ]
