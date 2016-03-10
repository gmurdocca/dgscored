# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dgs', '0005_auto_20160124_0843'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contestant',
            name='initial_handicap',
            field=models.FloatField(default=None, null=True, blank=True),
        ),
    ]
