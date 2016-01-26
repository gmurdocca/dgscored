from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib import admin
from django.db import models
from dgs.models import *


@admin.register(League)
@admin.register(Card)
@admin.register(Course)
@admin.register(Event)
@admin.register(Layout)
@admin.register(Player)
@admin.register(Contestant)
@admin.register(Hole)
@admin.register(Award)
@admin.register(Score)
class ModelAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.ManyToManyField: {'widget': FilteredSelectMultiple("", False)}
        }
