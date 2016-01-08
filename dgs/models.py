from django.db import models
from collections import OrderedDict, defaultdict
from dgscored import settings
import numpy


class Player(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    handicap = models.IntegerField(default=0)

    def calculate_handicap(self):
        best_two_from_five_previous_results = \
                sorted([float(c.get_result()[self]["scratch_delta"]) for c in self.card_set.order_by('-id')[:5]])[:2]
        if not best_two_from_five_previous_results:
            return 0
        new_hc = int(numpy.mean(best_two_from_five_previous_results))
        self.handicap = new_hc
        self.save()
        return new_hc

    @property
    def name(self):
        return "%s %s" % (self.first_name, self.last_name)

    def __unicode__(self):
        return self.name


class Course(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name


class Layout(models.Model):
    name = models.CharField(max_length=50)
    course = models.ForeignKey(Course)

    def __unicode__(self):
        return self.name

    def get_par(self):
        holes = self.hole_set.all()
        return sum([h.par for h in holes])


class Hole(models.Model):
    number = models.IntegerField()
    par = models.IntegerField()
    layout = models.ForeignKey(Layout)
    course = models.ForeignKey(Course)

    def __unicode__(self):
        return "Hole %s: Par %s, %s layout, %s" % (self.number, self.par, self.layout, self.course)


class TotalScore(models.Model):
    """
    Model for overall scratch score for a player on a card after their round
    """
    player = models.ForeignKey(Player)
    current_handicap = models.IntegerField(blank=True, null=True)
    holes = models.ManyToManyField(Hole)
    total_strokes = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.current_handicap = self.player.handicap
        super(TotalScore, self).save(*args, **kwargs)

    def __unicode__(self):
        return "%s - %s - %s" % (self.total_strokes, self.date.ctime(), self.player)

    class Meta:
        verbose_name = "Score"
        verbose_name_plural = "Scores"


class Card(models.Model):
    course = models.ForeignKey(Course)
    players = models.ManyToManyField(Player)
    date = models.DateTimeField(auto_now_add=True)
    hole_count = models.IntegerField(default=0)
    total_scores = models.ManyToManyField(TotalScore, blank=True)

    def __unicode__(self):
        return "%s (%s)" % (self.date, ", ".join([p.name for p in self.players.all()]))

    def get_layout(self):
        return self.total_scores.last().holes.last().layout

    def get_date(self):
        return self.date.strftime("%a %b %d %H:%M, %Y")

    def get_players(self):
        return ", ".join([str(p) for p in self.players.all()])

    def get_result(self):
        result = OrderedDict()
        for tscore in self.total_scores.all():
            player = tscore.player
            layout_par = tscore.holes.last().layout.get_par()
            scratch_score = tscore.total_strokes
            scratch_delta = scratch_score - layout_par
            handicap = tscore.current_handicap
            handicap_score = scratch_score - handicap
            handicap_delta = handicap_score - layout_par
            result[player] = {}
            result[player]["handicap"] = handicap
            result[player]["scratch_score"] = scratch_score
            result[player]["scratch_delta"] = str(scratch_delta) if scratch_delta < 0 else "+%s" % scratch_delta
            result[player]["handicap_score"] = handicap_score
            result[player]["handicap_delta"] = handicap_delta if handicap_delta < 0 else "+%s" % handicap_delta
        # sort by rank
        result = OrderedDict(sorted(result.iteritems(), key=lambda x: x[1]["handicap_score"]))
        return result


class Award(models.Model):
    """
    Generic award model, eg. CTP
    """
    name = models.CharField(max_length=50, blank=True, null=True)
    player = models.ForeignKey(Player)

    def __unicode__(self):
        return "%s: %s" % (self.name, self.player.name)

class Event(models.Model):
    """
    Generic event model, eg. a league day
    """
    name = models.CharField(max_length=50, blank=True, null=True, help_text="Name of event, eg 'September League Day'")
    date = models.DateTimeField(auto_now_add=True)
    rounds = models.IntegerField(help_text="Number of rounds that players are required to complete during this league event")
    awards = models.ManyToManyField(Award, blank=True)
    cards = models.ManyToManyField(Card, blank=True)

    def get_date(self):
        return self.date.strftime("%a %b %d, %Y")

    def get_points(self, rank):
        """
        reutrns points earned for a player ranked at specified rank (zero indexed).
        if rank < 0 (eg. -1), minimum points attanable is returned (eg. if player
        did not complete Event.rounds rounds, then they earned minimum points for
        attendance, eg one point.
        """
        if 0 > rank > len(settings.LEAGUE_POINTS):
            return settings.LEAGUE_POINTS[-1]
        return settings.LEAGUE_POINTS[rank]

    def get_result(self):
        """
        Returns points earned by players during this event in the format:
        """
        event_result = OrderedDict()
        for card in self.cards.all():
            result = card.get_result()
            for player in result:
                stats = result[player]
                event_result[player] = defaultdict(int)
                event_result[player]['round_count'] += 1
                event_result[player]['handicap_score'] += stats['handicap_score']
                event_result[player]['awards'] = "<br />".join([a.name for a in self.awards.filter(player=player)])
        # sort by rank
        event_result = OrderedDict(sorted(event_result.iteritems(), key=lambda x: x[1]["handicap_score"]))
        # assign points earned
        for player in event_result:
            if event_result[player]['round_count'] < self.rounds < event_result[player]['round_count']:
                # give player minimum possible points if they completed less than or more than the required number
                # of rounds.
                event_result[player]['points_earned'] = self.get_points(-1)
            else:
                rank = event_result.keys().index(player)
                event_result[player]['points_earned'] = self.get_points(rank)
        return event_result

    def save(self, *args, **kwargs):
        for player in self.get_result():
            player.calculate_handicap()
        super(Event, self).save(*args, **kwargs)

    def get_course(self):
        return self.cards.last().course

    def get_layout(self):
        return self.cards.last().total_scores.last().holes.last().layout

    def __unicode__(self):
        name = self.name or "Event"
        return "%s - %s" % (name, self.date.ctime())


class League(models.Model):
    name = models.CharField(max_length=50)
    events = models.ManyToManyField(Event, blank=True)

    def __unicode__(self):
        return "%s" % self.name

    def get_standings(self):
        """
        returns {player: {'current_handicap': x, 'total_points': y}}
        """
        standings = defaultdict(int)
        for event in self.events.all():
            result = event.get_result()
            for player in result:
                standings[player] += result[player]['points_earned']
        # sort by rank
        standings = OrderedDict(sorted(standings.iteritems(), key=lambda x: x[1], reverse=True))
        return standings

    def get_event_count(self):
        return self.events.count()
