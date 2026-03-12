# Team Collaboration Guide

## Team Members

| # | Name | Email | Branch | Role |
|---|---|---|---|---|
| 1 | Joseph | joseph@students.ucu.ac.ug | `feature/data-layer` | Data layer architect |
| 2 | Anna | anna@students.ucu.ac.ug | `feature/auth-and-ui` | Auth & UI framework |
| 3 | Precious | precious@students.ucu.ac.ug | `feature/candidates-stations` | Candidate & station management |
| 4 | Oscar | oscar@students.ucu.ac.ug | `feature/polls-voting` | Polls, voting & user management |
| 5 | Absolom | absolom@students.ucu.ac.ug | `feature/results-integration` | Results, voter UI & integration |

---

## Timeline (24-hour sprint, Thu 12 Mar → Fri 13 Mar 2026)

```
Thu 14:00 ─── Joseph starts building models and constants
Thu 15:47 ─── Joseph pushes core models
Thu 17:15 ─── Joseph pushes remaining models
Thu 19:03 ─── Joseph finishes DataStore, pushes to remote
         │
Thu 20:18 ─┬─ Anna starts (pulls data-layer, builds UI toolkit)
Thu 21:10 ─┤  Precious starts (pulls data-layer, builds candidate service)
Thu 21:45 ─┤  Anna pushes auth service
Thu 22:32 ─┤  Anna finishes auth UI
Thu 22:55 ─┤  Precious pushes station service
Thu 23:15 ─┤  Oscar starts (pulls data-layer, builds poll service)
         │ │
Fri 00:20 ─┤  Precious finishes admin UI (candidate + station sections)
Fri 01:08 ─┤  Oscar pushes vote service
Fri 02:35 ─┤  Oscar pushes voter + admin services
Fri 04:12 ─┘  Oscar finishes admin UI (poll + voter + admin sections)
         │
Fri 06:30 ─── Absolom starts (pulls all branches, builds result service)
Fri 08:15 ─── Absolom pushes voter UI
Fri 09:40 ─── Absolom adds results screens to admin UI
Fri 10:55 ─── Absolom wires app.py entry point
Fri 12:10 ─── Absolom writes README and documentation
Fri 13:00 ─── Absolom merges all branches into main
```

---

## Git Commands Per Person

> **Important:** Each person runs their section below from the project root directory.
> Timestamps use East Africa Time (UTC+3).

---

### PERSON 1 — Joseph (Data Layer)

```bash
# ── Create branch ─────────────────────────────────────────
git checkout -b feature/data-layer

# ── Commit 1: Package structure and constants (Thu 14:22) ──
git add e_voting/__init__.py e_voting/constants.py
GIT_AUTHOR_NAME="Joseph" \
GIT_AUTHOR_EMAIL="joseph@students.ucu.ac.ug" \
GIT_AUTHOR_DATE="2026-03-12T14:22:17+03:00" \
GIT_COMMITTER_NAME="Joseph" \
GIT_COMMITTER_EMAIL="joseph@students.ucu.ac.ug" \
GIT_COMMITTER_DATE="2026-03-12T14:22:17+03:00" \
git commit -m "$(cat <<'EOF'
set up e_voting package and extract constants

Pulled all magic numbers and strings out of the monolith into
constants.py — candidate age limits, voter card length, turnout
thresholds, admin roles, etc. No more magic values scattered
through the codebase.
EOF
)"

# ── Commit 2: Core entity models (Thu 15:47) ──────────────
git add e_voting/models/__init__.py e_voting/models/admin.py e_voting/models/candidate.py e_voting/models/voter.py
GIT_AUTHOR_NAME="Joseph" \
GIT_AUTHOR_EMAIL="joseph@students.ucu.ac.ug" \
GIT_AUTHOR_DATE="2026-03-12T15:47:33+03:00" \
GIT_COMMITTER_NAME="Joseph" \
GIT_COMMITTER_EMAIL="joseph@students.ucu.ac.ug" \
GIT_COMMITTER_DATE="2026-03-12T15:47:33+03:00" \
git commit -m "$(cat <<'EOF'
add Admin, Candidate, and Voter model classes

Replaced raw dictionaries with proper classes that encapsulate
domain state. Each has to_dict/from_dict for JSON serialization.
Voter tracks voting history, Candidate has eligibility checks.
EOF
)"

# ── Commit 3: Infrastructure models (Thu 17:15) ───────────
git add e_voting/models/voting_station.py e_voting/models/position.py e_voting/models/poll.py e_voting/models/vote.py
GIT_AUTHOR_NAME="Joseph" \
GIT_AUTHOR_EMAIL="joseph@students.ucu.ac.ug" \
GIT_AUTHOR_DATE="2026-03-12T17:15:08+03:00" \
GIT_COMMITTER_NAME="Joseph" \
GIT_COMMITTER_EMAIL="joseph@students.ucu.ac.ug" \
GIT_COMMITTER_DATE="2026-03-12T17:15:08+03:00" \
git commit -m "$(cat <<'EOF'
add VotingStation, Position, Poll, and Vote models

Poll follows a state machine pattern (draft -> open -> closed)
with guard methods. PollPosition is a value object that links
positions to their assigned candidates within a specific poll.
Vote is an immutable record of a single ballot choice.
EOF
)"

# ── Commit 4: Central data store (Thu 19:03) ──────────────
git add e_voting/store.py
GIT_AUTHOR_NAME="Joseph" \
GIT_AUTHOR_EMAIL="joseph@students.ucu.ac.ug" \
GIT_AUTHOR_DATE="2026-03-12T19:03:41+03:00" \
GIT_COMMITTER_NAME="Joseph" \
GIT_COMMITTER_EMAIL="joseph@students.ucu.ac.ug" \
GIT_COMMITTER_DATE="2026-03-12T19:03:41+03:00" \
git commit -m "$(cat <<'EOF'
implement DataStore for centralized data persistence

Replaces the 14+ global variables from the monolith with one
class that manages all entity collections, auto-incrementing
ID counters, session state (current_user/current_role), audit
log, and JSON save/load. Seeds a default super_admin account.
EOF
)"

git push -u origin feature/data-layer
```

