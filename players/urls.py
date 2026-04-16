from django.urls import path
from . import views

urlpatterns = [
    # --- Owner portal ---
    path('owner/', views.OwnerDashboardView.as_view(), name='owner_dashboard'),
    path('owner/roster/', views.OwnerRosterView.as_view(), name='owner_roster'),
    path('owner/performance/', views.TeamPerformanceView.as_view(), name='team_performance'),
    path('owner/seasons/', views.SeasonListView.as_view(), name='season_list'),
    path('owner/seasons/new/', views.SeasonCreateView.as_view(), name='season_create'),
    path('owner/seasons/<int:pk>/edit/', views.SeasonUpdateView.as_view(), name='season_update'),
    path('owner/seasons/<int:pk>/delete/', views.SeasonDeleteView.as_view(), name='season_delete'),
    path('owner/expenses/', views.ExpenseListView.as_view(), name='expense_list'),
    path('owner/expenses/<int:pk>/delete/', views.ExpenseDeleteView.as_view(), name='expense_delete'),
    path('owner/transfers/', views.TransferListView.as_view(), name='transfer_list'),

    # --- Coach portal ---
    path('coach/', views.CoachDashboardView.as_view(), name='coach_dashboard'),
    path('coach/players/', views.CoachPlayerListView.as_view(), name='coach_player_list'),
    path('coach/players/new/', views.CoachPlayerCreateView.as_view(), name='coach_player_create'),
    path('coach/players/<int:pk>/', views.CoachPlayerDetailView.as_view(), name='coach_player_detail'),
    path('coach/players/<int:pk>/edit/', views.CoachPlayerUpdateView.as_view(), name='coach_player_update'),
    path('coach/players/<int:pk>/delete/', views.CoachPlayerDeleteView.as_view(), name='coach_player_delete'),
    path('coach/players/<int:pk>/account/', views.CoachCreatePlayerAccountView.as_view(), name='coach_player_account'),
    path('coach/matches/', views.MatchListView.as_view(), name='match_list'),
    path('coach/matches/new/', views.MatchCreateView.as_view(), name='match_create'),
    path('coach/matches/<int:pk>/edit/', views.MatchUpdateView.as_view(), name='match_update'),
    path('coach/matches/<int:pk>/delete/', views.MatchDeleteView.as_view(), name='match_delete'),
    path('coach/matches/<int:pk>/', views.MatchDetailView.as_view(), name='match_detail'),
    path('coach/matches/<int:pk>/attendance/', views.MatchAttendanceView.as_view(), name='match_attendance'),
    path('coach/matches/<int:pk>/stats/', views.MatchStatsView.as_view(), name='match_stats'),
    path('coach/trainings/', views.TrainingListView.as_view(), name='training_list'),
    path('coach/trainings/new/', views.TrainingCreateView.as_view(), name='training_create'),
    path('coach/trainings/<int:pk>/edit/', views.TrainingUpdateView.as_view(), name='training_update'),
    path('coach/trainings/<int:pk>/delete/', views.TrainingDeleteView.as_view(), name='training_delete'),
    path('coach/trainings/<int:pk>/attendance/', views.TrainingAttendanceView.as_view(), name='training_attendance'),
    path('coach/stats/', views.CoachSeasonStatsView.as_view(), name='coach_season_stats'),

    # --- Player portal ---
    path('player/', views.PlayerDashboardView.as_view(), name='player_dashboard'),
    path('player/calendar/', views.PlayerCalendarView.as_view(), name='player_calendar'),
    path('player/attendance/', views.PlayerMyAttendanceView.as_view(), name='player_attendance'),
    path('player/attendance/mark/', views.PlayerMarkAttendanceView.as_view(), name='player_mark_attendance'),
    path('player/stats/', views.PlayerMyStatsView.as_view(), name='player_stats'),
]
