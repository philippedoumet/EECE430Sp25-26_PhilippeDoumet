"""
Seed the database with realistic demo data for the Volley Manager demo.

Creates:
  - Superuser + Owner profile
  - 2 Coach accounts
  - 14 Player accounts (full Volley Perugia–style roster)
  - Active season 2025-2026
  - Past matches (with scores) and upcoming matches mirroring the real
    Italian Volleyball League SuperLega calendar
  - Trainings (past and upcoming)
  - Attendance + per-match player statistics
  - Transfers and expenses

Run:    python manage.py seed_demo
        python manage.py seed_demo --reset    (wipes existing demo data first)
"""
from __future__ import annotations

import datetime as _dt
import random
from decimal import Decimal

from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from players.models import (
    Attendance, Coach, ClubOwner, Expense, Match, Player,
    PlayerStatistic, Season, Training, Transfer,
)


# ---------------------------------------------------------------------------
# Demo dataset (deterministic — same seed every run)
# ---------------------------------------------------------------------------

SEASON = {"name": "2025-2026", "start": _dt.date(2025, 9, 1), "end": _dt.date(2026, 5, 31)}

OWNER = {
    "username": "owner",
    "password": "Owner@2026",
    "first_name": "Marco",
    "last_name": "Bianchi",
    "email": "owner@volleyperugia.it",
    "phone": "+39 075 555 0100",
}

COACHES = [
    {"username": "coach", "password": "Coach@2026",
     "first_name": "Andrea", "last_name": "Lorenzetti",
     "email": "head.coach@volleyperugia.it",
     "phone": "+39 075 555 0110", "specialty": "Head Coach — Attack"},
    {"username": "coach2", "password": "Coach@2026",
     "first_name": "Daniele", "last_name": "Bagnoli",
     "email": "assistant.coach@volleyperugia.it",
     "phone": "+39 075 555 0111", "specialty": "Assistant Coach — Defense"},
]

# Roster modelled after a typical SuperLega squad (made-up but plausible)
PLAYERS = [
    {"name": "Simone Giannelli",   "position": "Setter",            "jersey": 6,  "salary": 24000, "nationality": "Italy",     "height": 199, "birth": "1996-08-09"},
    {"name": "Wassim Ben Tara",    "position": "Opposite Hitter",   "jersey": 9,  "salary": 22000, "nationality": "Tunisia",   "height": 205, "birth": "1996-12-13"},
    {"name": "Kamil Semeniuk",     "position": "Outside Hitter",    "jersey": 11, "salary": 19000, "nationality": "Poland",    "height": 199, "birth": "1996-08-26"},
    {"name": "Oleh Plotnytskyi",   "position": "Outside Hitter",    "jersey": 17, "salary": 18000, "nationality": "Ukraine",   "height": 200, "birth": "1996-04-08"},
    {"name": "Roberto Russo",      "position": "Middle Blocker",   "jersey": 13, "salary": 16000, "nationality": "Italy",     "height": 207, "birth": "1997-09-13"},
    {"name": "Sebastian Solé",     "position": "Middle Blocker",   "jersey": 5,  "salary": 17500, "nationality": "Argentina", "height": 207, "birth": "1991-11-23"},
    {"name": "Massimo Colaci",     "position": "Libero",            "jersey": 14, "salary": 14000, "nationality": "Italy",     "height": 175, "birth": "1985-04-14"},
    {"name": "Jesús Herrera",      "position": "Outside Hitter",    "jersey": 20, "salary": 15000, "nationality": "Cuba",      "height": 198, "birth": "1995-05-02"},
    {"name": "Donovan Cvetković",  "position": "Opposite Hitter",   "jersey": 24, "salary": 12500, "nationality": "Serbia",    "height": 204, "birth": "2000-03-20"},
    {"name": "Luca Piccinelli",    "position": "Setter",            "jersey": 8,  "salary": 11000, "nationality": "Italy",     "height": 191, "birth": "2001-07-15"},
    {"name": "Davide Candellaro",  "position": "Middle Blocker",   "jersey": 12, "salary": 13500, "nationality": "Italy",     "height": 209, "birth": "1990-01-10"},
    {"name": "Antoine Brizard",    "position": "Setter",            "jersey": 16, "salary": 15500, "nationality": "France",    "height": 195, "birth": "1994-08-25"},
    {"name": "Yacine Toumi",       "position": "Defensive Specialist","jersey": 22, "salary": 9500, "nationality": "Algeria",   "height": 190, "birth": "1999-02-18"},
    {"name": "Marco Vitelli",      "position": "Libero",            "jersey": 7,  "salary": 10000, "nationality": "Italy",     "height": 178, "birth": "1998-06-30"},
]

