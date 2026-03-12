from __future__ import annotations

from evoting.services.auth_service import AuthService
from evoting.ui import themes
from evoting.ui.console import Console


class LoginFlow:
    def __init__(self, console: Console, auth_service: AuthService, exit_callback) -> None:
        self.console = console
        self.auth_service = auth_service
        self.exit_callback = exit_callback
        self.actions = {
            "1": ("Login as Admin", self.auth_service.login_admin),
            "2": ("Login as Voter", self.auth_service.login_voter),
            "3": ("Register as Voter", self._register_voter),
            "4": ("Exit", self._exit),
        }

    def _register_voter(self) -> bool:
        self.auth_service.register_voter()
        return False

    def _exit(self) -> bool:
        print()
        self.console.info("Goodbye!")
        self.exit_callback()
        raise SystemExit

    def login(self) -> bool:
        self.console.clear_screen()
        self.console.header("E-VOTING SYSTEM", themes.THEME_LOGIN)
        print()
        for option, (label, _) in self.actions.items():
            self.console.menu_item(int(option), label, themes.THEME_LOGIN)
        print()
        choice = self.console.prompt("Enter choice: ")
        action = self.actions.get(choice)
        if action is None:
            self.console.error("Invalid choice.")
            self.console.pause()
            return False
        return action[1]()
