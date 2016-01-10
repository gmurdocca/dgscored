from collections import OrderedDict, defaultdict
from dgscored import settings
from django.db import models
import math


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
    def name(self):
        return self.full_name

    @property
    def last_name_initial(self):
        return self.last_name[0]

    @property
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
        return self.full_name


class Contestant(models.Model):
    player = models.ForeignKey(Player)
    initial_handicap = models.IntegerField(default=0)

    def __unicode__(self):
        return "%s (%s)" % (self.player.full_name, self.league_set.get())


class Hole(models.Model):
    number = models.IntegerField()
    par = models.IntegerField(default=3)

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
        return "%s - %s - %s" % (self.strokes, self.date.ctime(), self.contestant.player.name)


class Card(models.Model):
    course = models.ForeignKey(Course)
    layout = models.ForeignKey(Layout)
    date = models.DateTimeField()
    scores = models.ManyToManyField(Score, blank=True)

    @property
    def players(self, render=True):
        """
        Returns a list of Players who are competing on this card
        Returns a string if render=True, else a list of Player objects.
        """
        result = [s.contestant.player.shortest_name for s in self.scores.all()]
        if render:
            return ", ".join(result)
        return result

    def __unicode__(self):
        return "%s (%s)" % (self.date, ", ".join([str(p) for p in self.players]))

    def render_date(self):
        return self.date.strftime("%a %b %d %H:%M, %Y")

    @property
    def result(self):
        result = OrderedDict()
        for score in self.scores.all():
            contestant = score.contestant
            scratch_score = score.strokes
            scratch_delta = scratch_score - self.layout.par
            result[contestant] = {}
            result[contestant]["scratch_score"] = scratch_score
            result[contestant]["scratch_delta"] = str(scratch_delta) if scratch_delta < 0 else "+%s" % scratch_delta
        # sort by rank
        result = OrderedDict(sorted(result.iteritems(), key=lambda x: x[1]["scratch_score"]))
        return result


class Award(models.Model):
    """
    Generic award model, eg. Closest to Pin
    """
    name = models.CharField(max_length=50, blank=True, null=True)
    contestant = models.ForeignKey(Contestant)

    def __unicode__(self):
        return "%s: %s" % (self.name, self.contestant.player.name)


class Event(models.Model):
    """
    Generic event model, eg. a league day
    """
    name = models.CharField(max_length=50, blank=True, null=True, help_text="Name of event, eg 'September League Day'")
    date = models.DateTimeField()
    rounds = models.IntegerField(help_text="Number of rounds that players are required to complete during this league event")
    awards = models.ManyToManyField(Award, blank=True)
    cards = models.ManyToManyField(Card, blank=True)

    def get_latest_cards(self, contestant, n=1):
        """
        returns up to n latest score cards for contestant, sorted 
        """
        result = []
        all_events = self.league_set.get().events.filter(date__lte=self.date)
        for event in all_events:
            cards = event.cards.all()
            for card in cards:
                if card.scores.filter(contestant=contestant):
                    # this card counts
                    result.append(card)
        result = sorted(result, key=lambda x: x.date, reverse=True)[:n]
        return result

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

    @property
    def result(self):
        """
        Returns points earned by contestants during this event
        """
        event_result = OrderedDict()
        # only use the first self.rounds cards
        for card in self.cards.order_by("date")[:self.rounds]:
            result = card.result
            for contestant in result:
                stats = result[contestant]
                event_result[contestant] = defaultdict(int)
                event_result[contestant]['awards'] = "<br />".join([a.name for a in self.awards.filter(contestant=contestant)])
                event_result[contestant]['round_count'] += 1
                event_result[contestant]['scratch_score'] += stats['scratch_score']
        for contestant in event_result:
            # calculate handicap score
            try:
                previous_event = self.get_previous_by_date()
            except self.DoesNotExist:
                previous_event = None
            if not previous_event:
                previous_handicap = contestant.initial_handicap
            else:
                try:
                    previous_handicap = previous_event.result[contestant]['handicap']
                except KeyError:
                    previous_handicap = contestant.initial_handicap
            event_result[contestant]['previous_handicap'] = int(previous_handicap)
            event_result[contestant]['handicap_score'] = int(event_result[contestant]['scratch_score'] - (previous_handicap * event_result[contestant]['round_count']))
            # calculate new handicap
            latest_five_cards = self.get_latest_cards(contestant, 5)
            # sort by scratch_delta
            best_two_cards = sorted(latest_five_cards, key=lambda x: x.result[contestant]['scratch_delta'])[:2]
            # calculate average:
            best_two_scratch_deltas = [int(c.result[contestant]["scratch_delta"]) for c in best_two_cards]
            handicap = reduce(lambda x, y: float(x) + float(y), best_two_scratch_deltas) / len(best_two_scratch_deltas)
            # round up
            handicap = math.ceil(handicap)
            event_result[contestant]['handicap'] = handicap
        # sort event_result by rank
        event_result = OrderedDict(sorted(event_result.iteritems(), key=lambda x: x[1]["handicap_score"]))
        # assign points earned
        for contestant in event_result:
            if self.rounds < event_result[contestant]['round_count']:
                # player completed less than the required rounds, assign minimum possible points. 
                event_result[contestant]['points_earned'] = self.get_points(-1)
            else:
                rank = event_result.keys().index(contestant)
                event_result[contestant]['points_earned'] = self.get_points(rank)
        return event_result

    def __unicode__(self):
        name = self.name or "Event"
        return "%s - %s" % (name, self.date.ctime())


class League(models.Model):
    name = models.CharField(max_length=50)
    contentants = models.ManyToManyField(Contestant, blank=True)
    events = models.ManyToManyField(Event, blank=True)

    def __unicode__(self):
        return "%s" % self.name

    @property
    def result(self):
        standings = OrderedDict()
        for event in self.events.all():
            result = event.result
            for contestant in result:
                player = contestant.player
                if not player in standings:
                    standings[player] = defaultdict(int)
                standings[player]['points'] += result[contestant]['points_earned']
                standings[player]['handicap'] = int(result[contestant]['handicap'])
        # sort by rank
        standings = OrderedDict(sorted(standings.iteritems(), key=lambda x: x[1]['points'], reverse=True))
        return standings

