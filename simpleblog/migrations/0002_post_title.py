# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-11-12 18:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('simpleblog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='title',
            field=models.CharField(default='New Post Title', max_length=50),
            preserve_default=False,
        ),
    ]
