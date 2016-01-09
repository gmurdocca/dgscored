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
                ('date', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Contestant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('initial_handicap', models.IntegerField(default=0)),
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
                ('date', models.DateTimeField()),
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
            ],
        ),
        migrations.CreateModel(
            name='Layout',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('holes', models.ManyToManyField(to='dgs.Hole')),
            ],
        ),
        migrations.CreateModel(
            name='League',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('contentants', models.ManyToManyField(to='dgs.Contestant')),
                ('events', models.ManyToManyField(to='dgs.Event', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('email_address', models.EmailField(max_length=254, null=True, blank=True)),
                ('phone_number', models.TextField(null=True, blank=True)),
                ('pdga_number', models.IntegerField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Score',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('strokes', models.IntegerField()),
                ('date', models.DateTimeField()),
                ('contestant', models.ForeignKey(to='dgs.Contestant')),
            ],
        ),
        migrations.AddField(
            model_name='course',
            name='layouts',
            field=models.ManyToManyField(to='dgs.Layout'),
        ),
        migrations.AddField(
            model_name='contestant',
            name='player',
            field=models.ForeignKey(to='dgs.Player'),
        ),
        migrations.AddField(
            model_name='card',
            name='course',
            field=models.ForeignKey(to='dgs.Course'),
        ),
        migrations.AddField(
            model_name='card',
            name='layout',
            field=models.ForeignKey(to='dgs.Layout'),
        ),
        migrations.AddField(
            model_name='card',
            name='scores',
            field=models.ManyToManyField(to='dgs.Score', blank=True),
        ),
        migrations.AddField(
            model_name='award',
            name='contestant',
            field=models.ForeignKey(to='dgs.Contestant'),
        ),
    ]
