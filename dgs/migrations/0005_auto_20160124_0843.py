# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-23 21:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dgs', '0004_auto_20160112_2230'),
    ]

    operations = [
        migrations.AlterField(
            model_name='score',
            name='strokes',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]