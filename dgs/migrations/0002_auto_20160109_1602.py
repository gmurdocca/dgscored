# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dgs', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hole',
            name='par',
            field=models.IntegerField(default=3),
        ),
        migrations.AlterField(
            model_name='league',
            name='contentants',
            field=models.ManyToManyField(to='dgs.Contestant', blank=True),
        ),
    ]
