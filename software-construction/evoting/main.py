from __future__ import annotations

import time
from pathlib import Path

from evoting.domain.state import SystemState
from evoting.repository.storage import JsonStorageRepository, StorageError
from evoting.services.admin_service import AdminService
from evoting.services.audit_service import AuditService
from evoting.services.auth_service import AuthService
from evoting.services.candidate_service import CandidateService
from evoting.services.poll_service import PollService
from evoting.services.position_service import PositionService
from evoting.services.results_service import ResultsService
from evoting.services.station_service import StationService
from evoting.services.voter_service import VoterService
from evoting.services.voting_service import VotingService
from evoting.ui import themes
from evoting.ui.admin_flow import AdminFlow
from evoting.ui.console import Console
from evoting.ui.login_flow import LoginFlow
from evoting.ui.voter_flow import VoterFlow


class EvotingApplication:
    def __init__(self) -> None:
        self.console = Console()
        data_file = Path(__file__).resolve().parent.parent / "evoting_data.json"
        self.storage = JsonStorageRepository(data_file)
        try:
            self.state = self.storage.load()
        except StorageError as error:
            self.console.error(str(error))
            self.state = SystemState()
        self.audit = AuditService(self.state)
        build_service = lambda service_cls: service_cls(
            self.state,
            self.console,
            self.storage,
            self.audit,
        )
        self.auth_service = build_service(AuthService)
        self.candidate_service = build_service(CandidateService)
        self.station_service = build_service(StationService)
        self.position_service = build_service(PositionService)
        self.poll_service = build_service(PollService)
        self.voter_service = build_service(VoterService)
        self.results_service = build_service(ResultsService)
        self.admin_service = AdminService(
            self.state,
            self.console,
            self.storage,
            self.audit,
            self.auth_service,
        )
        self.voting_service = build_service(VotingService)
        self.login_flow = LoginFlow(self.console, self.auth_service, self.save_data)
        self.admin_flow = AdminFlow(
            self.console,
            self.state,
            self.candidate_service,
            self.station_service,
            self.position_service,
            self.poll_service,
            self.voter_service,
            self.admin_service,
            self.results_service,
            self.save_data,
            self.logout_admin,
        )
        self.voter_flow = VoterFlow(
            self.console,
            self.state,
            self.voting_service,
            self.auth_service,
            self.results_service,
            self.logout_voter,
        )

    def save_data(self) -> None:
        try:
            self.storage.save(self.state)
        except StorageError as error:
            self.console.error(str(error))
        else:
            self.console.info("Data saved successfully")

    def logout_admin(self) -> None:
        if self.state.current_user is not None:
            self.audit.log("LOGOUT", self.state.current_user["username"], "Admin logged out")
        self.save_data()
        self.state.clear_session()

    def logout_voter(self) -> None:
        if self.state.current_user is not None:
            self.audit.log(
                "LOGOUT",
                self.state.current_user["voter_card_number"],
                "Voter logged out",
            )
        self.save_data()
        self.state.clear_session()

    def run(self) -> None:
        print(f"\n  {themes.THEME_LOGIN}Loading E-Voting System...{themes.RESET}")
        time.sleep(1)
        while True:
            try:
                logged_in = self.login_flow.login()
            except SystemExit:
                return
            if not logged_in:
                continue
            if self.state.current_role == "admin":
                self.admin_flow.run()
            elif self.state.current_role == "voter":
                self.voter_flow.run()
            self.state.clear_session()


def main() -> None:
    application = EvotingApplication()
    application.run()


if __name__ == "__main__":
    main()