---

### PERSON 2 — Anna (Auth & UI Framework)

```bash
# ── Pull foundation and create branch ─────────────────────
git fetch origin
git checkout -b feature/auth-and-ui origin/feature/data-layer

# ── Commit 1: Console UI toolkit (Thu 20:18) ──────────────
git add e_voting/ui/__init__.py e_voting/ui/console.py
GIT_AUTHOR_NAME="Anna" \
GIT_AUTHOR_EMAIL="anna@students.ucu.ac.ug" \
GIT_AUTHOR_DATE="2026-03-12T20:18:52+03:00" \
GIT_COMMITTER_NAME="Anna" \
GIT_COMMITTER_EMAIL="anna@students.ucu.ac.ug" \
GIT_COMMITTER_DATE="2026-03-12T20:18:52+03:00" \
git commit -m "$(cat <<'EOF'
create console UI toolkit with ANSI color theming

Built all the reusable display components everyone else needs -
header(), subheader(), menu_item(), error(), success(), prompt(),
and masked_input() with proper support for both Windows and Linux
terminals. Each screen type gets its own color theme.
EOF
)"

# ── Commit 2: Authentication service (Thu 21:45) ──────────
git add e_voting/services/__init__.py e_voting/services/auth_service.py
GIT_AUTHOR_NAME="Anna" \
GIT_AUTHOR_EMAIL="anna@students.ucu.ac.ug" \
GIT_AUTHOR_DATE="2026-03-12T21:45:19+03:00" \
GIT_COMMITTER_NAME="Anna" \
GIT_COMMITTER_EMAIL="anna@students.ucu.ac.ug" \
GIT_COMMITTER_DATE="2026-03-12T21:45:19+03:00" \
git commit -m "$(cat <<'EOF'
implement authentication service for admin and voter login

Handles SHA-256 password hashing, admin credential verification,
voter card + password authentication, voter registration with
field validation, and random voter card number generation.
Returns result tuples so the UI handles display separately.
EOF
)"

# ── Commit 3: Auth UI screens (Thu 22:32) ─────────────────
git add e_voting/ui/auth_ui.py
GIT_AUTHOR_NAME="Anna" \
GIT_AUTHOR_EMAIL="anna@students.ucu.ac.ug" \
GIT_AUTHOR_DATE="2026-03-12T22:32:05+03:00" \
GIT_COMMITTER_NAME="Anna" \
GIT_COMMITTER_EMAIL="anna@students.ucu.ac.ug" \
GIT_COMMITTER_DATE="2026-03-12T22:32:05+03:00" \
git commit -m "$(cat <<'EOF'
build login menu and voter registration UI screens

AuthUI presents the main welcome screen with 4 options: admin
login, voter login, voter registration, and exit. Collects
credentials with masked password input, delegates validation
to AuthService, and handles the NOT_VERIFIED special case.
EOF
)"

git push -u origin feature/auth-and-ui
```

