# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dgs', '0002_auto_20160109_1602'),
    ]

    operations = [
        migrations.AddField(
            model_name='contestant',
            name='current_handicap',
            field=models.IntegerField(default=None, null=True, editable=False, blank=True),
        ),
    ]
