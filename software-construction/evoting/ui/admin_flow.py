from __future__ import annotations

from evoting.services.admin_service import AdminService
from evoting.services.candidate_service import CandidateService
from evoting.services.poll_service import PollService
from evoting.services.position_service import PositionService
from evoting.services.results_service import ResultsService
from evoting.services.station_service import StationService
from evoting.services.voter_service import VoterService
from evoting.ui import themes
from evoting.ui.console import Console


class AdminFlow:
    def __init__(
        self,
        console: Console,
        state,
        candidate_service: CandidateService,
        station_service: StationService,
        position_service: PositionService,
        poll_service: PollService,
        voter_service: VoterService,
        admin_service: AdminService,
        results_service: ResultsService,
        save_callback,
        logout_callback,
    ) -> None:
        self.console = console
        self.state = state
        self.save_callback = save_callback
        self.logout_callback = logout_callback
        self.sections = [
            (
                "Candidate Management",
                [
                    ("1", "Create Candidate", candidate_service.create_candidate),
                    ("2", "View All Candidates", candidate_service.view_all_candidates),
                    ("3", "Update Candidate", candidate_service.update_candidate),
                    ("4", "Delete Candidate", candidate_service.delete_candidate),
                    ("5", "Search Candidates", candidate_service.search_candidates),
                ],
            ),
            (
                "Voting Station Management",
                [
                    ("6", "Create Voting Station", station_service.create_voting_station),
                    ("7", "View All Stations", station_service.view_all_stations),
                    ("8", "Update Station", station_service.update_station),
                    ("9", "Delete Station", station_service.delete_station),
                ],
            ),
            (
                "Polls & Positions",
                [
                    ("10", "Create Position", position_service.create_position),
                    ("11", "View Positions", position_service.view_positions),
                    ("12", "Update Position", position_service.update_position),
                    ("13", "Delete Position", position_service.delete_position),
                    ("14", "Create Poll", poll_service.create_poll),
                    ("15", "View All Polls", poll_service.view_all_polls),
                    ("16", "Update Poll", poll_service.update_poll),
                    ("17", "Delete Poll", poll_service.delete_poll),
                    ("18", "Open/Close Poll", poll_service.open_close_poll),
                    ("19", "Assign Candidates to Poll", poll_service.assign_candidates_to_poll),
                ],
            ),
            (
                "Voter Management",
                [
                    ("20", "View All Voters", voter_service.view_all_voters),
                    ("21", "Verify Voter", voter_service.verify_voter),
                    ("22", "Deactivate Voter", voter_service.deactivate_voter),
                    ("23", "Search Voters", voter_service.search_voters),
                ],
            ),
            (
                "Admin Management",
                [
                    ("24", "Create Admin Account", admin_service.create_admin),
                    ("25", "View Admins", admin_service.view_admins),
                    ("26", "Deactivate Admin", admin_service.deactivate_admin),
                ],
            ),
            (
                "Results & Reports",
                [
                    ("27", "View Poll Results", results_service.view_poll_results),
                    ("28", "View Detailed Statistics", results_service.view_detailed_statistics),
                    ("29", "View Audit Log", results_service.view_audit_log),
                    ("30", "Station-wise Results", results_service.station_wise_results),
                ],
            ),
            (
                "System",
                [
                    ("31", "Save Data", self._save_data),
                    ("32", "Logout", self._logout),
                ],
            ),
        ]
        self.handlers = {
            option: handler
            for _, actions in self.sections
            for option, _, handler in actions
        }

    def _save_data(self) -> None:
        self.save_callback()
        self.console.pause()

    def _logout(self) -> None:
        self.logout_callback()
        raise StopIteration

    def run(self) -> None:
        while True:
            try:
                self._render_dashboard()
                choice = self.console.prompt("Enter choice: ")
                handler = self.handlers.get(choice)
                if handler is None:
                    self.console.error("Invalid choice.")
                    self.console.pause()
                    continue
                handler()
            except StopIteration:
                break

    def _render_dashboard(self) -> None:
        self.console.clear_screen()
        self.console.header("ADMIN DASHBOARD", themes.THEME_ADMIN)
        print(
            f"  {themes.THEME_ADMIN}  ● {themes.RESET}{themes.BOLD}{self.state.current_user['full_name']}"
            f"{themes.RESET}  {themes.DIM}│  Role: {self.state.current_user['role']}{themes.RESET}"
        )
        for title, actions in self.sections:
            self.console.subheader(title, themes.THEME_ADMIN_ACCENT)
            for option, label, _ in actions:
                self.console.menu_item(int(option), label, themes.THEME_ADMIN)
        print()