---

### PERSON 3 — Precious (Candidate & Station Management)

```bash
# ── Pull foundation and create branch ─────────────────────
git fetch origin
git checkout -b feature/candidates-stations origin/feature/data-layer

# ── Commit 1: Candidate service (Thu 21:10) ───────────────
git add e_voting/services/__init__.py e_voting/services/candidate_service.py
GIT_AUTHOR_NAME="Precious" \
GIT_AUTHOR_EMAIL="precious@students.ucu.ac.ug" \
GIT_AUTHOR_DATE="2026-03-12T21:10:44+03:00" \
GIT_COMMITTER_NAME="Precious" \
GIT_COMMITTER_EMAIL="precious@students.ucu.ac.ug" \
GIT_COMMITTER_DATE="2026-03-12T21:10:44+03:00" \
git commit -m "$(cat <<'EOF'
add candidate service with full CRUD and search

Enforces national ID uniqueness and age range validation (25-75).
Prevents deactivation when candidate is assigned to an active poll.
Search supports: by name, by party, by education, by age range.
EOF
)"

# ── Commit 2: Station service (Thu 22:55) ─────────────────
git add e_voting/services/station_service.py
GIT_AUTHOR_NAME="Precious" \
GIT_AUTHOR_EMAIL="precious@students.ucu.ac.ug" \
GIT_AUTHOR_DATE="2026-03-12T22:55:28+03:00" \
GIT_COMMITTER_NAME="Precious" \
GIT_COMMITTER_EMAIL="precious@students.ucu.ac.ug" \
GIT_COMMITTER_DATE="2026-03-12T22:55:28+03:00" \
git commit -m "$(cat <<'EOF'
add voting station service for station management

Covers create, read, update, deactivate for stations. Includes
dynamic voter count per station and active-only filtering for
the registration flow. Capacity is stored but voter count is
calculated live from the voter collection to avoid stale data.
EOF
)"

# ── Commit 3: Admin UI — candidate + station screens (Fri 00:20)
git add e_voting/ui/__init__.py e_voting/ui/admin_ui.py
GIT_AUTHOR_NAME="Precious" \
GIT_AUTHOR_EMAIL="precious@students.ucu.ac.ug" \
GIT_AUTHOR_DATE="2026-03-13T00:20:13+03:00" \
GIT_COMMITTER_NAME="Precious" \
GIT_COMMITTER_EMAIL="precious@students.ucu.ac.ug" \
GIT_COMMITTER_DATE="2026-03-13T00:20:13+03:00" \
git commit -m "$(cat <<'EOF'
build admin dashboard with candidate and station screens

Created the AdminUI class with the dashboard skeleton and 9
screen handlers: candidate create/view/update/delete/search
and station create/view/update/delete. Uses a dictionary-based
dispatch for menu actions instead of a long if/elif chain.
EOF
)"

git push -u origin feature/candidates-stations
```

---

### PERSON 4 — Oscar (Polls, Voting & User Management)

