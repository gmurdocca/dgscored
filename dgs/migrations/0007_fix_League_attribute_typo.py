# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dgs', '0006_support_decimal_handicap_values'),
    ]

    operations = [
        migrations.RenameField(
            model_name='league',
            old_name='contentants',
            new_name='contestants',
        ),
    ]
