from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Sum, Q


class Season(models.Model):
    name = models.CharField(max_length=20)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_active:
            Season.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)


class ClubOwner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='owner_profile')
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"Owner: {self.user.get_full_name() or self.user.username}"


class Coach(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='coach_profile')
    phone = models.CharField(max_length=20, blank=True)
    specialty = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Coach: {self.user.get_full_name() or self.user.username}"


class Player(models.Model):
    POSITIONS = [
        ('Setter', 'Setter'),
        ('Outside Hitter', 'Outside Hitter'),
        ('Opposite Hitter', 'Opposite Hitter'),
        ('Middle Blocker', 'Middle Blocker'),
        ('Libero', 'Libero'),
        ('Defensive Specialist', 'Defensive Specialist'),
    ]
    user = models.OneToOneField(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='player_profile'
    )
    name = models.CharField(max_length=100)
    date_joined = models.DateField()
    position = models.CharField(max_length=50, choices=POSITIONS)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    contact_person = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    jersey_number = models.PositiveIntegerField(null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    nationality = models.CharField(max_length=50, blank=True)
    height_cm = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def age(self):
        from datetime import date
        if self.birth_date:
            today = date.today()
            return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
            )
        return None

    def season_stats(self, season):
        return self.statistics.filter(match__season=season).aggregate(
            total_points=Sum('points'),
            total_kills=Sum('kills'),
            total_aces=Sum('aces'),
            total_blocks=Sum('blocks'),
            total_digs=Sum('digs'),
        )

    def attendance_rate(self, season=None):
        qs = self.attendances.all()
        if season:
            qs = qs.filter(Q(match__season=season) | Q(training__season=season))
        total = qs.count()
        if total == 0:
            return 0
        present = qs.filter(status__in=['present', 'late']).count()
        return round((present / total) * 100)


class Match(models.Model):
    MATCH_TYPES = [
        ('league', 'League'),
        ('cup', 'Cup'),
        ('friendly', 'Friendly'),
        ('playoff', 'Playoff'),
    ]
    VENUES = [('home', 'Home'), ('away', 'Away')]

    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='matches')
    date = models.DateTimeField()
    opponent = models.CharField(max_length=100)
    venue = models.CharField(max_length=5, choices=VENUES, default='home')
    match_type = models.CharField(max_length=10, choices=MATCH_TYPES, default='league')
    sets_won = models.PositiveIntegerField(null=True, blank=True)
    sets_lost = models.PositiveIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"vs {self.opponent} ({self.date.strftime('%Y-%m-%d')})"

    @property
    def result(self):
        if self.sets_won is None:
            return 'Upcoming'
        if self.sets_won > self.sets_lost:
            return 'Win'
        if self.sets_won < self.sets_lost:
            return 'Loss'
        return 'Draw'

    @property
    def result_badge(self):
        r = self.result
        return {'Win': 'success', 'Loss': 'danger', 'Draw': 'warning', 'Upcoming': 'secondary'}.get(r, 'secondary')

    @property
    def score(self):
        if self.sets_won is None:
            return 'TBD'
        return f"{self.sets_won}–{self.sets_lost}"

    @property
    def is_upcoming(self):
        return self.date > timezone.now()


class Training(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='trainings')
    date = models.DateTimeField()
    location = models.CharField(max_length=100, default='Main Court')
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        Coach, on_delete=models.SET_NULL, null=True, blank=True, related_name='trainings_created'
    )

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Training — {self.date.strftime('%Y-%m-%d %H:%M')}"

    @property
    def is_upcoming(self):
        return self.date > timezone.now()


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('excused', 'Excused'),
        ('late', 'Late'),
    ]
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='attendances')
    match = models.ForeignKey(
        Match, on_delete=models.CASCADE, null=True, blank=True, related_name='attendances'
    )
    training = models.ForeignKey(
        Training, on_delete=models.CASCADE, null=True, blank=True, related_name='attendances'
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present')
    reason = models.CharField(max_length=200, blank=True)

    def __str__(self):
        event = self.match or self.training
        return f"{self.player.name} — {event} — {self.get_status_display()}"

    @property
    def badge_color(self):
        return {
            'present': 'success', 'late': 'warning',
            'absent': 'danger', 'excused': 'info'
        }.get(self.status, 'secondary')


class PlayerStatistic(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='statistics')
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='statistics')
    points = models.PositiveIntegerField(default=0)
    kills = models.PositiveIntegerField(default=0)
    aces = models.PositiveIntegerField(default=0)
    blocks = models.PositiveIntegerField(default=0)
    digs = models.PositiveIntegerField(default=0)
    errors = models.PositiveIntegerField(default=0)
    minutes_played = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)

    class Meta:
        unique_together = ('player', 'match')

    def __str__(self):
        return f"{self.player.name} vs {self.match.opponent}"


class Transfer(models.Model):
    TYPES = [
        ('in', 'Transfer In'),
        ('out', 'Transfer Out'),
        ('loan_in', 'Loan In'),
        ('loan_out', 'Loan Out'),
    ]
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='transfers')
    transfer_type = models.CharField(max_length=10, choices=TYPES)
    from_club = models.CharField(max_length=100, blank=True)
    to_club = models.CharField(max_length=100, blank=True)
    fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    date = models.DateField()
    season = models.ForeignKey(
        Season, on_delete=models.SET_NULL, null=True, blank=True, related_name='transfers'
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.get_transfer_type_display()} — {self.player.name}"


class Expense(models.Model):
    CATEGORIES = [
        ('salary', 'Player Salary'),
        ('transfer', 'Transfer Fee'),
        ('equipment', 'Equipment'),
        ('travel', 'Travel'),
        ('facility', 'Facility'),
        ('medical', 'Medical'),
        ('coaching', 'Coaching Staff'),
        ('other', 'Other'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORIES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    description = models.CharField(max_length=200)
    season = models.ForeignKey(
        Season, on_delete=models.SET_NULL, null=True, blank=True, related_name='expenses'
    )

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.get_category_display()} — ${self.amount}"
