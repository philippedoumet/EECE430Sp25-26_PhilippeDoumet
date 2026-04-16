from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User, Group
from django.views import View
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Sum, F, Q
from django.utils import timezone
from django.contrib import messages

from .models import (
    Player, Match, Training, Attendance, PlayerStatistic,
    Transfer, Expense, Season, Coach
)
from .forms import (
    PlayerForm, PlayerAccountForm, MatchForm, TrainingForm,
    TransferForm, ExpenseForm, SeasonForm
)


# ---------------------------------------------------------------------------
# Access-control mixins
# ---------------------------------------------------------------------------

class OwnerRequiredMixin(LoginRequiredMixin):
    login_url = '/login/'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not (request.user.is_superuser or request.user.groups.filter(name='Owner').exists()):
            messages.error(request, "Access denied.")
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)


class CoachRequiredMixin(LoginRequiredMixin):
    login_url = '/login/'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not (request.user.is_superuser or request.user.groups.filter(name='Coach').exists()):
            messages.error(request, "Access denied.")
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)


class PlayerRequiredMixin(LoginRequiredMixin):
    login_url = '/login/'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not (request.user.is_superuser or request.user.groups.filter(name='Player').exists()):
            messages.error(request, "Access denied.")
            return redirect('login')
        if not hasattr(request.user, 'player_profile'):
            messages.error(request, "No player profile found.")
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)


def _active_season():
    return Season.objects.filter(is_active=True).first()


# ---------------------------------------------------------------------------
# OWNER PORTAL
# ---------------------------------------------------------------------------

class OwnerDashboardView(OwnerRequiredMixin, TemplateView):
    template_name = 'players/owner/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        season = _active_season()
        ctx['season'] = season
        ctx['all_seasons'] = Season.objects.all()
        ctx['player_count'] = Player.objects.filter(is_active=True).count()
        ctx['total_salary'] = Player.objects.filter(is_active=True).aggregate(
            s=Sum('salary'))['s'] or 0

        if season:
            played = Match.objects.filter(season=season, sets_won__isnull=False)
            ctx['wins'] = played.filter(sets_won__gt=F('sets_lost')).count()
            ctx['losses'] = played.filter(sets_won__lt=F('sets_lost')).count()
            ctx['draws'] = played.filter(sets_won=F('sets_lost')).count()
            ctx['total_expenses'] = Expense.objects.filter(season=season).aggregate(
                s=Sum('amount'))['s'] or 0
            ctx['expense_by_category'] = (
                Expense.objects.filter(season=season)
                .values('category')
                .annotate(total=Sum('amount'))
                .order_by('-total')
            )
            ctx['recent_transfers'] = Transfer.objects.filter(season=season).order_by('-date')[:5]
            ctx['upcoming_matches'] = Match.objects.filter(
                season=season, date__gt=timezone.now()).order_by('date')[:5]
            ctx['coaches'] = Coach.objects.select_related('user').all()
        return ctx


class SeasonListView(OwnerRequiredMixin, ListView):
    model = Season
    template_name = 'players/owner/season_list.html'
    context_object_name = 'seasons'


class SeasonCreateView(OwnerRequiredMixin, CreateView):
    model = Season
    form_class = SeasonForm
    template_name = 'players/owner/season_form.html'
    success_url = reverse_lazy('season_list')


class SeasonUpdateView(OwnerRequiredMixin, UpdateView):
    model = Season
    form_class = SeasonForm
    template_name = 'players/owner/season_form.html'
    success_url = reverse_lazy('season_list')


class SeasonDeleteView(OwnerRequiredMixin, DeleteView):
    model = Season
    template_name = 'players/owner/season_confirm_delete.html'
    success_url = reverse_lazy('season_list')


class ExpenseListView(OwnerRequiredMixin, View):
    template_name = 'players/owner/expense_list.html'

    def get(self, request):
        season = _active_season()
        season_id = request.GET.get('season')
        if season_id:
            season = get_object_or_404(Season, pk=season_id)
        expenses = Expense.objects.filter(season=season) if season else Expense.objects.all()
        return render(request, self.template_name, {
            'expenses': expenses,
            'season': season,
            'all_seasons': Season.objects.all(),
            'total': expenses.aggregate(s=Sum('amount'))['s'] or 0,
            'form': ExpenseForm(initial={'season': season}),
        })

    def post(self, request):
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Expense added.")
        return redirect('expense_list')


