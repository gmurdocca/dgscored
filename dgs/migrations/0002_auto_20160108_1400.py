# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dgs', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='totalscore',
            options={'verbose_name': 'Score', 'verbose_name_plural': 'Scores'},
        ),
        migrations.AlterField(
            model_name='totalscore',
            name='current_handicap',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
