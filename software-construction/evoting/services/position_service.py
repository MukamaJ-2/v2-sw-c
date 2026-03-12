from __future__ import annotations

from evoting.domain.constants import MIN_CANDIDATE_AGE, VALID_POSITION_LEVELS
from evoting.domain.state import timestamp_now
from evoting.services.base import BaseService
from evoting.ui import themes


class PositionService(BaseService):
    def _render_position_choice(self, position: dict) -> str:
        return (
            f"  {themes.THEME_ADMIN}{position['id']}.{themes.RESET} "
            f"{position['title']} {themes.DIM}({position['level']}){themes.RESET}"
        )

    def create_position(self) -> None:
        current_user = self.state.current_user
        self.show_screen("CREATE POSITION", themes.THEME_ADMIN)
        print()
        title = self.console.prompt("Position Title (e.g. President, Governor, Senator): ")
        if not title:
            self.console.error("Title cannot be empty.")
            self.console.pause()
            return
        description = self.console.prompt("Description: ")
        level = self.console.prompt("Level (National/Regional/Local): ")
        if level.lower() not in VALID_POSITION_LEVELS:
            self.console.error("Invalid level.")
            self.console.pause()
            return
        try:
            max_winners = int(self.console.prompt("Number of winners/seats: "))
            if max_winners <= 0:
                raise ValueError
        except ValueError:
            self.console.error("Must be at least 1.")
            self.console.pause()
            return
        min_candidate_age = self.console.prompt(f"Minimum candidate age [{MIN_CANDIDATE_AGE}]: ")
        min_candidate_age_value = (
            int(min_candidate_age) if min_candidate_age.isdigit() else MIN_CANDIDATE_AGE
        )

        position_id = self.state.position_id_counter
        self.state.positions[position_id] = {
            "id": position_id,
            "title": title,
            "description": description,
            "level": level.capitalize(),
            "max_winners": max_winners,
            "min_candidate_age": min_candidate_age_value,
            "is_active": True,
            "created_at": timestamp_now(),
            "created_by": current_user["username"],
        }
        self.state.position_id_counter += 1
        self.audit.log(
            "CREATE_POSITION",
            current_user["username"],
            f"Created position: {title} (ID: {position_id})",
        )
        print()
        self.console.success(f"Position '{title}' created! ID: {position_id}")
        self.persist()
        self.console.pause()

    def view_positions(self) -> None:
        self.show_screen("ALL POSITIONS", themes.THEME_ADMIN)
        if not self.require_records(self.state.positions, "No positions found."):
            return

        print()
        self.console.table_header(
            f"{'ID':<5} {'Title':<25} {'Level':<12} {'Seats':<8} {'Min Age':<10} {'Status':<10}",
            themes.THEME_ADMIN,
        )
        self.console.table_divider(70, themes.THEME_ADMIN)
        for position in self.state.positions.values():
            status = self.console.status_badge("Active", True) if position["is_active"] else self.console.status_badge("Inactive", False)
            print(
                f"  {position['id']:<5} {position['title']:<25} {position['level']:<12} "
                f"{position['max_winners']:<8} {position['min_candidate_age']:<10} {status}"
            )
        print(f"\n  {themes.DIM}Total Positions: {len(self.state.positions)}{themes.RESET}")
        self.console.pause()

    def update_position(self) -> None:
        current_user = self.state.current_user
        self.show_screen("UPDATE POSITION", themes.THEME_ADMIN)
        if not self.require_records(self.state.positions, "No positions found."):
            return
        position_id, position = self.select_record(
            self.state.positions,
            self._render_position_choice,
            "\nEnter Position ID to update: ",
            "Position not found.",
        )
        if position is None:
            return

        print(f"\n  {themes.BOLD}Updating: {position['title']}{themes.RESET}")
        self.console.info("Press Enter to keep current value\n")
        new_title = self.console.prompt(f"Title [{position['title']}]: ")
        if new_title:
            position["title"] = new_title
        new_description = self.console.prompt(f"Description [{position['description'][:50]}]: ")
        if new_description:
            position["description"] = new_description
        new_level = self.console.prompt(f"Level [{position['level']}]: ")
        if new_level and new_level.lower() in VALID_POSITION_LEVELS:
            position["level"] = new_level.capitalize()
        new_seats = self.console.prompt(f"Seats [{position['max_winners']}]: ")
        if new_seats:
            try:
                position["max_winners"] = int(new_seats)
            except ValueError:
                self.console.warning("Keeping old value.")
        self.audit.log(
            "UPDATE_POSITION",
            current_user["username"],
            f"Updated position: {position['title']}",
        )
        print()
        self.console.success("Position updated!")
        self.persist()
        self.console.pause()

    def delete_position(self) -> None:
        current_user = self.state.current_user
        self.show_screen("DELETE POSITION", themes.THEME_ADMIN)
        if not self.require_records(self.state.positions, "No positions found."):
            return
        position_id, position = self.select_record(
            self.state.positions,
            self._render_position_choice,
            "\nEnter Position ID to delete: ",
            "Position not found.",
        )
        if position is None:
            return

        for poll in self.state.polls.values():
            for poll_position in poll.get("positions", []):
                if poll_position["position_id"] == position_id and poll["status"] == "open":
                    self.console.error(f"Cannot delete - in active poll: {poll['title']}")
                    self.console.pause()
                    return

        if self.confirm(f"Confirm deactivation of '{position['title']}'? (yes/no): "):
            position["is_active"] = False
            self.audit.log(
                "DELETE_POSITION",
                current_user["username"],
                f"Deactivated position: {position['title']}",
            )
            print()
            self.console.success("Position deactivated.")
            self.persist()
        self.console.pause()