# Past matches (real SuperLega-style results)
PAST_MATCHES = [
    # date,           opponent,                  venue,  type,     home_sets, away_sets, our_role
    ("2025-09-28 17:00", "Modena Volley",        "home", "league", 3, 1, "home"),
    ("2025-10-05 18:30", "Volley Lube",          "away", "league", 1, 3, "away"),
    ("2025-10-12 17:00", "Trentino Volley",      "home", "league", 3, 0, "home"),
    ("2025-10-19 16:00", "You Energy Volley",    "away", "league", 3, 2, "away"),
    ("2025-10-26 17:00", "Verona Volley",        "home", "league", 3, 1, "home"),
    ("2025-11-02 16:00", "Cisterna Volley",      "away", "league", 3, 0, "away"),
    ("2025-11-09 17:00", "Powervolley Milano",   "home", "league", 3, 2, "home"),
    ("2025-11-16 18:00", "Volley Milano",        "home", "league", 3, 0, "home"),
    ("2025-11-23 17:00", "Pallavolo Padova",     "away", "league", 3, 1, "away"),
    ("2025-11-30 17:00", "Prisma Taranto",       "home", "cup",    3, 0, "home"),
    ("2025-12-07 18:00", "Modena Volley",        "away", "league", 2, 3, "away"),
    ("2025-12-14 17:00", "Volley Lube",          "home", "league", 3, 2, "home"),
    ("2026-01-11 17:00", "Trentino Volley",      "away", "league", 0, 3, "away"),
    ("2026-01-18 17:00", "You Energy Volley",    "home", "league", 3, 0, "home"),
    ("2026-01-25 17:00", "Verona Volley",        "away", "league", 3, 1, "away"),
    ("2026-02-01 17:00", "Cisterna Volley",      "home", "league", 3, 0, "home"),
    ("2026-02-08 18:00", "Powervolley Milano",   "away", "league", 3, 1, "away"),
    ("2026-02-22 17:00", "Volley Milano",        "away", "league", 3, 1, "away"),
    ("2026-03-08 17:00", "M&G Scuola Pallavolo", "home", "playoff",3, 0, "home"),
    ("2026-03-15 17:00", "M&G Scuola Pallavolo", "away", "playoff",3, 1, "away"),
    ("2026-04-06 15:30", "You Energy Volley",    "home", "playoff",3, 1, "home"),
    ("2026-04-09 18:30", "You Energy Volley",    "away", "playoff",3, 1, "away"),
    ("2026-04-12 16:00", "You Energy Volley",    "home", "playoff",3, 0, "home"),
]

# Upcoming matches — the SuperLega final vs Volley Lube
UPCOMING_MATCHES = [
    ("2026-04-30 18:30", "Volley Lube",      "home", "playoff", "Game 1 of the SuperLega Final"),
    ("2026-05-03 16:00", "Volley Lube",      "away", "playoff", "Game 2 of the SuperLega Final"),
    ("2026-05-06 18:30", "Volley Lube",      "home", "playoff", "Game 3 of the SuperLega Final"),
    ("2026-05-10 16:00", "Volley Lube",      "away", "playoff", "Game 4 (if necessary)"),
    ("2026-05-14 19:30", "Volley Lube",      "home", "playoff", "Game 5 (if necessary)"),
]

UPCOMING_TRAININGS = [
    ("2026-04-28 17:00", "PalaEvangelisti",  "Tactical session — Volley Lube scouting"),
    ("2026-04-29 10:30", "PalaEvangelisti",  "Walk-through, serve-receive drills"),
    ("2026-05-01 17:00", "PalaEvangelisti",  "Recovery + light strength"),
    ("2026-05-02 10:30", "PalaEvangelisti",  "Pre-match shake-out, video review"),
    ("2026-05-04 17:00", "Tennis Club Conad", "Recovery — pool & mobility"),
    ("2026-05-05 10:30", "PalaEvangelisti",  "Game 3 prep — block & defense"),
]

PAST_TRAININGS = [
    ("2025-09-22 17:00", "PalaEvangelisti",  "Pre-season fitness"),
    ("2025-09-25 17:00", "PalaEvangelisti",  "Tactical drills"),
    ("2026-02-10 17:00", "PalaEvangelisti",  "Block & defense workshop"),
    ("2026-03-05 17:00", "PalaEvangelisti",  "Playoffs ramp-up"),
    ("2026-04-15 17:00", "PalaEvangelisti",  "Final preparation — week 1"),
]

