from __future__ import annotations

from evoting.domain.constants import ROLE_MAP
from evoting.domain.state import timestamp_now
from evoting.domain.validators import ensure_password_length
from evoting.services.audit_service import AuditService
from evoting.services.auth_service import AuthService
from evoting.services.base import BaseService
from evoting.ui import themes


class AdminService(BaseService):
    def __init__(self, state, console, storage, audit: AuditService, auth_service: AuthService) -> None:
        super().__init__(state, console, storage, audit)
        self.auth_service = auth_service

    def _render_admin_choice(self, admin: dict) -> str:
        active = (
            self.console.status_badge("Active", True)
            if admin["is_active"]
            else self.console.status_badge("Inactive", False)
        )
        return (
            f"  {themes.THEME_ADMIN}{admin['id']}.{themes.RESET} {admin['username']} "
            f"{themes.DIM}({admin['role']}){themes.RESET} {active}"
        )

    def create_admin(self) -> None:
        current_user = self.state.current_user
        self.show_screen("CREATE ADMIN ACCOUNT", themes.THEME_ADMIN)
        if current_user["role"] != "super_admin":
            print()
            self.console.error("Only super admins can create admin accounts.")
            self.console.pause()
            return

        print()
        username = self.console.prompt("Username: ")
        if not username:
            self.console.error("Username cannot be empty.")
            self.console.pause()
            return
        if any(admin["username"] == username for admin in self.state.admins.values()):
            self.console.error("Username already exists.")
            self.console.pause()
            return

        full_name = self.console.prompt("Full Name: ")
        email = self.console.prompt("Email: ")
        try:
            password = ensure_password_length(
                self.console.masked_input("Password: ").strip()
            )
        except ValueError as error:
            self.console.error(str(error))
            self.console.pause()
            return

        self.console.subheader("Available Roles", themes.THEME_ADMIN_ACCENT)
        self.console.menu_item(1, f"super_admin {themes.DIM}─ Full access{themes.RESET}", themes.THEME_ADMIN)
        self.console.menu_item(2, f"election_officer {themes.DIM}─ Manage polls and candidates{themes.RESET}", themes.THEME_ADMIN)
        self.console.menu_item(3, f"station_manager {themes.DIM}─ Manage stations and verify voters{themes.RESET}", themes.THEME_ADMIN)
        self.console.menu_item(4, f"auditor {themes.DIM}─ Read-only access{themes.RESET}", themes.THEME_ADMIN)
        role_choice = self.console.prompt("\nSelect role (1-4): ")
        if role_choice not in ROLE_MAP:
            self.console.error("Invalid role.")
            self.console.pause()
            return

        role = ROLE_MAP[role_choice]
        admin_id = self.state.admin_id_counter
        self.state.admins[admin_id] = {
            "id": admin_id,
            "username": username,
            "password": self.auth_service.hash_password(password),
            "full_name": full_name,
            "email": email,
            "role": role,
            "created_at": timestamp_now(),
            "is_active": True,
        }
        self.state.admin_id_counter += 1
        self.audit.log(
            "CREATE_ADMIN",
            current_user["username"],
            f"Created admin: {username} (Role: {role})",
        )
        print()
        self.console.success(f"Admin '{username}' created with role: {role}")
        self.persist()
        self.console.pause()

    def view_admins(self) -> None:
        self.show_screen("ALL ADMIN ACCOUNTS", themes.THEME_ADMIN)
        print()
        self.console.table_header(
            f"{'ID':<5} {'Username':<20} {'Full Name':<25} {'Role':<20} {'Active':<8}",
            themes.THEME_ADMIN,
        )
        self.console.table_divider(78, themes.THEME_ADMIN)
        for admin in self.state.admins.values():
            active = self.console.status_badge("Yes", True) if admin["is_active"] else self.console.status_badge("No", False)
            print(
                f"  {admin['id']:<5} {admin['username']:<20} {admin['full_name']:<25} "
                f"{admin['role']:<20} {active}"
            )
        print(f"\n  {themes.DIM}Total Admins: {len(self.state.admins)}{themes.RESET}")
        self.console.pause()

    def deactivate_admin(self) -> None:
        current_user = self.state.current_user
        self.show_screen("DEACTIVATE ADMIN", themes.THEME_ADMIN)
        if current_user["role"] != "super_admin":
            print()
            self.console.error("Only super admins can deactivate admins.")
            self.console.pause()
            return

        admin_id, admin = self.select_record(
            self.state.admins,
            self._render_admin_choice,
            "\nEnter Admin ID to deactivate: ",
            "Admin not found.",
        )
        if admin is None:
            return
        if admin_id == current_user["id"]:
            self.console.error("Cannot deactivate your own account.")
            self.console.pause()
            return
        if self.confirm(f"Deactivate '{admin['username']}'? (yes/no): "):
            admin["is_active"] = False
            self.audit.log(
                "DEACTIVATE_ADMIN",
                current_user["username"],
                f"Deactivated admin: {admin['username']}",
            )
            print()
            self.console.success("Admin deactivated.")
            self.persist()
        self.console.pause()
