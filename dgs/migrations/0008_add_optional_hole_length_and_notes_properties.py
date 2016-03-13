# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dgs', '0007_fix_League_attribute_typo'),
    ]

    operations = [
        migrations.AddField(
            model_name='hole',
            name='length',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='hole',
            name='notes',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='player',
            name='phone_number',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
    ]
