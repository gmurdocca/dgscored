from collections import OrderedDict, defaultdict
from django.utils import timezone
from dgscored import settings
from django.db import models
import pytz

timezone.activate(pytz.timezone(settings.TIME_ZONE))
current_tz = timezone.get_current_timezone()

def normalise(date):
    return current_tz.normalize(date)

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
            same_last_name_initial = defaultdict(int)
            for player in same_first_names:
                same_last_name_initial[player.last_name_initial] += 1
            if same_last_name_initial[self.last_name_initial] == 1:
                return "%s %s" % (self.first_name, self.last_name_initial)
        return self.full_name

    def __unicode__(self):
        return self.full_name


class Contestant(models.Model):
    player = models.ForeignKey(Player)
    initial_handicap = models.IntegerField(blank=True, null=True, default=None)

    def __unicode__(self):
        return "%s (%s)" % (self.player.full_name, self.league_set.all() and self.league_set.get() or "None")


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
        return "%s - %s - %s" % (self.strokes, normalise(self.date).ctime(), self.contestant.player.name)


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
        return "%s (%s)" % (normalise(self.date), self.players)

    def render_date(self):
        return normalise(self.date).strftime("%a %b %d %H:%M, %Y")

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
        return normalise(self.date).strftime("%a %b %d, %Y")

    def get_points(self, rank):
        """
        reutrns points earned for a player ranked at specified rank (zero indexed).
        if rank < 0 (eg. -1), minimum points attanable is returned (eg. if player
        did not complete Event.rounds rounds, then they earned minimum points for
        attendance, eg one point.
        """
        if 0 > rank or rank >= len(settings.LEAGUE_POINTS):
            return settings.LEAGUE_POINTS[-1]
        return settings.LEAGUE_POINTS[rank]

    @staticmethod
    def get_previous_handicap(event, contestant):
        try:
            previous_event = event.get_previous_by_date()
        except event.DoesNotExist:
            return contestant.initial_handicap
        try:
            return previous_event.result[contestant]['handicap']
        except KeyError:
            # contestant did not compete in previous event, check the next previous
            return Event.get_previous_handicap(previous_event, contestant)

    @property
    def result(self):
        """
        Returns a per-player results dict including points earned by contestants during this event, ordered by rank.
        """
        event_result = {}
        for card in self.cards.order_by("date"):
            result = card.result
            for contestant in result:
                stats = result[contestant]
                if not contestant in event_result:
                    event_result[contestant] = defaultdict(int)
                event_result[contestant]['awards'] = "<br />".join([a.name for a in self.awards.filter(contestant=contestant)])
                event_result[contestant]['round_count'] += 1
                event_result[contestant]['completed_event'] = event_result[contestant]['round_count'] >= settings.HANDICAP_MIN_ROUNDS
                # only count a scratch score if the contestant has not exceeded the max number of rounds required in this event.
                if event_result[contestant]['round_count'] <= self.rounds:
                    event_result[contestant]['scratch_score'] += stats['scratch_score']
        for contestant in event_result:
            # calculate handicap score
            previous_handicap = Event.get_previous_handicap(self, contestant)
            event_result[contestant]['previous_handicap'] = None if previous_handicap == None else int(previous_handicap)
            if previous_handicap == None:
                event_result[contestant]['handicap_score'] = None
            else:
                event_result[contestant]['handicap_score'] = int(event_result[contestant]['scratch_score'] - (previous_handicap * event_result[contestant]['round_count']))
            # calculate new handicap
            latest_max_cards = self.get_latest_cards(contestant, settings.HANDICAP_MAX_ROUNDS)
            # sort by scratch_delta
            best_min_cards = sorted(latest_max_cards, key=lambda x: x.result[contestant]['scratch_delta'])[:settings.HANDICAP_MIN_ROUNDS]
            # calculate average:
            best_scratch_deltas = [int(c.result[contestant]["scratch_delta"]) for c in best_min_cards]
            handicap = reduce(lambda x, y: float(x) + float(y), best_scratch_deltas) / len(best_scratch_deltas)
            # round to nearest integer
            handicap = int(round(handicap * settings.HANDICAP_MULTIPLIER))
            event_result[contestant]['handicap'] = handicap
            # inject the handicap into the contestant's initial handicap value if they played the required number of rounds
            total_rounds = sum([sum([c.scores.filter(contestant=contestant).count() for c in e.cards.all()]) for e in self.league_set.last().events.all()])
            if total_rounds == settings.HANDICAP_MIN_ROUNDS:
                contestant.initial_handicap = handicap
                contestant.save()
        # sort event_result by players who completed all required rounds, then by handicap score, then by scratch score
        result = {}
        incomplete_result = {}
        no_hc_result = {}
        for contestant in event_result:
            if event_result[contestant]["handicap_score"] == None:
                no_hc_result[contestant] = event_result[contestant]
            elif not event_result[contestant]['completed_event']:
                incomplete_result[contestant] = event_result[contestant]
            else:
                result[contestant] = event_result[contestant]
        result = OrderedDict(sorted(result.iteritems(), key=lambda x: x[1]["handicap_score"]))
        incomplete_result = OrderedDict(sorted(incomplete_result.iteritems(), key=lambda x: x[1]["handicap_score"]))
        no_hc_result = OrderedDict(sorted(no_hc_result.iteritems(), key=lambda x: x[1]["scratch_score"]))
        incomplete_result.update(no_hc_result)
        result.update(incomplete_result)
        event_result = result
        # assign points earned
        for contestant in event_result:
            if event_result[contestant]['handicap_score'] == None:
                event_result[contestant]['points_earned'] = None
            elif event_result[contestant]['round_count'] < self.rounds:
                # player completed less than the required rounds, assign minimum possible points. 
                event_result[contestant]['points_earned'] = self.get_points(-1)
            else:
                rank = event_result.keys().index(contestant)
                event_result[contestant]['points_earned'] = self.get_points(rank)
        return event_result

    def __unicode__(self):
        name = self.name or "Event"
        return "%s - %s" % (name, normalise(self.date).ctime())


class League(models.Model):
    name = models.CharField(max_length=50)
    contentants = models.ManyToManyField(Contestant, blank=True)
    events = models.ManyToManyField(Event, blank=True)
    min_rounds = settings.HANDICAP_MIN_ROUNDS

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
                standings[player]['initial_handicap'] = contestant.initial_handicap
                standings[player]['points'] += result[contestant]['points_earned'] or 0
                standings[player]['handicap'] = int(result[contestant]['handicap'])
                standings[player]['events_attended'] += 1 
                standings[player]['rounds_played'] += sum([c.scores.filter(contestant=contestant).count() for c in event.cards.all()])
        # flag playeres who have not completed enough rounds to be ranked
        for player in standings:
            if standings[player]['initial_handicap'] == None and standings[player]['rounds_played'] < settings.HANDICAP_MIN_ROUNDS:
                standings[player]['valid_hc'] = False
            else:
                standings[player]['valid_hc'] = True
        # sort by rank
        standings = OrderedDict(sorted(standings.iteritems(), key=lambda x: x[1]['points'], reverse=True))
        return standings

