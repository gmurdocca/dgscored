from django.shortcuts import render
from django.views.decorators.cache import cache_page
from dgs.cache import cache_per
import models

@cache_per(None, username="all")
def home(request):
    context = {
            'leagues': models.League.objects.all()
            }
    return render(request, 'index.html', context)
