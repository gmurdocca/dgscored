from django.db import models
from collections import OrderedDict, defaultdict
from dgscored import settings
import numpy


class Player(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email_address = models.EmailField(blank=True, null=True)
    phone_number = models.TextField(blank=True, null=True)
    pdga_number = models.IntegerField(blank=True, null=True)

    @property
    def full_name(self):
        return "%s %s" % (self.first_name, self.last_name)

    @property
    def last_name_initial(self):
        return self.last_name[0]

    @peoperty
    def shortest_name(self):
        """
        Returns first name if unique, else first_name + last_name_initial if unique,
        else first_name + last name
        """
        same_first_names = Player.objects.filter(first_name__iexact=self.first_name)
        if len(same_first_names) == 1:
            return self.first_name
        else:
            same_last_name_initial = {}
            for player in same_first_names:
                same_last_name_initial[player.last_name_initial] = player
            if len(same_last_name_initial[self.last_name_initial]) == 1:
                return "%s %s" % (self.first_name, self.last_name_initial)
        return self.full_name

    def __unicode__(self):
        return self.name


class Contestant(models.Model):
    player = models.ForeignKey(Player)
    initial_handicap = models.IntegerField(default=0)
    handicap = models.IntegerField(blank=True, null=True, default=None, editable=False)

    @property
    def handicap(self):
        if self.handicap == None:
            return self.initial_handicap
        else:
            return self.handicap

class Hole(models.Model):
    number = models.IntegerField()
    par = models.IntegerField()

    def __unicode__(self):
        return "Hole %s (Par %s)" % (self.number, self.par)


class Layout(models.Model):
    name = models.CharField(max_length=50)
    holes = models.ManyToManyField(Hole)

    @property
    def par(self):
        return sum([h.par for h in self.holes.all()])

    def __unicode__(self):
        return self.name

    @property
    def hole_count(self):
        return self.holes.count()


class Course(models.Model):
    name = models.CharField(max_length=50)
    layouts = models.ManyToManyField(Layout)

    def __unicode__(self):
        return self.name


class Score(models.Model):
    """
    Model for overall scratch score for a player on a card after their round
    """
    contestant = models.ForeignKey(Contestant)
    strokes = models.IntegerField()
    date = models.DateTimeField()

    def __unicode__(self):
        return "%s - %s - %s" % (self.total_strokes, self.date.ctime(), self.player)


class Card(models.Model):
    course = models.ForeignKey(Course)
    layout = models.ForeignKey(Layout)
    date = models.DateTimeField()
    scores = models.ManyToManyField(TotalScore, blank=True)

    @property
    def players(self):
        """
        Returns a list of Players who are competing on this card
        """
        return [c.player for c in self.contestants.all()]

    def __unicode__(self):
        return "%s (%s)" % (self.date, ", ".join([p.name for p in self.players]))

    def get_date(self):
        return self.date.strftime("%a %b %d %H:%M, %Y")

    @property
    def result(self):
        result = OrderedDict()
        for score in self.scores.all():
            contestant = score.contestant.player
            scratch_score = score.strokes
            scratch_delta = scratch_score - self.layout.par
            handicap = score.contestant.handicap
            handicap_score = scratch_score - handicap
            handicap_delta = handicap_score - self.layout.par
            result[contestant] = {}
            result[contestant]["handicap"] = handicap
            result[contestant]["scratch_score"] = scratch_score
            result[contestant]["scratch_delta"] = str(scratch_delta) if scratch_delta < 0 else "+%s" % scratch_delta
            result[contestant]["handicap_score"] = handicap_score
            result[contestant]["handicap_delta"] = handicap_delta if handicap_delta < 0 else "+%s" % handicap_delta
        # sort by rank
        result = OrderedDict(sorted(result.iteritems(), key=lambda x: x[1]["handicap_score"]))
        return result


class Award(models.Model):
    """
    Generic award model, eg. Closest To Pin
    """
    name = models.CharField(max_length=50, blank=True, null=True)
    contestant = models.ForeignKey(Contestant)

    def __unicode__(self):
        return "%s: %s" % (self.name, self.player.name)


class Event(models.Model):
    """
    Generic event model, eg. a league day
    """
    name = models.CharField(max_length=50, blank=True, null=True, help_text="Name of event, eg 'September League Day'")
    date = models.DateTimeField()
    rounds = models.IntegerField(help_text="Number of rounds that players are required to complete during this league event")
    awards = models.ManyToManyField(Award, blank=True)
    cards = models.ManyToManyField(Card, blank=True)

    @property
    def render_date(self):
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
        Returns points earned by players during this event
        """
        event_result = OrderedDict()
        # only use the first self.rounds cards
        for card in self.cards.order_by("date")[:self.rounds]:
            result = card.get_result()
            for contestant in result:
                stats = result[contestant]
                event_result[contestant] = defaultdict(int)
                event_result[contestant]['round_count'] += 1
                event_result[contestant]['handicap_score'] += stats['handicap_score']
                event_result[contestant]['awards'] = "<br />".join([a.name for a in self.awards.filter(contestant=contestant)])
        # sort by rank
        event_result = OrderedDict(sorted(event_result.iteritems(), key=lambda x: x[1]["handicap_score"]))
        # assign points earned
        for player in event_result:
            if self.rounds < event_result[player]['round_count']:
                # player completed less than the required rounds, assign minimum possible points. 
                event_result[player]['points_earned'] = self.get_points(-1)
            else:
                rank = event_result.keys().index(player)
                event_result[player]['points_earned'] = self.get_points(rank)
        return event_result

    def save(self, *args, **kwargs):
        super(Event, self).save(*args, **kwargs)
        # TODO recalculate curent handicaps from the first event using initial handicap for contestant.

    def __unicode__(self):
        name = self.name or "Event"
        return "%s - %s" % (name, self.date.ctime())


class League(models.Model):
    name = models.CharField(max_length=50)
    contentants = models.ManyToManyField(Contestant)
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
