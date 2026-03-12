from __future__ import annotations

from evoting.services.auth_service import AuthService
from evoting.services.results_service import ResultsService
from evoting.services.voting_service import VotingService
from evoting.ui import themes
from evoting.ui.console import Console


class VoterFlow:
    def __init__(
        self,
        console: Console,
        state,
        voting_service: VotingService,
        auth_service: AuthService,
        results_service: ResultsService,
        logout_callback,
    ) -> None:
        self.console = console
        self.state = state
        self.logout_callback = logout_callback
        self.actions = [
            ("1", "View Open Polls", voting_service.view_open_polls_voter),
            ("2", "Cast Vote", voting_service.cast_vote),
            ("3", "View My Voting History", voting_service.view_voting_history),
            ("4", "View Results (Closed Polls)", results_service.view_closed_poll_results_voter),
            ("5", "View My Profile", voting_service.view_voter_profile),
            ("6", "Change Password", auth_service.change_voter_password),
            ("7", "Logout", self._logout),
        ]
        self.handlers = {option: handler for option, _, handler in self.actions}

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
        current_user = self.state.current_user
        station_name = self.state.voting_stations.get(current_user["station_id"], {}).get(
            "name",
            "Unknown",
        )
        self.console.clear_screen()
        self.console.header("VOTER DASHBOARD", themes.THEME_VOTER)
        print(f"  {themes.THEME_VOTER}  ● {themes.RESET}{themes.BOLD}{current_user['full_name']}{themes.RESET}")
        print(
            f"  {themes.DIM}    Card: {current_user['voter_card_number']}  │  Station: "
            f"{station_name}{themes.RESET}"
        )
        print()
        for option, label, _ in self.actions:
            self.console.menu_item(int(option), label, themes.THEME_VOTER)
        print()