class ExpenseDeleteView(OwnerRequiredMixin, DeleteView):
    model = Expense
    template_name = 'players/owner/expense_confirm_delete.html'
    success_url = reverse_lazy('expense_list')


class TransferListView(OwnerRequiredMixin, View):
    template_name = 'players/owner/transfer_list.html'

    def get(self, request):
        season = _active_season()
        season_id = request.GET.get('season')
        if season_id:
            season = get_object_or_404(Season, pk=season_id)
        transfers = Transfer.objects.filter(season=season) if season else Transfer.objects.all()
        return render(request, self.template_name, {
            'transfers': transfers.select_related('player', 'season'),
            'season': season,
            'all_seasons': Season.objects.all(),
            'form': TransferForm(initial={'season': season}),
        })

    def post(self, request):
        form = TransferForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Transfer recorded.")
        return redirect('transfer_list')


class OwnerRosterView(OwnerRequiredMixin, TemplateView):
    template_name = 'players/owner/roster.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        players = Player.objects.filter(is_active=True)
        ctx['players'] = players
        ctx['total_salary'] = players.aggregate(s=Sum('salary'))['s'] or 0
        ctx['season'] = _active_season()
        return ctx


class TeamPerformanceView(OwnerRequiredMixin, TemplateView):
    template_name = 'players/owner/team_performance.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        season = _active_season()
        season_id = self.request.GET.get('season')
        if season_id:
            season = get_object_or_404(Season, pk=season_id)
        ctx['season'] = season
        ctx['all_seasons'] = Season.objects.all()
        if season:
            matches = Match.objects.filter(season=season)
            played = matches.filter(sets_won__isnull=False)
            ctx['matches'] = matches
            ctx['played'] = played.count()
            ctx['wins'] = played.filter(sets_won__gt=F('sets_lost')).count()
            ctx['losses'] = played.filter(sets_won__lt=F('sets_lost')).count()
            ctx['draws'] = played.filter(sets_won=F('sets_lost')).count()
            # Top performers
            ctx['top_scorers'] = (
                PlayerStatistic.objects.filter(match__season=season)
                .values('player__name')
                .annotate(total_points=Sum('points'), total_kills=Sum('kills'))
                .order_by('-total_points')[:5]
            )
        return ctx


# ---------------------------------------------------------------------------
# COACH PORTAL
# ---------------------------------------------------------------------------

class CoachDashboardView(CoachRequiredMixin, TemplateView):
    template_name = 'players/coach/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        season = _active_season()
        ctx['season'] = season
        ctx['player_count'] = Player.objects.filter(is_active=True).count()
        if season:
            matches = Match.objects.filter(season=season)
            played = matches.filter(sets_won__isnull=False)
            ctx['wins'] = played.filter(sets_won__gt=F('sets_lost')).count()
            ctx['losses'] = played.filter(sets_won__lt=F('sets_lost')).count()
            ctx['upcoming_matches'] = matches.filter(
                date__gt=timezone.now()).order_by('date')[:3]
            ctx['recent_results'] = played.order_by('-date')[:4]
            ctx['upcoming_trainings'] = Training.objects.filter(
                season=season, date__gt=timezone.now()).order_by('date')[:3]
        return ctx


# --- Coach: Players ---

class CoachPlayerListView(CoachRequiredMixin, ListView):
    model = Player
    template_name = 'players/coach/player_list.html'
    context_object_name = 'players'

    def get_queryset(self):
        qs = Player.objects.all()
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(position__icontains=q))
        active = self.request.GET.get('active', '1')
        if active == '1':
            qs = qs.filter(is_active=True)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['season'] = _active_season()
        return ctx