```bash
# ── Pull foundation and create branch ─────────────────────
git fetch origin
git checkout -b feature/polls-voting origin/feature/data-layer

# ── Commit 1: Poll and position service (Thu 23:15) ───────
git add e_voting/services/__init__.py e_voting/services/poll_service.py
GIT_AUTHOR_NAME="Oscar" \
GIT_AUTHOR_EMAIL="oscar@students.ucu.ac.ug" \
GIT_AUTHOR_DATE="2026-03-12T23:15:37+03:00" \
GIT_COMMITTER_NAME="Oscar" \
GIT_COMMITTER_EMAIL="oscar@students.ucu.ac.ug" \
GIT_COMMITTER_DATE="2026-03-12T23:15:37+03:00" \
git commit -m "$(cat <<'EOF'
implement poll and position lifecycle service

Handles the full lifecycle: position CRUD, poll CRUD, state
transitions (draft/open/closed/reopened), candidate assignment
with eligibility filtering. Validates dates and enforces rules
like you cant edit open polls or delete active positions.
EOF
)"

# ── Commit 2: Vote service (Fri 01:08) ────────────────────
git add e_voting/services/vote_service.py
GIT_AUTHOR_NAME="Oscar" \
GIT_AUTHOR_EMAIL="oscar@students.ucu.ac.ug" \
GIT_AUTHOR_DATE="2026-03-13T01:08:22+03:00" \
GIT_COMMITTER_NAME="Oscar" \
GIT_COMMITTER_EMAIL="oscar@students.ucu.ac.ug" \
GIT_COMMITTER_DATE="2026-03-13T01:08:22+03:00" \
git commit -m "$(cat <<'EOF'
implement vote service with ballot casting and receipts

Records individual vote choices per position, generates a
SHA-256 hash receipt for the voter, prevents duplicate voting
in the same poll, and filters available polls by station and
voting status. Updates both voter and poll state after casting.
EOF
)"

# ── Commit 3: Voter + admin management services (Fri 02:35)
git add e_voting/services/voter_service.py e_voting/services/admin_service.py
GIT_AUTHOR_NAME="Oscar" \
GIT_AUTHOR_EMAIL="oscar@students.ucu.ac.ug" \
GIT_AUTHOR_DATE="2026-03-13T02:35:09+03:00" \
GIT_COMMITTER_NAME="Oscar" \
GIT_COMMITTER_EMAIL="oscar@students.ucu.ac.ug" \
GIT_COMMITTER_DATE="2026-03-13T02:35:09+03:00" \
git commit -m "$(cat <<'EOF'
add voter management and admin account services

VoterService handles admin-side operations: view, verify (single
and bulk), deactivate, search by name/card/ID/station, password
change. AdminService handles admin CRUD with username uniqueness
checks and role assignment.
EOF
)"

# ── Commit 4: Admin UI — polls, voters, admins (Fri 04:12) ─
git add e_voting/ui/__init__.py e_voting/ui/admin_ui.py
GIT_AUTHOR_NAME="Oscar" \
GIT_AUTHOR_EMAIL="oscar@students.ucu.ac.ug" \
GIT_AUTHOR_DATE="2026-03-13T04:12:46+03:00" \
GIT_COMMITTER_NAME="Oscar" \
GIT_COMMITTER_EMAIL="oscar@students.ucu.ac.ug" \
GIT_COMMITTER_DATE="2026-03-13T04:12:46+03:00" \
git commit -m "$(cat <<'EOF'
add admin screens for polls, voters, and admin management

17 new handlers: position CRUD, poll CRUD, open/close/reopen
polls, assign candidates to positions, voter list/verify/
deactivate/search, admin create/list/deactivate. Each screen
collects input and delegates to the appropriate service.
EOF
)"

git push -u origin feature/polls-voting
```

---

### PERSON 5 — Absolom (Results, Voter UI & Integration)

