## 5-Person GitHub Split

### Person 1: Core architecture and state
- Create the `evoting/` package skeleton.
- Own `evoting/domain/state.py`, `evoting/domain/constants.py`, and `evoting/main.py`.
- Keep the application boot sequence and shared state stable for everyone else.
- Suggested branch: `refactor/core-state`
- Suggested commit: `refactor core application state into modular package`

### Person 2: UI and menu flows
- Own `evoting/ui/themes.py`, `evoting/ui/console.py`, `evoting/ui/login_flow.py`, `evoting/ui/admin_flow.py`, and `evoting/ui/voter_flow.py`.
- Focus on presentation concerns, prompt helpers, and dispatch-based dashboards.
- Suggested branch: `refactor/ui-flows`
- Suggested commit: `extract cli presentation and menu flows`

### Person 3: Authentication and account management
- Own `evoting/services/auth_service.py`, `evoting/services/admin_service.py`, and `evoting/services/voter_service.py`.
- Focus on login, voter registration, password changes, admin creation, and voter verification/deactivation.
- Suggested branch: `refactor/auth-accounts`
- Suggested commit: `modularize authentication and account management`

### Person 4: Election domain services
- Own `evoting/services/candidate_service.py`, `evoting/services/station_service.py`, `evoting/services/position_service.py`, and `evoting/services/poll_service.py`.
- Focus on CRUD flows, poll lifecycle rules, and candidate assignment.
- Suggested branch: `refactor/election-services`
- Suggested commit: `extract election management services and validations`

### Person 5: Persistence, reporting, and tests
- Own `evoting/repository/storage.py`, `evoting/services/audit_service.py`, `evoting/services/results_service.py`, and `tests/`.
- Focus on storage safety, shared tally logic, audit behavior, and regression coverage.
- Suggested branch: `refactor/results-storage-tests`
- Suggested commit: `centralize reporting persistence and defensive error handling`

## Merge Order
1. Merge Person 1 first so the package layout and shared state are stable.
2. Merge Person 2 next so the new entrypoints and menu dispatch are available.
3. Merge Person 3 and Person 4 after that; these can proceed mostly in parallel.
4. Merge Person 5 last, because reporting and persistence depend on the service boundaries being in place.
