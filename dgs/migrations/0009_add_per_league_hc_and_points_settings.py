# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dgs', '0008_add_optional_hole_length_and_notes_properties'),
    ]

    operations = [
        migrations.AddField(
            model_name='league',
            name='handicap_max_rounds_avg',
            field=models.IntegerField(default=8),
        ),
        migrations.AddField(
            model_name='league',
            name='handicap_min_rounds',
            field=models.IntegerField(default=2),
        ),
        migrations.AddField(
            model_name='league',
            name='handicap_min_rounds_avg',
            field=models.IntegerField(default=5),
        ),
        migrations.AddField(
            model_name='league',
            name='handicap_multiplier',
            field=models.FloatField(default=0.8),
        ),
        migrations.AddField(
            model_name='league',
            name='league_points',
            field=models.CharField(default=b'10,9,8,7,6,5,4,3,2,1', max_length=50),
        ),
    ]
