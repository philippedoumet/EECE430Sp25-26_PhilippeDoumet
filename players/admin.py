from django.contrib import admin
from .models import (
    Season, ClubOwner, Coach, Player, Match, Training,
    Attendance, PlayerStatistic, Transfer, Expense
)

@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'is_active']
    list_editable = ['is_active']

@admin.register(ClubOwner)
class ClubOwnerAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone']

@admin.register(Coach)
class CoachAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'specialty']

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'jersey_number', 'salary', 'is_active', 'user']
    list_filter = ['position', 'is_active']
    search_fields = ['name']

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['opponent', 'date', 'venue', 'match_type', 'season', 'score', 'result']
    list_filter = ['season', 'match_type', 'venue']

@admin.register(Training)
class TrainingAdmin(admin.ModelAdmin):
    list_display = ['date', 'location', 'season', 'created_by']
    list_filter = ['season']

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['player', 'status', 'match', 'training', 'reason']
    list_filter = ['status']

@admin.register(PlayerStatistic)
class PlayerStatisticAdmin(admin.ModelAdmin):
    list_display = ['player', 'match', 'points', 'kills', 'aces', 'blocks', 'rating']

@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = ['player', 'transfer_type', 'from_club', 'to_club', 'fee', 'date', 'season']
    list_filter = ['transfer_type', 'season']

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['category', 'amount', 'date', 'description', 'season']
    list_filter = ['category', 'season']
