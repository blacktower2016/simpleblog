# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-11-17 16:47
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('simpleblog', '0017_auto_20171117_1644'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='tag',
            new_name='tags',
        ),
    ]
