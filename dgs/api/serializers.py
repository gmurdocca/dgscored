from rest_framework import serializers
from dgs import models


class PlayerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Player
        fields = ('first_name', 'last_name', 'email_address', 'phone_number', 'pdga_number')


class ContestantSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Contestant
        fields = ('player', 'initial_handicap')


class HoleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Hole
        fields = ('number', 'par')


class LayoutSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Layout
        fields = ('name', 'holes')


class CourseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Course
        fields = ('name', 'layouts')


class ScoreSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Score
        fields = ('contestant', 'strokes', 'date')


class CardSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Card
        fields = ('course', 'layout', 'date', 'scores')


class AwardSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Award
        fields = ('name', 'contestant')


class EventSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Event
        fields = ('name', 'date', 'rounds', 'awards', 'cards')


class LeagueSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.League
        fields = ('name', 'contestants', 'events')