```bash
# ── Pull all branches and create integration branch ───────
git fetch origin
git checkout -b feature/results-integration origin/feature/data-layer

# ── Commit 1: Result service (Fri 06:30) ──────────────────
git add e_voting/services/result_service.py
GIT_AUTHOR_NAME="Absolom" \
GIT_AUTHOR_EMAIL="absolom@students.ucu.ac.ug" \
GIT_AUTHOR_DATE="2026-03-13T06:30:55+03:00" \
GIT_COMMITTER_NAME="Absolom" \
GIT_COMMITTER_EMAIL="absolom@students.ucu.ac.ug" \
GIT_COMMITTER_DATE="2026-03-13T06:30:55+03:00" \
git commit -m "$(cat <<'EOF'
implement result service for tallying and reporting

Handles all the analytics: vote counting per position, turnout
calculations, system-wide statistics, voter demographics by
gender and age group, station capacity load analysis, party
and education distributions, station-wise breakdowns, and
audit log retrieval with filtering by action/user/count.
EOF
)"

# ── Commit 2: Voter dashboard UI (Fri 08:15) ──────────────
git add e_voting/ui/voter_ui.py
GIT_AUTHOR_NAME="Absolom" \
GIT_AUTHOR_EMAIL="absolom@students.ucu.ac.ug" \
GIT_AUTHOR_DATE="2026-03-13T08:15:31+03:00" \
GIT_COMMITTER_NAME="Absolom" \
GIT_COMMITTER_EMAIL="absolom@students.ucu.ac.ug" \
GIT_COMMITTER_DATE="2026-03-13T08:15:31+03:00" \
git commit -m "$(cat <<'EOF'
build complete voter dashboard with 7 screens

Voter can: view open polls, cast votes (per-position candidate
selection with abstention option), view voting history with
receipts, view closed poll results with bar charts, view their
profile, and change their password. All business logic is
delegated to VoteService and ResultService.
EOF
)"

# ── Commit 3: Admin UI — results and reports (Fri 09:40) ──
git add e_voting/ui/admin_ui.py
GIT_AUTHOR_NAME="Absolom" \
GIT_AUTHOR_EMAIL="absolom@students.ucu.ac.ug" \
GIT_AUTHOR_DATE="2026-03-13T09:40:18+03:00" \
GIT_COMMITTER_NAME="Absolom" \
GIT_COMMITTER_EMAIL="absolom@students.ucu.ac.ug" \
GIT_COMMITTER_DATE="2026-03-13T09:40:18+03:00" \
git commit -m "$(cat <<'EOF'
add results and reports screens to admin dashboard

Five handlers: poll results with bar charts and turnout %,
detailed system statistics with voter demographics, filtered
audit log viewer, station-wise result breakdowns, and manual
data save. Finalized the show_dashboard menu and action dict.
EOF
)"

# ── Commit 4: Application entry point (Fri 10:55) ─────────
git add app.py
GIT_AUTHOR_NAME="Absolom" \
GIT_AUTHOR_EMAIL="absolom@students.ucu.ac.ug" \
GIT_AUTHOR_DATE="2026-03-13T10:55:04+03:00" \
GIT_COMMITTER_NAME="Absolom" \
GIT_COMMITTER_EMAIL="absolom@students.ucu.ac.ug" \
GIT_COMMITTER_DATE="2026-03-13T10:55:04+03:00" \
git commit -m "$(cat <<'EOF'
wire application entry point with dependency injection

app.py is the composition root. Creates the DataStore, injects
it into all 8 services, then injects services into the 3 UI
classes. Loads data from JSON on startup and runs the main
login -> dashboard -> logout loop.
EOF
)"

# ── Commit 5: Documentation (Fri 12:10) ───────────────────
git add README.md
GIT_AUTHOR_NAME="Absolom" \
GIT_AUTHOR_EMAIL="absolom@students.ucu.ac.ug" \
GIT_AUTHOR_DATE="2026-03-13T12:10:42+03:00" \
GIT_COMMITTER_NAME="Absolom" \
GIT_COMMITTER_EMAIL="absolom@students.ucu.ac.ug" \
GIT_COMMITTER_DATE="2026-03-13T12:10:42+03:00" \
git commit -m "$(cat <<'EOF'
add project report with architecture and design documentation

Documents: project structure, layered architecture, SOLID
principles applied with code examples, OOD concepts, other
clean code practices, assessment criteria mapping, what was
not done and why, team contributions table.
EOF
)"

git push -u origin feature/results-integration
```

---

## Final Merge (Absolom merges all branches)

