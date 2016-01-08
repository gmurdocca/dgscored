# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Award',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('hole_count', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b"Name of event, eg 'September League Day'", max_length=50, null=True, blank=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('rounds', models.IntegerField(help_text=b'Number of rounds that players are required to complete during this league event')),
                ('awards', models.ManyToManyField(to='dgs.Award', blank=True)),
                ('cards', models.ManyToManyField(to='dgs.Card', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Hole',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number', models.IntegerField()),
                ('par', models.IntegerField()),
                ('course', models.ForeignKey(to='dgs.Course')),
            ],
        ),
        migrations.CreateModel(
            name='Layout',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('course', models.ForeignKey(to='dgs.Course')),
            ],
        ),
        migrations.CreateModel(
            name='League',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('events', models.ManyToManyField(to='dgs.Event', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('handicap', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='TotalScore',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('current_handicap', models.IntegerField(null=True, editable=False, blank=True)),
                ('total_strokes', models.IntegerField()),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('holes', models.ManyToManyField(to='dgs.Hole')),
                ('player', models.ForeignKey(to='dgs.Player')),
            ],
        ),
        migrations.AddField(
            model_name='hole',
            name='layout',
            field=models.ForeignKey(to='dgs.Layout'),
        ),
        migrations.AddField(
            model_name='card',
            name='course',
            field=models.ForeignKey(to='dgs.Course'),
        ),
        migrations.AddField(
            model_name='card',
            name='players',
            field=models.ManyToManyField(to='dgs.Player'),
        ),
        migrations.AddField(
            model_name='card',
            name='total_scores',
            field=models.ManyToManyField(to='dgs.TotalScore', blank=True),
        ),
        migrations.AddField(
            model_name='award',
            name='player',
            field=models.ForeignKey(to='dgs.Player'),
        ),
    ]
