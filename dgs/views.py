from django.shortcuts import render
import models


def home(request):
    print models.League.objects.get(name__icontains="saturday").events.all()
    context = {
            'leagues': models.League.objects.all()
            }
    return render(request, 'index.html', context)