EXPENSES = [
    ("salary",    240000, "2025-09-30", "September 2025 — player salaries"),
    ("coaching",  35000,  "2025-09-30", "September 2025 — coaching staff"),
    ("equipment", 12500,  "2025-10-04", "Mizuno match jerseys & shoes"),
    ("travel",    8400,   "2025-10-12", "Away trip to Civitanova"),
    ("medical",   3200,   "2025-11-02", "Physio sessions — November"),
    ("facility",  18000,  "2025-12-15", "PalaEvangelisti rental — Q4"),
    ("salary",    240000, "2025-12-30", "December 2025 — player salaries"),
    ("transfer",  45000,  "2026-01-15", "Mid-season loan-in fee — A. Brizard"),
    ("travel",    11200,  "2026-02-22", "Away trip to Milano"),
    ("salary",    240000, "2026-03-30", "March 2026 — player salaries"),
    ("medical",   4500,   "2026-04-04", "Recovery treatments — playoff"),
    ("travel",    9800,   "2026-04-12", "Logistics — playoff round 1"),
]


def _parse(dt_str: str):
    naive = _dt.datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
    return timezone.make_aware(naive)


# ---------------------------------------------------------------------------

class Command(BaseCommand):
    help = "Seed the database with demo data (owner, coach, players, matches, stats)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset", action="store_true",
            help="Wipe existing demo data before seeding (keeps superusers untouched).",
        )

    @transaction.atomic
    def handle(self, *args, **opts):
        random.seed(42)
        if opts["reset"]:
            self._reset()

        # Groups
        for name in ("Owner", "Coach", "Player"):
            Group.objects.get_or_create(name=name)

        season = self._seed_season()
        owner = self._seed_owner()
        coaches = self._seed_coaches()
        players = self._seed_players()
        matches = self._seed_past_matches(season)
        upcoming = self._seed_upcoming_matches(season)
        all_matches = matches + upcoming
        trainings = self._seed_trainings(season, coaches[0])
        self._seed_attendance_and_stats(players, all_matches, trainings)
        self._seed_transfers(players, season)
        self._seed_expenses(season)

        self._print_credentials(owner, coaches, players)

    # ------------------------------------------------------------------ helpers

    def _reset(self):
        self.stdout.write(self.style.WARNING("Resetting demo data…"))
        # Delete in dependency order
        Attendance.objects.all().delete()
        PlayerStatistic.objects.all().delete()
        Transfer.objects.all().delete()
        Expense.objects.all().delete()
        Match.objects.all().delete()
        Training.objects.all().delete()
        Player.objects.all().delete()
        Coach.objects.all().delete()
        ClubOwner.objects.all().delete()
        Season.objects.all().delete()
        # Drop demo users (keep superusers we didn't create here)
        User.objects.filter(is_superuser=False).delete()

    def _seed_season(self) -> Season:
        Season.objects.update(is_active=False)
        season, created = Season.objects.get_or_create(
            name=SEASON["name"],
            defaults={
                "start_date": SEASON["start"],
                "end_date": SEASON["end"],
                "is_active": True,
            },
        )
        if not created:
            season.start_date = SEASON["start"]
            season.end_date = SEASON["end"]
            season.is_active = True
            season.save()
        return season

    def _seed_owner(self) -> User:
        info = OWNER
        user, created = User.objects.get_or_create(
            username=info["username"],
            defaults={
                "first_name": info["first_name"],
                "last_name": info["last_name"],
                "email": info["email"],
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            user.set_password(info["password"])
            user.save()
        else:
            # always ensure password is the demo password
            user.set_password(info["password"])
            user.is_superuser = True
            user.is_staff = True
            user.first_name = info["first_name"]
            user.last_name = info["last_name"]
            user.email = info["email"]
            user.save()
        ClubOwner.objects.update_or_create(user=user, defaults={"phone": info["phone"]})
        return user

    def _seed_coaches(self) -> list[Coach]:
        coaches = []
        for info in COACHES:
            user, created = User.objects.get_or_create(
                username=info["username"],
                defaults={
                    "first_name": info["first_name"],
                    "last_name": info["last_name"],
                    "email": info["email"],
                },
            )
            user.set_password(info["password"])
            user.first_name = info["first_name"]
            user.last_name = info["last_name"]
            user.email = info["email"]
            user.save()
            coach, _ = Coach.objects.update_or_create(
                user=user,
                defaults={"phone": info["phone"], "specialty": info["specialty"]},
            )
            coaches.append(coach)
        return coaches

    def _seed_players(self) -> list[Player]:
        out: list[Player] = []
        for i, info in enumerate(PLAYERS, start=1):
            first, last = info["name"].split(" ", 1)
            username = f"player{i:02d}"
            user, _ = User.objects.get_or_create(
                username=username,
                defaults={"first_name": first, "last_name": last,
                          "email": f"{username}@volleyperugia.it"},
            )
            user.set_password("Player@2026")
            user.first_name = first
            user.last_name = last
            user.email = f"{username}@volleyperugia.it"
            user.save()
            player, _ = Player.objects.update_or_create(
                name=info["name"],
                defaults={
                    "user": user,
                    "position": info["position"],
                    "jersey_number": info["jersey"],
                    "salary": Decimal(info["salary"]),
                    "date_joined": _dt.date(2025, 7, 1),
                    "contact_person": "Volley Perugia HR",
                    "phone": f"+39 075 555 02{i:02d}",
                    "birth_date": _dt.date.fromisoformat(info["birth"]),
                    "nationality": info["nationality"],
                    "height_cm": info["height"],
                    "is_active": True,
                },
            )
            out.append(player)
        return out

    def _seed_past_matches(self, season: Season) -> list[Match]:
        matches = []
        for dt_str, opp, venue, mtype, hs, as_, our_role in PAST_MATCHES:
            sw, sl = (hs, as_) if our_role == "home" else (as_, hs)
            match, _ = Match.objects.update_or_create(
                season=season, date=_parse(dt_str), opponent=opp,
                defaults={
                    "venue": venue, "match_type": mtype,
                    "sets_won": sw, "sets_lost": sl,
                    "notes": "Italian Volleyball League — SuperLega",
                },
            )
            matches.append(match)
        return matches

    def _seed_upcoming_matches(self, season: Season) -> list[Match]:
        matches = []
        for dt_str, opp, venue, mtype, note in UPCOMING_MATCHES:
            match, _ = Match.objects.update_or_create(
                season=season, date=_parse(dt_str), opponent=opp,
                defaults={
                    "venue": venue, "match_type": mtype,
                    "sets_won": None, "sets_lost": None,
                    "notes": note,
                },
            )
            matches.append(match)
        return matches

    def _seed_trainings(self, season: Season, coach: Coach) -> list[Training]:
        trainings = []
        for dt_str, location, desc in PAST_TRAININGS + UPCOMING_TRAININGS:
            t, _ = Training.objects.update_or_create(
                season=season, date=_parse(dt_str),
                defaults={"location": location, "description": desc, "created_by": coach},
            )
            trainings.append(t)
        return trainings

    def _seed_attendance_and_stats(self, players, matches, trainings):
        # Attendance for past matches: most players present, a couple absent/late
        for m in matches:
            played = m.sets_won is not None
            for p in players:
                roll = random.random()
                if roll < 0.83:
                    status = "present"
                    reason = ""
                elif roll < 0.93:
                    status = "late"
                    reason = "Traffic delay"
                elif roll < 0.97:
                    status = "excused"
                    reason = "Recovery rotation"
                else:
                    status = "absent"
                    reason = "Personal"
                Attendance.objects.update_or_create(
                    player=p, match=m,
                    defaults={"status": status, "reason": reason, "training": None},
                )

            if not played:
                continue

            # Per-player match statistics — scaled to position + match outcome
            our_won = m.sets_won > m.sets_lost
            total_sets = m.sets_won + m.sets_lost
            for p in players:
                base = self._stat_baseline_for(p.position, our_won, total_sets)
                if base is None:
                    continue
                PlayerStatistic.objects.update_or_create(
                    player=p, match=m,
                    defaults=base,
                )

        # Past trainings — mostly present
        now = timezone.now()
        for t in trainings:
            if t.date > now:
                continue
            for p in players:
                roll = random.random()
                status = "present" if roll < 0.9 else ("late" if roll < 0.96 else "absent")
                Attendance.objects.update_or_create(
                    player=p, training=t,
                    defaults={"status": status, "reason": "", "match": None},
                )

    def _stat_baseline_for(self, position: str, won: bool, total_sets: int) -> dict | None:
        """Return a realistic stat dict for a player based on their role."""
        scale = total_sets / 4.0  # 4-set match = 1.0
        win_bonus = 1.1 if won else 0.85

        def jitter(low, high):
            return int(round(random.uniform(low, high) * scale * win_bonus))

        if position == "Setter":
            return {
                "points": jitter(2, 6),  "kills": jitter(0, 2),  "aces": jitter(0, 2),
                "blocks": jitter(0, 2),  "digs": jitter(2, 6),
                "errors": jitter(1, 3),  "minutes_played": jitter(75, 100),
                "rating": Decimal(f"{random.uniform(6.5, 8.5):.1f}"),
            }
        if position == "Outside Hitter":
            return {
                "points": jitter(10, 18), "kills": jitter(8, 14),  "aces": jitter(0, 2),
                "blocks": jitter(0, 2),   "digs": jitter(4, 9),
                "errors": jitter(2, 5),   "minutes_played": jitter(75, 100),
                "rating": Decimal(f"{random.uniform(6.0, 9.0):.1f}"),
            }
        if position == "Opposite Hitter":
            return {
                "points": jitter(12, 22), "kills": jitter(10, 18), "aces": jitter(0, 3),
                "blocks": jitter(0, 3),   "digs": jitter(2, 5),
                "errors": jitter(2, 5),   "minutes_played": jitter(75, 100),
                "rating": Decimal(f"{random.uniform(6.0, 9.5):.1f}"),
            }
        if position == "Middle Blocker":
            return {
                "points": jitter(6, 12),  "kills": jitter(3, 7),   "aces": jitter(0, 1),
                "blocks": jitter(2, 6),   "digs": jitter(0, 2),
                "errors": jitter(1, 3),   "minutes_played": jitter(60, 90),
                "rating": Decimal(f"{random.uniform(6.5, 8.5):.1f}"),
            }
        if position == "Libero":
            return {
                "points": 0, "kills": 0, "aces": 0, "blocks": 0,
                "digs": jitter(8, 18), "errors": jitter(1, 3),
                "minutes_played": jitter(75, 100),
                "rating": Decimal(f"{random.uniform(6.5, 9.0):.1f}"),
            }
        # Defensive Specialist / fallback
        return {
            "points": jitter(0, 4), "kills": jitter(0, 2),  "aces": jitter(0, 1),
            "blocks": jitter(0, 1), "digs": jitter(3, 9),
            "errors": jitter(0, 2), "minutes_played": jitter(20, 60),
            "rating": Decimal(f"{random.uniform(6.0, 8.0):.1f}"),
        }

    def _seed_transfers(self, players, season):
        if len(players) < 4:
            return
        Transfer.objects.update_or_create(
            player=players[0], transfer_type="in",
            defaults={"from_club": "Trentino Volley", "to_club": "Volley Perugia",
                      "fee": Decimal(150000), "date": _dt.date(2025, 7, 5),
                      "season": season, "notes": "Marquee summer signing"},
        )
        Transfer.objects.update_or_create(
            player=players[3], transfer_type="loan_in",
            defaults={"from_club": "PGE Skra Bełchatów", "to_club": "Volley Perugia",
                      "fee": Decimal(40000), "date": _dt.date(2025, 7, 12),
                      "season": season, "notes": "Season-long loan"},
        )
        Transfer.objects.update_or_create(
            player=players[8], transfer_type="out",
            defaults={"from_club": "Volley Perugia", "to_club": "Volley Milano",
                      "fee": Decimal(70000), "date": _dt.date(2025, 8, 1),
                      "season": season, "notes": "Permanent transfer"},
        )

    def _seed_expenses(self, season):
        for cat, amount, date_str, desc in EXPENSES:
            Expense.objects.update_or_create(
                category=cat, date=_dt.date.fromisoformat(date_str),
                description=desc,
                defaults={"amount": Decimal(amount), "season": season},
            )

    def _print_credentials(self, owner, coaches, players):
        line = "=" * 70
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(line))
        self.stdout.write(self.style.SUCCESS("  DEMO DATA SEEDED — credentials below"))
        self.stdout.write(self.style.SUCCESS(line))
        self.stdout.write(f"  Owner / Admin   : {owner.username:<14}  password: {OWNER['password']}")
        for info, c in zip(COACHES, coaches):
            self.stdout.write(f"  Coach           : {info['username']:<14}  password: {info['password']}  ({c.specialty})")
        self.stdout.write(f"  Players         : player01 .. player{len(PLAYERS):02d}   password: Player@2026")
        self.stdout.write(self.style.SUCCESS(line))
        self.stdout.write("")