class CoachPlayerCreateView(CoachRequiredMixin, CreateView):
    model = Player
    form_class = PlayerForm
    template_name = 'players/coach/player_form.html'
    success_url = reverse_lazy('coach_player_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Add Player'
        return ctx


class CoachPlayerUpdateView(CoachRequiredMixin, UpdateView):
    model = Player
    form_class = PlayerForm
    template_name = 'players/coach/player_form.html'
    success_url = reverse_lazy('coach_player_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = f'Edit — {self.object.name}'
        return ctx


class CoachPlayerDeleteView(CoachRequiredMixin, DeleteView):
    model = Player
    template_name = 'players/coach/player_confirm_delete.html'
    success_url = reverse_lazy('coach_player_list')


class CoachPlayerDetailView(CoachRequiredMixin, TemplateView):
    template_name = 'players/coach/player_detail.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        player = get_object_or_404(Player, pk=kwargs['pk'])
        season = _active_season()
        ctx['player'] = player
        ctx['season'] = season
        ctx['has_account'] = player.user is not None
        if season:
            ctx['stats'] = player.season_stats(season)
            ctx['attendance_rate'] = player.attendance_rate(season)
            ctx['recent_stats'] = player.statistics.filter(
                match__season=season).select_related('match').order_by('-match__date')[:5]
            ctx['transfers'] = player.transfers.filter(season=season)
        return ctx


class CoachCreatePlayerAccountView(CoachRequiredMixin, View):
    template_name = 'players/coach/player_account_form.html'

    def get(self, request, pk):
        player = get_object_or_404(Player, pk=pk)
        if player.user:
            messages.info(request, f"{player.name} already has an account.")
            return redirect('coach_player_detail', pk=pk)
        return render(request, self.template_name, {'player': player, 'form': PlayerAccountForm()})

    def post(self, request, pk):
        player = get_object_or_404(Player, pk=pk)
        form = PlayerAccountForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data.get('first_name', ''),
                last_name=form.cleaned_data.get('last_name', ''),
            )
            group, _ = Group.objects.get_or_create(name='Player')
            user.groups.add(group)
            player.user = user
            player.save()
            messages.success(request, f"Account created for {player.name}.")
            return redirect('coach_player_detail', pk=pk)
        return render(request, self.template_name, {'player': player, 'form': form})


# --- Coach: Matches ---

class MatchListView(CoachRequiredMixin, View):
    template_name = 'players/coach/match_list.html'

    def get(self, request):
        season = _active_season()
        season_id = request.GET.get('season')
        if season_id:
            season = get_object_or_404(Season, pk=season_id)
        matches = Match.objects.filter(season=season) if season else Match.objects.none()
        return render(request, self.template_name, {
            'matches': matches,
            'season': season,
            'all_seasons': Season.objects.all(),
        })


class MatchCreateView(CoachRequiredMixin, CreateView):
    model = Match
    form_class = MatchForm
    template_name = 'players/coach/match_form.html'
    success_url = reverse_lazy('match_list')

    def get_initial(self):
        return {'season': _active_season()}

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Schedule Match'
        return ctx


class MatchUpdateView(CoachRequiredMixin, UpdateView):
    model = Match
    form_class = MatchForm
    template_name = 'players/coach/match_form.html'
    success_url = reverse_lazy('match_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = f'Edit Match — vs {self.object.opponent}'
        return ctx


class MatchDeleteView(CoachRequiredMixin, DeleteView):
    model = Match
    template_name = 'players/coach/match_confirm_delete.html'
    success_url = reverse_lazy('match_list')


class MatchDetailView(CoachRequiredMixin, TemplateView):
    template_name = 'players/coach/match_detail.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        match = get_object_or_404(Match, pk=kwargs['pk'])
        ctx['match'] = match
        ctx['attendances'] = match.attendances.select_related('player').all()
        ctx['statistics'] = match.statistics.select_related('player').all()
        ctx['players_without_attendance'] = Player.objects.filter(
            is_active=True
        ).exclude(attendances__match=match)
        return ctx


class MatchAttendanceView(CoachRequiredMixin, View):
    template_name = 'players/coach/match_attendance.html'

    def get(self, request, pk):
        match = get_object_or_404(Match, pk=pk)
        players = Player.objects.filter(is_active=True)
        attendance_map = {
            a.player_id: a for a in Attendance.objects.filter(match=match)
        }
        rows = [{'player': p, 'attendance': attendance_map.get(p.pk)} for p in players]
        return render(request, self.template_name, {'match': match, 'rows': rows})

    def post(self, request, pk):
        match = get_object_or_404(Match, pk=pk)
        players = Player.objects.filter(is_active=True)
        for player in players:
            status = request.POST.get(f'status_{player.pk}')
            reason = request.POST.get(f'reason_{player.pk}', '')
            if status:
                Attendance.objects.update_or_create(
                    player=player, match=match,
                    defaults={'status': status, 'reason': reason, 'training': None}
                )
        messages.success(request, "Attendance saved.")
        return redirect('match_detail', pk=pk)


class MatchStatsView(CoachRequiredMixin, View):
    template_name = 'players/coach/match_stats.html'

    def get(self, request, pk):
        match = get_object_or_404(Match, pk=pk)
        players = Player.objects.filter(is_active=True)
        stats_map = {s.player_id: s for s in PlayerStatistic.objects.filter(match=match)}
        rows = [{'player': p, 'stat': stats_map.get(p.pk)} for p in players]
        return render(request, self.template_name, {'match': match, 'rows': rows})

    def post(self, request, pk):
        match = get_object_or_404(Match, pk=pk)
        players = Player.objects.filter(is_active=True)
        for player in players:
            if request.POST.get(f'include_{player.pk}'):
                PlayerStatistic.objects.update_or_create(
                    player=player, match=match,
                    defaults={
                        'points': int(request.POST.get(f'points_{player.pk}', 0)),
                        'kills': int(request.POST.get(f'kills_{player.pk}', 0)),
                        'aces': int(request.POST.get(f'aces_{player.pk}', 0)),
                        'blocks': int(request.POST.get(f'blocks_{player.pk}', 0)),
                        'digs': int(request.POST.get(f'digs_{player.pk}', 0)),
                        'errors': int(request.POST.get(f'errors_{player.pk}', 0)),
                        'minutes_played': int(request.POST.get(f'minutes_{player.pk}', 0)),
                    }
                )
        messages.success(request, "Statistics saved.")
        return redirect('match_detail', pk=pk)


# --- Coach: Trainings ---

class TrainingListView(CoachRequiredMixin, View):
    template_name = 'players/coach/training_list.html'

    def get(self, request):
        season = _active_season()
        season_id = request.GET.get('season')
        if season_id:
            season = get_object_or_404(Season, pk=season_id)
        trainings = Training.objects.filter(season=season) if season else Training.objects.none()
        return render(request, self.template_name, {
            'trainings': trainings,
            'season': season,
            'all_seasons': Season.objects.all(),
        })


class TrainingCreateView(CoachRequiredMixin, CreateView):
    model = Training
    form_class = TrainingForm
    template_name = 'players/coach/training_form.html'
    success_url = reverse_lazy('training_list')

    def get_initial(self):
        return {'season': _active_season()}

    def form_valid(self, form):
        coach = getattr(self.request.user, 'coach_profile', None)
        form.instance.created_by = coach
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Schedule Training'
        return ctx


class TrainingUpdateView(CoachRequiredMixin, UpdateView):
    model = Training
    form_class = TrainingForm
    template_name = 'players/coach/training_form.html'
    success_url = reverse_lazy('training_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = f'Edit Training — {self.object.date.strftime("%Y-%m-%d")}'
        return ctx


class TrainingDeleteView(CoachRequiredMixin, DeleteView):
    model = Training
    template_name = 'players/coach/training_confirm_delete.html'
    success_url = reverse_lazy('training_list')


class TrainingAttendanceView(CoachRequiredMixin, View):
    template_name = 'players/coach/training_attendance.html'

    def get(self, request, pk):
        training = get_object_or_404(Training, pk=pk)
        players = Player.objects.filter(is_active=True)
        attendance_map = {
            a.player_id: a for a in Attendance.objects.filter(training=training)
        }
        rows = [{'player': p, 'attendance': attendance_map.get(p.pk)} for p in players]
        return render(request, self.template_name, {'training': training, 'rows': rows})

    def post(self, request, pk):
        training = get_object_or_404(Training, pk=pk)
        players = Player.objects.filter(is_active=True)
        for player in players:
            status = request.POST.get(f'status_{player.pk}')
            reason = request.POST.get(f'reason_{player.pk}', '')
            if status:
                Attendance.objects.update_or_create(
                    player=player, training=training,
                    defaults={'status': status, 'reason': reason, 'match': None}
                )
        messages.success(request, "Attendance saved.")
        return redirect('training_list')


# --- Coach: Season Stats ---

class CoachSeasonStatsView(CoachRequiredMixin, TemplateView):
    template_name = 'players/coach/season_stats.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        season = _active_season()
        ctx['season'] = season
        ctx['all_seasons'] = Season.objects.all()
        if season:
            players = Player.objects.filter(is_active=True)
            player_data = []
            for p in players:
                stats = p.season_stats(season)
                player_data.append({
                    'player': p,
                    'points': stats['total_points'] or 0,
                    'kills': stats['total_kills'] or 0,
                    'aces': stats['total_aces'] or 0,
                    'blocks': stats['total_blocks'] or 0,
                    'digs': stats['total_digs'] or 0,
                    'attendance': p.attendance_rate(season),
                })
            player_data.sort(key=lambda x: x['points'], reverse=True)
            ctx['player_data'] = player_data
        return ctx


# ---------------------------------------------------------------------------
# PLAYER PORTAL
# ---------------------------------------------------------------------------

class PlayerDashboardView(PlayerRequiredMixin, TemplateView):
    template_name = 'players/player_portal/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        player = self.request.user.player_profile
        season = _active_season()
        ctx['player'] = player
        ctx['season'] = season
        if season:
            ctx['next_match'] = Match.objects.filter(
                season=season, date__gt=timezone.now()).order_by('date').first()
            ctx['next_training'] = Training.objects.filter(
                season=season, date__gt=timezone.now()).order_by('date').first()
            ctx['attendance_rate'] = player.attendance_rate(season)
            ctx['stats'] = player.season_stats(season)
            ctx['recent_results'] = Match.objects.filter(
                season=season, sets_won__isnull=False).order_by('-date')[:4]
        return ctx


class PlayerCalendarView(PlayerRequiredMixin, TemplateView):
    template_name = 'players/player_portal/calendar.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        player = self.request.user.player_profile
        season = _active_season()
        ctx['season'] = season
        if season:
            now = timezone.now()
            upcoming_matches = Match.objects.filter(season=season, date__gte=now).order_by('date')
            upcoming_trainings = Training.objects.filter(season=season, date__gte=now).order_by('date')
            # Merge and annotate with player's attendance
            match_att = {
                a.match_id: a for a in
                Attendance.objects.filter(player=player, match__season=season)
            }
            training_att = {
                a.training_id: a for a in
                Attendance.objects.filter(player=player, training__season=season)
            }
            ctx['upcoming_matches'] = [
                {'event': m, 'attendance': match_att.get(m.pk), 'type': 'match'}
                for m in upcoming_matches
            ]
            ctx['upcoming_trainings'] = [
                {'event': t, 'attendance': training_att.get(t.pk), 'type': 'training'}
                for t in upcoming_trainings
            ]
        return ctx


class PlayerMarkAttendanceView(PlayerRequiredMixin, View):
    def post(self, request):
        player = request.user.player_profile
        status = request.POST.get('status')
        reason = request.POST.get('reason', '')
        match_id = request.POST.get('match_id')
        training_id = request.POST.get('training_id')

        if match_id:
            match = get_object_or_404(Match, pk=match_id)
            Attendance.objects.update_or_create(
                player=player, match=match,
                defaults={'status': status, 'reason': reason, 'training': None}
            )
            messages.success(request, f"Marked as {status} for match vs {match.opponent}.")
        elif training_id:
            training = get_object_or_404(Training, pk=training_id)
            Attendance.objects.update_or_create(
                player=player, training=training,
                defaults={'status': status, 'reason': reason, 'match': None}
            )
            messages.success(request, f"Marked as {status} for training on {training.date.strftime('%Y-%m-%d')}.")

        return redirect('player_calendar')


class PlayerMyStatsView(PlayerRequiredMixin, TemplateView):
    template_name = 'players/player_portal/stats.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        player = self.request.user.player_profile
        season = _active_season()
        ctx['player'] = player
        ctx['season'] = season
        if season:
            ctx['stats'] = player.season_stats(season)
            ctx['match_stats'] = player.statistics.filter(
                match__season=season).select_related('match').order_by('-match__date')
            ctx['attendance_rate'] = player.attendance_rate(season)
        return ctx


class PlayerMyAttendanceView(PlayerRequiredMixin, TemplateView):
    template_name = 'players/player_portal/attendance.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        player = self.request.user.player_profile
        season = _active_season()
        ctx['player'] = player
        ctx['season'] = season
        if season:
            ctx['match_attendances'] = Attendance.objects.filter(
                player=player, match__season=season
            ).select_related('match').order_by('-match__date')
            ctx['training_attendances'] = Attendance.objects.filter(
                player=player, training__season=season
            ).select_related('training').order_by('-training__date')
            ctx['attendance_rate'] = player.attendance_rate(season)
        return ctx
