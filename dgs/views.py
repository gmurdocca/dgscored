from django.views.decorators.cache import cache_page
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from django.shortcuts import render
from rest_framework import viewsets
from dgs.cache import cache_per
import dgs.api.serializers
import models


##### App Views ####


@cache_per(None, username="all")
def home(request):
    context = {
            'leagues': models.League.objects.all()
            }
    return render(request, 'index.html', context)


##### API Views ####

class PlayerViewSet(viewsets.ModelViewSet):
    """
    A model for a DG player. Create one instance per human.
    """
    queryset = models.Player.objects.all()
    serializer_class = dgs.api.serializers.PlayerSerializer


class ContestantViewSet(viewsets.ModelViewSet):
    """
    A model for a contestant in a League. Extends a Player by adding an optional initial handicap for them.
    A League object relates to several Contestant objects. If initial HC is not specified, then it will be
    automatically calculated by default to be: 0.8 * avg(scratch delta of first two rounds played).
    """
    queryset = models.Contestant.objects.all()
    serializer_class = dgs.api.serializers.ContestantSerializer


class HoleViewSet(viewsets.ModelViewSet):
    """
    A simple model to represent a hole.
    """
    queryset = models.Hole.objects.all()
    serializer_class = dgs.api.serializers.HoleSerializer


class LayoutViewSet(viewsets.ModelViewSet):
    """
    A model to represent a Layout of a series of Hole objects.
    Courses relate to one or more Layouts.
    """
    queryset = models.Layout.objects.all()
    serializer_class = dgs.api.serializers.LayoutSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """
    A model to represent a DG course that can contain one or more Layouts.
    """
    queryset = models.Course.objects.all()
    serializer_class = dgs.api.serializers.CourseSerializer


class ScoreViewSet(viewsets.ModelViewSet):
    """
    A simple view that stores the scratch score of a Contestant after a round. Cards relate to
    one Score per player on a Card.
    """
    queryset = models.Score.objects.all()
    serializer_class = dgs.api.serializers.ScoreSerializer


class CardViewSet(viewsets.ModelViewSet):
    """
    A model for a Card that stores Course, Layout and one or more Scores.
    """
    queryset = models.Card.objects.all()
    serializer_class = dgs.api.serializers.CardSerializer


class AwardViewSet(viewsets.ModelViewSet):
    """
    A generic Award model to capture awards for a Contestant such as Ace (hole in one)
    or CTP (closest to pin). Event objects relate to one or more Awards.
    """
    queryset = models.Award.objects.all()
    serializer_class = dgs.api.serializers.AwardSerializer


class EventViewSet(viewsets.ModelViewSet):
    """
    A model to store a league day or a similar event. Records the requisite number of rounds a
    Contestant is required to play during the event as well as Awards and Cards created during the
    Event.
    """
    queryset = models.Event.objects.all()
    serializer_class = dgs.api.serializers.EventSerializer


class LeagueViewSet(viewsets.ModelViewSet):
    """
    A model to represent a League. Stores all Events and Contestants associated with it.
    """
    queryset = models.League.objects.all()
    serializer_class = dgs.api.serializers.LeagueSerializer

