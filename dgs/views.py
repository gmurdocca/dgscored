from django.shortcuts import render
import models


def home(request):
    context = {
            'leagues': models.League.objects.all()
            }
    return render(request, 'index.html', context)
