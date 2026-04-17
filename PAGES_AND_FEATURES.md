# Volley Manager — Pages, Features & Implementation Reference

> EECE 430 · Spring 2025-26 · Philippe Doumet (202303965)

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [User Roles](#2-user-roles)
3. [Setup & Authentication Pages](#3-setup--authentication-pages)
4. [Owner Portal](#4-owner-portal)
5. [Coach Portal](#5-coach-portal)
6. [Player Portal](#6-player-portal)
7. [Django Admin](#7-django-admin)
8. [Full URL Reference](#8-full-url-reference)
9. [Data Models Reference](#9-data-models-reference)
10. [How to Create Users & Assign Roles](#10-how-to-create-users--assign-roles)
11. [Docker & Deployment](#11-docker--deployment)
12. [Implemented Features Summary](#12-implemented-features-summary)

---

## 1. System Overview

Volley Manager is a multi-portal Django 6.0.3 web application for managing a volleyball club. It separates concerns into three distinct portals, each with its own dashboard, navigation, and colour scheme:

| Portal | Colour | Who uses it |
|--------|--------|-------------|
| Owner  | Navy / Purple gradient | Club owner, superuser |
| Coach  | Green gradient | Team coaches |
| Player | Purple gradient | Individual players |

Authentication is shared across all portals. After login the system automatically redirects each user to their own portal based on their Django Group membership.

---

## 2. User Roles

| Role | Django Group | Access |
|------|-------------|--------|
| **Superuser** | (built-in Django) | Owner portal + `/admin/` |
| **Owner** | `Owner` | Owner portal |
| **Coach** | `Coach` | Coach portal |
| **Player** | `Player` | Player portal |

> A user can only belong to one role group. The login view checks groups in the order: Owner → Coach → Player.

---

## 3. Setup & Authentication Pages

### `/setup/` — First-Run Superuser Wizard
**Template:** `accounts/templates/accounts/setup.html`

- Shown automatically when **no superuser exists in the database**.
- Any visit to `/login/` is also redirected here until a superuser is created.
- Form fields: Username, Email (optional), Password, Confirm Password.
- Validation: username uniqueness, password length ≥ 8, passwords match.
- On success: creates a Django superuser and redirects to `/setup/done/`.
- Once a superuser exists this page redirects to `/login/` (cannot be accessed again).

### `/setup/done/` — Setup Complete Confirmation
**Template:** `accounts/templates/accounts/setup_done.html`

- Simple success screen shown after the first superuser is created.
- Contains a "Go to Login" button.

### `/login/` — Sign In
**Template:** `accounts/templates/accounts/login.html`

- Standard username + password form.
- On success redirects to the user's portal based on their group.
- Shows error message on bad credentials.
- Auto-redirects to `/setup/` if no superuser exists.
- Footer link to `/admin/` (Django Admin).

### `/logout/` — Sign Out
- Logs the user out and redirects to `/login/`.

---

## 4. Owner Portal

> Accessible to: Superusers and users in the `Owner` group.
> Sidebar colour: Navy / Purple (`#0f3460` → `#533483`)

### `/owner/` — Owner Dashboard
**View:** `OwnerDashboardView`
**Template:** `players/templates/players/owner/dashboard.html`

Shows a high-level snapshot of the club:
- Active season name
- Total active players count
- Total matches played and win rate (%)
- Total training sessions this season
- Recent match results (last 5) with score and win/loss badge
- Upcoming matches (next 3)
- Expense summary: total spent this season + breakdown by category (pie data)
- Transfer activity: recent player transfers in/out
- Quick-action buttons to all major sections

### `/owner/roster/` — Full Player Roster
**View:** `OwnerRosterView`
**Template:** `players/templates/players/owner/roster.html`

- Table of all active players
- Columns: Name, Position, Jersey #, Nationality, Salary, Date Joined, Status
- Links to player detail (coach view)

### `/owner/performance/` — Team Performance
**View:** `TeamPerformanceView`
**Template:** `players/templates/players/owner/performance.html`

- Match results table for the active season (date, opponent, score, venue, result)
- Season aggregate: total wins, losses, sets won/lost
- Top scorers table (points per player)

### `/owner/seasons/` — Season Management
**View:** `SeasonListView`
**Template:** `players/templates/players/owner/season_list.html`

- Lists all seasons (active season highlighted)
- Links to create, edit, delete each season

### `/owner/seasons/new/` — Create Season
**View:** `SeasonCreateView`
**Template:** `players/templates/players/owner/season_form.html`

- Fields: Name, Start Date, End Date, Is Active
- Setting Is Active automatically deactivates all other seasons (enforced in `Season.save()`)

### `/owner/seasons/<pk>/edit/` — Edit Season
**View:** `SeasonUpdateView` — same form as create

### `/owner/seasons/<pk>/delete/` — Delete Season
**View:** `SeasonDeleteView`
**Template:** `players/templates/players/owner/season_confirm_delete.html`

### `/owner/expenses/` — Expense Tracker
**View:** `ExpenseListView`
**Template:** `players/templates/players/owner/expense_list.html`

- Lists all expenses for the active season
- Columns: Date, Category, Description, Amount
- Category badges (Salary, Equipment, Travel, Medical, Facility, Marketing, Transfers, Other)
- Inline delete button per expense
- Total at the bottom

### `/owner/expenses/<pk>/delete/` — Delete Expense
**View:** `ExpenseDeleteView`

### `/owner/transfers/` — Transfer Log
**View:** `TransferListView`
**Template:** `players/templates/players/owner/transfer_list.html`

- Lists all player transfers for the active season
- Columns: Player, Type (In/Out/Loan), From Club, To Club, Fee, Date
- Transfer type badges (success/danger/warning)

---

## 5. Coach Portal

> Accessible to: Users in the `Coach` group.
> Sidebar colour: Green (`#134e2a` → `#1a7a40`)

### `/coach/` — Coach Dashboard
**View:** `CoachDashboardView`
**Template:** `players/templates/players/coach/dashboard.html`

- Active season name
- Total active players
- Upcoming matches (next 3 with date, opponent, venue)
- Upcoming trainings (next 3)
- Quick-action buttons (Add Player, Schedule Match, Schedule Training)
- Recent match results (last 5)

### `/coach/players/` — Player List
**View:** `CoachPlayerListView`
**Template:** `players/templates/players/coach/player_list.html`

- Table of all active players
- Columns: Jersey #, Name, Position, Nationality, Height, Salary, Account status
- "Has Account" badge (green if linked to a Django User, grey if not)
- Action buttons: View Detail, Edit, Delete, Create Account

### `/coach/players/new/` — Add Player
**View:** `CoachPlayerCreateView`
**Template:** `players/templates/players/coach/player_form.html`

Fields: Name, Position, Jersey Number, Salary, Date Joined, Contact Person, Phone, Birth Date, Nationality, Height (cm), Is Active

### `/coach/players/<pk>/` — Player Detail
**View:** `CoachPlayerDetailView`
**Template:** `players/templates/players/coach/player_detail.html`

- Full player profile (bio data, salary, contact)
- Season stats card (points, kills, aces, blocks, digs this season)
- Attendance rate for the active season
- Per-match attendance history
- Link to create/manage player account

### `/coach/players/<pk>/edit/` — Edit Player
**View:** `CoachPlayerUpdateView` — same form as create

### `/coach/players/<pk>/delete/` — Delete Player
**View:** `CoachPlayerDeleteView`
**Template:** `players/templates/players/coach/player_confirm_delete.html`

### `/coach/players/<pk>/account/` — Create Player Account
**View:** `CoachCreatePlayerAccountView`
**Template:** `players/templates/players/coach/player_account_form.html`

- Creates a Django `User` account for the player
- Fields: Username, Password, Confirm Password
- Automatically adds the user to the `Player` group
- Links the user to the `Player` model (one-to-one)
- Only shown if the player does not already have an account

### `/coach/matches/` — Match List
**View:** `MatchListView`
**Template:** `players/templates/players/coach/match_list.html`

- Table of all matches for the active season
- Columns: Date, Opponent, Venue, Type, Score, Result
- Result badge (Win/Loss/Draw/Upcoming)
- Action buttons: View, Edit, Attendance, Stats, Delete

### `/coach/matches/new/` — Schedule Match
**View:** `MatchCreateView`
**Template:** `players/templates/players/coach/match_form.html`

Fields: Season, Date & Time, Opponent, Venue (Home/Away/Neutral), Match Type (League/Cup/Friendly/Tournament), Sets Won, Sets Lost, Notes

### `/coach/matches/<pk>/edit/` — Edit Match
**View:** `MatchUpdateView`

### `/coach/matches/<pk>/delete/` — Delete Match
**View:** `MatchDeleteView`

### `/coach/matches/<pk>/` — Match Detail
**View:** `MatchDetailView`
**Template:** `players/templates/players/coach/match_detail.html`

- Full match info (date, opponent, score, venue, type, notes)
- Attendance summary (present/absent/late/excused counts)
- Player statistics table for this match
- Links to attendance and stats entry forms

### `/coach/matches/<pk>/attendance/` — Record Match Attendance
**View:** `MatchAttendanceView`
**Template:** `players/templates/players/coach/match_attendance.html`

- Lists all active players
- Per-player dropdown: Present / Absent / Excused / Late
- Optional reason text field
- Single "Save All" button → `update_or_create` per player

### `/coach/matches/<pk>/stats/` — Enter Match Statistics
**View:** `MatchStatsView`
**Template:** `players/templates/players/coach/match_stats.html`

- Lists all active players
- Per-player numeric inputs: Points, Kills, Aces, Blocks, Digs, Errors, Minutes Played, Rating
- Single "Save All" button → `update_or_create` per player

### `/coach/trainings/` — Training Sessions
**View:** `TrainingListView`
**Template:** `players/templates/players/coach/training_list.html`

- Table of all training sessions for the active season
- Columns: Date, Location, Description, Actions

### `/coach/trainings/new/` — Schedule Training
**View:** `TrainingCreateView`
**Template:** `players/templates/players/coach/training_form.html`

Fields: Season, Date & Time, Location, Description

### `/coach/trainings/<pk>/edit/` — Edit Training
**View:** `TrainingUpdateView`

### `/coach/trainings/<pk>/delete/` — Delete Training
**View:** `TrainingDeleteView`

### `/coach/trainings/<pk>/attendance/` — Record Training Attendance
**View:** `TrainingAttendanceView`
**Template:** `players/templates/players/coach/training_attendance.html`

- Same bulk attendance form as match attendance
- Saves to `Attendance` model with `training` FK instead of `match`

### `/coach/stats/` — Season Statistics
**View:** `CoachSeasonStatsView`
**Template:** `players/templates/players/coach/season_stats.html`

- One row per player for the active season
- Columns: Player Name, Position, Points, Kills, Aces, Blocks, Digs, Attendance %
- Attendance colour-coded: green ≥ 80%, yellow ≥ 60%, red < 60%

---

## 6. Player Portal

> Accessible to: Users in the `Player` group.
> Sidebar colour: Purple (`#4a1070` → `#7b2fa8`)

### `/player/` — Player Dashboard
**View:** `PlayerDashboardView`
**Template:** `players/templates/players/player_portal/dashboard.html`

- Welcome banner with player name, position, jersey number, active season
- Stat cards: Points This Season, Kills This Season, Attendance Rate %, Blocks This Season
- Upcoming Events panel (next match + next training with date, time, venue)
- Recent Team Results table (last 5 matches)
- My Profile card (salary, date joined, contact person, nationality, height, phone)

### `/player/calendar/` — My Calendar
**View:** `PlayerCalendarView`
**Template:** `players/templates/players/player_portal/calendar.html`

- Two-column layout: Upcoming Matches | Upcoming Trainings
- Each event shows: opponent/location, date & time, venue, match type
- Current attendance status badge (if already marked)
- **Present / Absent buttons** — player can self-report attendance before the event
- Buttons highlight (solid) when that status is already set

### `/player/attendance/mark/` — Mark Attendance (POST only)
**View:** `PlayerMarkAttendanceView`

- Accepts POST from calendar buttons
- Parameters: `match_id` or `training_id`, `status`
- Uses `update_or_create` so the player can change their answer

### `/player/attendance/` — My Attendance History
**View:** `PlayerMyAttendanceView`
**Template:** `players/templates/players/player_portal/attendance.html`

- Two-column table: Match Attendance | Training Attendance
- Each row shows event name, date, status badge (colour-coded)
- Overall attendance rate shown in header
- "No records" placeholder when empty

### `/player/stats/` — My Statistics
**View:** `PlayerMyStatsView`
**Template:** `players/templates/players/player_portal/stats.html`

- Season totals row: Points, Kills, Aces, Blocks, Digs, Attendance %
- Attendance colour-coded: green ≥ 80%, yellow ≥ 60%, red < 60%
- Per-match breakdown table: Date, Opponent, Result badge, all stat columns, Minutes Played
- "No active season" alert when no season is active

---

## 7. Django Admin

**URL:** `/admin/`

All 10 models are registered with custom `list_display` and filters:

| Model | list_display |
|-------|-------------|
| Season | name, start_date, end_date, is_active |
| ClubOwner | user |
| Coach | user, phone, specialty |
| Player | name, position, jersey_number, salary, is_active, user |
| Match | date, opponent, venue, match_type, season, result |
| Training | date, location, season, created_by |
| Attendance | player, match, training, status |
| PlayerStatistic | player, match, points, kills |
| Transfer | player, transfer_type, from_club, to_club, fee, season |
| Expense | category, amount, date, season |

Use the admin to:
- Create Owner / Coach / Player Django users and assign groups
- Create `ClubOwner` / `Coach` profile records linked to users
- Manage all data directly

---

## 8. Full URL Reference

| URL | Name | View | Portal |
|-----|------|------|--------|
| `/setup/` | `setup` | SetupView | Auth |
| `/setup/done/` | `setup_done` | SetupDoneView | Auth |
| `/login/` | `login` | LoginView | Auth |
| `/logout/` | `logout` | logout_view | Auth |
| `/admin/` | — | Django Admin | Admin |
| `/owner/` | `owner_dashboard` | OwnerDashboardView | Owner |
| `/owner/roster/` | `owner_roster` | OwnerRosterView | Owner |
| `/owner/performance/` | `team_performance` | TeamPerformanceView | Owner |
| `/owner/seasons/` | `season_list` | SeasonListView | Owner |
| `/owner/seasons/new/` | `season_create` | SeasonCreateView | Owner |
| `/owner/seasons/<pk>/edit/` | `season_update` | SeasonUpdateView | Owner |
| `/owner/seasons/<pk>/delete/` | `season_delete` | SeasonDeleteView | Owner |
| `/owner/expenses/` | `expense_list` | ExpenseListView | Owner |
| `/owner/expenses/<pk>/delete/` | `expense_delete` | ExpenseDeleteView | Owner |
| `/owner/transfers/` | `transfer_list` | TransferListView | Owner |
| `/coach/` | `coach_dashboard` | CoachDashboardView | Coach |
| `/coach/players/` | `coach_player_list` | CoachPlayerListView | Coach |
| `/coach/players/new/` | `coach_player_create` | CoachPlayerCreateView | Coach |
| `/coach/players/<pk>/` | `coach_player_detail` | CoachPlayerDetailView | Coach |
| `/coach/players/<pk>/edit/` | `coach_player_update` | CoachPlayerUpdateView | Coach |
| `/coach/players/<pk>/delete/` | `coach_player_delete` | CoachPlayerDeleteView | Coach |
| `/coach/players/<pk>/account/` | `coach_player_account` | CoachCreatePlayerAccountView | Coach |
| `/coach/matches/` | `match_list` | MatchListView | Coach |
| `/coach/matches/new/` | `match_create` | MatchCreateView | Coach |
| `/coach/matches/<pk>/edit/` | `match_update` | MatchUpdateView | Coach |
| `/coach/matches/<pk>/delete/` | `match_delete` | MatchDeleteView | Coach |
| `/coach/matches/<pk>/` | `match_detail` | MatchDetailView | Coach |
| `/coach/matches/<pk>/attendance/` | `match_attendance` | MatchAttendanceView | Coach |
| `/coach/matches/<pk>/stats/` | `match_stats` | MatchStatsView | Coach |
| `/coach/trainings/` | `training_list` | TrainingListView | Coach |
| `/coach/trainings/new/` | `training_create` | TrainingCreateView | Coach |
| `/coach/trainings/<pk>/edit/` | `training_update` | TrainingUpdateView | Coach |
| `/coach/trainings/<pk>/delete/` | `training_delete` | TrainingDeleteView | Coach |
| `/coach/trainings/<pk>/attendance/` | `training_attendance` | TrainingAttendanceView | Coach |
| `/coach/stats/` | `coach_season_stats` | CoachSeasonStatsView | Coach |
| `/player/` | `player_dashboard` | PlayerDashboardView | Player |
| `/player/calendar/` | `player_calendar` | PlayerCalendarView | Player |
| `/player/attendance/` | `player_attendance` | PlayerMyAttendanceView | Player |
| `/player/attendance/mark/` | `player_mark_attendance` | PlayerMarkAttendanceView | Player |
| `/player/stats/` | `player_stats` | PlayerMyStatsView | Player |

Total: **44 URL patterns**

---

## 9. Data Models Reference

### Season
| Field | Type | Notes |
|-------|------|-------|
| name | CharField(100) | e.g. "2025-26 Season" |
| start_date | DateField | |
| end_date | DateField | |
| is_active | BooleanField | Only one active at a time (enforced in save()) |

### ClubOwner
| Field | Type | Notes |
|-------|------|-------|
| user | OneToOneField(User) | |

### Coach
| Field | Type | Notes |
|-------|------|-------|
| user | OneToOneField(User) | |
| phone | CharField(20, blank) | |
| specialty | CharField(100, blank) | e.g. "Attack Coach" |

### Player
| Field | Type | Notes |
|-------|------|-------|
| user | OneToOneField(User, null) | Optional — set when coach creates account |
| name | CharField(100) | |
| position | CharField(choices) | Setter/Libero/Outside/Opposite/Middle/DS/Universal |
| salary | DecimalField | Monthly |
| date_joined | DateField | |
| contact_person | CharField | Emergency contact |
| jersey_number | PositiveSmallInt(null) | |
| phone | CharField(20, blank) | |
| birth_date | DateField(null) | |
| nationality | CharField(80, blank) | |
| height_cm | PositiveSmallInt(null) | |
| is_active | BooleanField | Soft-delete flag |

### Match
| Field | Type | Notes |
|-------|------|-------|
| season | ForeignKey(Season) | |
| date | DateTimeField | |
| opponent | CharField(100) | |
| venue | CharField(choices) | Home / Away / Neutral |
| match_type | CharField(choices) | League / Cup / Friendly / Tournament |
| sets_won | PositiveSmallInt(null) | Filled after the match |
| sets_lost | PositiveSmallInt(null) | |
| notes | TextField(blank) | |

Properties: `result` (Win/Loss/Draw/Upcoming), `score` ("3-1"), `is_upcoming` (bool), `result_badge` (Bootstrap colour class)

### Training
| Field | Type | Notes |
|-------|------|-------|
| season | ForeignKey(Season) | |
| date | DateTimeField | |
| location | CharField(150) | |
| description | TextField(blank) | |
| created_by | ForeignKey(Coach, null) | |

Property: `is_upcoming` (bool)

### Attendance
| Field | Type | Notes |
|-------|------|-------|
| player | ForeignKey(Player) | |
| match | ForeignKey(Match, null) | Either match or training is set |
| training | ForeignKey(Training, null) | |
| status | CharField(choices) | present / absent / excused / late |
| reason | CharField(200, blank) | Optional reason |

Property: `badge_color` (Bootstrap colour string)

### PlayerStatistic
| Field | Type | Notes |
|-------|------|-------|
| player | ForeignKey(Player) | |
| match | ForeignKey(Match) | |
| points | PositiveSmallInt | |
| kills | PositiveSmallInt | |
| aces | PositiveSmallInt | |
| blocks | PositiveSmallInt | |
| digs | PositiveSmallInt | |
| errors | PositiveSmallInt | |
| minutes_played | PositiveSmallInt | |
| rating | DecimalField(null) | 1-10 optional |

Constraint: `unique_together = ('player', 'match')`

### Transfer
| Field | Type | Notes |
|-------|------|-------|
| player | ForeignKey(Player) | |
| transfer_type | CharField(choices) | in / out / loan_in / loan_out |
| from_club | CharField(100, blank) | |
| to_club | CharField(100, blank) | |
| fee | DecimalField(null) | In USD |
| date | DateField | |
| season | ForeignKey(Season, null) | |

### Expense
| Field | Type | Notes |
|-------|------|-------|
| category | CharField(choices) | salary/equipment/travel/medical/facility/marketing/transfers/other |
| amount | DecimalField | |
| date | DateField | |
| description | CharField(200) | |
| season | ForeignKey(Season) | |

---

## 10. How to Create Users & Assign Roles

### Step 1 — Create the initial superuser (first run)
Visit `http://localhost:8000/` — you will be redirected to `/setup/` automatically.
Fill in username, optional email, and password (≥ 8 chars). Click **Create Superuser & Launch**.

### Step 2 — Log in as superuser
Go to `http://localhost:8000/login/` → you are taken to the **Owner Portal**.

### Step 3 — Access Django Admin
Navigate to `http://localhost:8000/admin/` and log in with your superuser credentials.

### Step 4 — Create the Owner / Coach groups (first time only)
Admin → Authentication → Groups → Add:
- Name: `Owner`
- Name: `Coach`
- Name: `Player`

### Step 5 — Create a Coach account
1. Admin → Users → Add User → set username + password → Save
2. On the user detail page, scroll to **Groups** → add `Coach`
3. Admin → Players → Coaches → Add Coach → select the user, fill phone/specialty

### Step 6 — Create Player accounts (two ways)
**Option A — Via Coach Portal (recommended):**
1. Coach logs in → Players → Add Player → fill player info
2. Coach → Player detail → "Create Account" → set username & password
   (Automatically adds to `Player` group and links user ↔ player)

**Option B — Via Django Admin:**
1. Admin → Users → Add User
2. Add to `Player` group
3. Admin → Players → Players → find the player → set the `user` field

### Step 7 — Create an Owner account (optional, for non-superuser owner)
1. Admin → Users → Add User → set credentials
2. Add to `Owner` group
3. Admin → Players → Club Owners → Add Club Owner → select the user

---

## 11. Docker & Deployment

### Run locally (no Docker)
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
Visit `http://localhost:8000/`

### Run with Docker (local build)
```bash
docker build -t volley-manager .
docker run --name volleyball-app -p 8000:8000 volley-manager
```

### Run from GitHub Container Registry
```bash
docker pull ghcr.io/philippedoumet/eece430sp25-26group20:latest
docker run --name volleyball-app -p 8000:8000 ghcr.io/philippedoumet/eece430sp25-26group20:latest
```

The container automatically runs `python manage.py migrate` on startup, so a fresh database is always ready.

---

## 12. Implemented Features Summary

### Authentication & Setup
- [x] First-run superuser wizard (`/setup/`) — auto-shown when DB is empty
- [x] Login page with role-based redirect
- [x] Logout
- [x] Role guard mixins (`OwnerRequiredMixin`, `CoachRequiredMixin`, `PlayerRequiredMixin`)
- [x] Auto-redirect authenticated users to their portal

### Season Management (Owner)
- [x] Create / Edit / Delete seasons
- [x] Only one active season at a time (enforced in model `save()`)
- [x] All stats and events are scoped to the active season

### Owner Portal
- [x] Dashboard with KPI cards (players, matches, win rate, trainings)
- [x] Recent match results and upcoming fixtures
- [x] Full player roster view
- [x] Team performance page (match history, win/loss record, top scorers)
- [x] Expense tracker (list + delete, by category with totals)
- [x] Transfer log (in/out/loan, with fee tracking)

### Coach Portal — Player Management
- [x] Full CRUD for players (Create, Read, Update, Delete)
- [x] Player detail page with bio, salary, stats, attendance history
- [x] Create Django User account for a player (sets username/password, assigns group, links model)
- [x] "Has Account" indicator on player list

### Coach Portal — Schedule Management
- [x] Full CRUD for matches (with venue, type, score entry)
- [x] Match detail page (attendance summary + stats table)
- [x] Full CRUD for training sessions
- [x] Bulk match attendance recording (all players on one form)
- [x] Bulk training attendance recording
- [x] Bulk match statistics entry (points/kills/aces/blocks/digs/errors/mins/rating)

### Coach Portal — Reporting
- [x] Season statistics table (all players, sortable by column)
- [x] Attendance colour-coded badges (green/yellow/red thresholds)

### Player Portal
- [x] Personal dashboard (stat cards, upcoming events, recent team results, profile card)
- [x] Calendar of upcoming matches and trainings
- [x] Self-report attendance for matches and trainings (Present / Absent buttons)
- [x] Attendance history (matches + trainings with status badges)
- [x] Overall attendance rate displayed
- [x] Personal season statistics (totals + per-match breakdown)

### Infrastructure & Deployment
- [x] Docker image (`python:3.12-slim`, auto-migrate on start)
- [x] Docker image published to GHCR: `ghcr.io/philippedoumet/eece430sp25-26group20:latest`
- [x] GitHub repository with full source code
- [x] `.gitignore` and `.dockerignore`
- [x] `requirements.txt`
- [x] `README.md` with run instructions

### UI / UX
- [x] Bootstrap 5 + Font Awesome 6 (CDN, no install required)
- [x] Three distinct portal colour schemes (navy, green, purple)
- [x] Sticky sidebar navigation on all portals
- [x] Responsive grid layout (Bootstrap breakpoints)
- [x] Flash messages for CRUD operations
- [x] Colour-coded badges (result: Win/Loss/Draw; attendance: present/absent/excused/late)
- [x] Empty-state placeholders on all tables
- [x] "No active season" alerts guiding the owner to create one

---

*Generated: April 2026 · Philippe Doumet · EECE 430*
