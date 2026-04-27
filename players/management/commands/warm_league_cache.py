"""
Warm the file-based cache with the Italian Volleyball League data, and
optionally write an offline snapshot file used as a fallback when the API
is throttled or unreachable.

Run:
    python manage.py warm_league_cache
    python manage.py warm_league_cache --save-snapshot
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import requests
from django.conf import settings
from django.core.cache import cache
from django.core.management.base import BaseCommand

from players import league_service


_BASE = "https://www.thesportsdb.com/api/v1/json"


def _api_get(path: str, params: dict, retries: int = 3, sleep_between: float = 0.4) -> dict:
    url = f"{_BASE}/{settings.LEAGUE_API_KEY}/{path}"
    for attempt in range(retries):
        try:
            time.sleep(sleep_between)
            r = requests.get(url, params=params, timeout=settings.LEAGUE_API_TIMEOUT)
            if r.status_code == 200:
                try:
                    return r.json() or {}
                except ValueError:
                    return {}
            if r.status_code == 429:
                time.sleep(2.0 * (attempt + 1))
                continue
            return {}
        except requests.RequestException:
            time.sleep(1.0)
    return {}


class Command(BaseCommand):
    help = "Fetch all league rounds + team data and populate the cache. Optionally save a snapshot."

    def add_arguments(self, parser):
        parser.add_argument("--save-snapshot", action="store_true",
                            help="Also write players/league_snapshot.json as offline fallback")
        parser.add_argument("--clear", action="store_true", help="Clear cache first")

    def handle(self, *args, **opts):
        if opts["clear"]:
            cache.clear()
            self.stdout.write(self.style.WARNING("Cache cleared."))

        all_events: list[dict] = []
        rounds = list(range(1, settings.LEAGUE_REGULAR_SEASON_ROUNDS + 1)) + [0]
        self.stdout.write(f"Fetching {len(rounds)} rounds for league {settings.LEAGUE_ID} season {settings.LEAGUE_SEASON}…")
        for r in rounds:
            payload = _api_get("eventsround.php", {
                "id": settings.LEAGUE_ID,
                "r": r,
                "s": settings.LEAGUE_SEASON,
            })
            evs = (payload or {}).get("events") or []
            self.stdout.write(f"  round {r:>2}: {len(evs)} events")
            all_events.extend(evs)

        # League info + teams
        info_payload = _api_get("lookupleague.php", {"id": settings.LEAGUE_ID})
        leagues = (info_payload or {}).get("leagues") or []
        info = leagues[0] if leagues else {}

        teams_payload = _api_get(
            "search_all_teams.php",
            {"l": settings.LEAGUE_NAME.split(" (")[0]},
        )
        teams_raw = (teams_payload or {}).get("teams") or []

        # Prime the cache so the next view request is instant.
        cache.set("league:all_events_v2",
                  [league_service._normalize(e) for e in all_events],
                  60 * 60 * 6)

        if opts["save_snapshot"]:
            snapshot = {
                "info": {
                    "name": info.get("strLeague") or settings.LEAGUE_NAME,
                    "country": info.get("strCountry") or "Italy",
                    "badge": info.get("strBadge") or info.get("strLogo") or "",
                    "description": (info.get("strDescriptionEN") or "").strip(),
                    "website": info.get("strWebsite") or "",
                    "season": settings.LEAGUE_SEASON,
                },
                "teams": [
                    {
                        "id": t.get("idTeam"),
                        "name": t.get("strTeam"),
                        "stadium": t.get("strStadium") or "",
                        "country": t.get("strCountry") or "",
                        "badge": t.get("strBadge") or t.get("strTeamBadge") or "",
                    }
                    for t in teams_raw
                ],
                "events": all_events,
                "league": settings.LEAGUE_NAME,
                "season": settings.LEAGUE_SEASON,
                "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }
            path = Path(settings.BASE_DIR) / "players" / "league_snapshot.json"
            path.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False), encoding="utf-8")
            self.stdout.write(self.style.SUCCESS(f"Snapshot saved to {path}"))

        self.stdout.write(self.style.SUCCESS(
            f"Done. {len(all_events)} events, {len(teams_raw)} teams cached."
        ))