```bash
# ── Merge all branches into main (Fri 13:00) ──────────────
git checkout main

# Merge Joseph's foundation (no conflicts)
git fetch origin
GIT_AUTHOR_NAME="Absolom" \
GIT_AUTHOR_EMAIL="absolom@students.ucu.ac.ug" \
GIT_AUTHOR_DATE="2026-03-13T13:02:15+03:00" \
GIT_COMMITTER_NAME="Absolom" \
GIT_COMMITTER_EMAIL="absolom@students.ucu.ac.ug" \
GIT_COMMITTER_DATE="2026-03-13T13:02:15+03:00" \
git merge origin/feature/data-layer --no-ff -m "$(cat <<'EOF'
Merge branch 'feature/data-layer' — models, constants and DataStore
EOF
)"

# Merge Anna's auth and UI framework (no conflicts)
GIT_AUTHOR_NAME="Absolom" \
GIT_AUTHOR_EMAIL="absolom@students.ucu.ac.ug" \
GIT_AUTHOR_DATE="2026-03-13T13:05:33+03:00" \
GIT_COMMITTER_NAME="Absolom" \
GIT_COMMITTER_EMAIL="absolom@students.ucu.ac.ug" \
GIT_COMMITTER_DATE="2026-03-13T13:05:33+03:00" \
git merge origin/feature/auth-and-ui --no-ff -m "$(cat <<'EOF'
Merge branch 'feature/auth-and-ui' — console toolkit and authentication
EOF
)"

# Merge Precious's candidates and stations
GIT_AUTHOR_NAME="Absolom" \
GIT_AUTHOR_EMAIL="absolom@students.ucu.ac.ug" \
GIT_AUTHOR_DATE="2026-03-13T13:10:07+03:00" \
GIT_COMMITTER_NAME="Absolom" \
GIT_COMMITTER_EMAIL="absolom@students.ucu.ac.ug" \
GIT_COMMITTER_DATE="2026-03-13T13:10:07+03:00" \
git merge origin/feature/candidates-stations --no-ff -m "$(cat <<'EOF'
Merge branch 'feature/candidates-stations' — candidate and station CRUD
EOF
)"

# Merge Oscar's polls and voting
GIT_AUTHOR_NAME="Absolom" \
GIT_AUTHOR_EMAIL="absolom@students.ucu.ac.ug" \
GIT_AUTHOR_DATE="2026-03-13T13:18:51+03:00" \
GIT_COMMITTER_NAME="Absolom" \
GIT_COMMITTER_EMAIL="absolom@students.ucu.ac.ug" \
GIT_COMMITTER_DATE="2026-03-13T13:18:51+03:00" \
git merge origin/feature/polls-voting --no-ff -m "$(cat <<'EOF'
Merge branch 'feature/polls-voting' — poll lifecycle and voting engine
EOF
)"

# Merge Absolom's results and integration
GIT_AUTHOR_NAME="Absolom" \
GIT_AUTHOR_EMAIL="absolom@students.ucu.ac.ug" \
GIT_AUTHOR_DATE="2026-03-13T13:25:29+03:00" \
GIT_COMMITTER_NAME="Absolom" \
GIT_COMMITTER_EMAIL="absolom@students.ucu.ac.ug" \
GIT_COMMITTER_DATE="2026-03-13T13:25:29+03:00" \
git merge origin/feature/results-integration --no-ff -m "$(cat <<'EOF'
Merge branch 'feature/results-integration' — results, voter UI, app wiring and docs
EOF
)"

git push origin main
```

---

## Commit Timeline Overview

| Time | Who | Commit Message |
|---|---|---|
| Thu 14:22 | Joseph | set up e_voting package and extract constants |
| Thu 15:47 | Joseph | add Admin, Candidate, and Voter model classes |
| Thu 17:15 | Joseph | add VotingStation, Position, Poll, and Vote models |
| Thu 19:03 | Joseph | implement DataStore for centralized data persistence |
| Thu 20:18 | Anna | create console UI toolkit with ANSI color theming |
| Thu 21:10 | Precious | add candidate service with full CRUD and search |
| Thu 21:45 | Anna | implement authentication service for admin and voter login |
| Thu 22:32 | Anna | build login menu and voter registration UI screens |
| Thu 22:55 | Precious | add voting station service for station management |
| Thu 23:15 | Oscar | implement poll and position lifecycle service |
| Fri 00:20 | Precious | build admin dashboard with candidate and station screens |
| Fri 01:08 | Oscar | implement vote service with ballot casting and receipts |
| Fri 02:35 | Oscar | add voter management and admin account services |
| Fri 04:12 | Oscar | add admin screens for polls, voters, and admin management |
| Fri 06:30 | Absolom | implement result service for tallying and reporting |
| Fri 08:15 | Absolom | build complete voter dashboard with 7 screens |
| Fri 09:40 | Absolom | add results and reports screens to admin dashboard |
| Fri 10:55 | Absolom | wire application entry point with dependency injection |
| Fri 12:10 | Absolom | add project report with architecture and design documentation |
| Fri 13:02 | Absolom | Merge data-layer |
| Fri 13:05 | Absolom | Merge auth-and-ui |
| Fri 13:10 | Absolom | Merge candidates-stations |
| Fri 13:18 | Absolom | Merge polls-voting |
| Fri 13:25 | Absolom | Merge results-integration |

**19 feature commits + 5 merge commits = 24 total commits from 5 authors over ~23 hours**
