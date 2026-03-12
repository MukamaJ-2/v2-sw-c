from __future__ import annotations

from evoting.domain.constants import (
    MIN_CANDIDATE_AGE,
    POLL_STATUS_CLOSED,
    POLL_STATUS_DRAFT,
    POLL_STATUS_OPEN,
)
from evoting.domain.state import timestamp_now
from evoting.domain.validators import ValidationError, parse_date, parse_int_list
from evoting.services.base import BaseService
from evoting.ui import themes


class PollService(BaseService):
    def _status_color(self, status: str) -> str:
        if status == POLL_STATUS_OPEN:
            return themes.GREEN
        if status == POLL_STATUS_DRAFT:
            return themes.YELLOW
        return themes.RED

    def _render_poll_choice(self, poll: dict) -> str:
        status_color = self._status_color(poll["status"])
        return (
            f"  {themes.THEME_ADMIN}{poll['id']}.{themes.RESET} {poll['title']} "
            f"{status_color}({poll['status']}){themes.RESET}"
        )

    def create_poll(self) -> None:
        current_user = self.state.current_user
        self.show_screen("CREATE POLL / ELECTION", themes.THEME_ADMIN)
        print()
        title = self.console.prompt("Poll/Election Title: ")
        if not title:
            self.console.error("Title cannot be empty.")
            self.console.pause()
            return
        description = self.console.prompt("Description: ")
        election_type = self.console.prompt(
            "Election Type (General/Primary/By-election/Referendum): "
        )
        start_date = self.console.prompt("Start Date (YYYY-MM-DD): ")
        end_date = self.console.prompt("End Date (YYYY-MM-DD): ")
        try:
            start = parse_date(start_date, "Start Date")
            end = parse_date(end_date, "End Date")
            if end <= start:
                raise ValidationError("End date must be after start date.")
        except ValidationError as error:
            self.console.error(str(error))
            self.console.pause()
            return

        active_positions = {
            position_id: position
            for position_id, position in self.state.positions.items()
            if position["is_active"]
        }
        if not active_positions:
            self.console.error("No active positions. Create positions first.")
            self.console.pause()
            return

        self.console.subheader("Available Positions", themes.THEME_ADMIN_ACCENT)
        for position in active_positions.values():
            print(
                f"    {themes.THEME_ADMIN}{position['id']}.{themes.RESET} {position['title']} "
                f"{themes.DIM}({position['level']}) - {position['max_winners']} seat(s){themes.RESET}"
            )
        try:
            selected_position_ids = parse_int_list(
                self.console.prompt("\nEnter Position IDs (comma-separated): "),
                "position ids",
            )
        except ValidationError as error:
            self.console.error(str(error))
            self.console.pause()
            return

        poll_positions = []
        for position_id in selected_position_ids:
            if position_id not in active_positions:
                self.console.warning(f"Position ID {position_id} not found or inactive. Skipping.")
                continue
            position = self.state.positions[position_id]
            poll_positions.append(
                {
                    "position_id": position_id,
                    "position_title": position["title"],
                    "candidate_ids": [],
                    "max_winners": position["max_winners"],
                }
            )
        if not poll_positions:
            self.console.error("No valid positions selected.")
            self.console.pause()
            return

        active_stations = {
            station_id: station
            for station_id, station in self.state.voting_stations.items()
            if station["is_active"]
        }
        if not active_stations:
            self.console.error("No voting stations. Create stations first.")
            self.console.pause()
            return

        self.console.subheader("Available Voting Stations", themes.THEME_ADMIN_ACCENT)
        for station in active_stations.values():
            print(
                f"    {themes.THEME_ADMIN}{station['id']}.{themes.RESET} {station['name']} "
                f"{themes.DIM}({station['location']}){themes.RESET}"
            )
        if self.console.prompt("\nUse all active stations? (yes/no): ").lower() == "yes":
            selected_station_ids = list(active_stations.keys())
        else:
            try:
                selected_station_ids = parse_int_list(
                    self.console.prompt("Enter Station IDs (comma-separated): "),
                    "station ids",
                )
            except ValidationError as error:
                self.console.error(str(error))
                self.console.pause()
                return

        poll_id = self.state.poll_id_counter
        self.state.polls[poll_id] = {
            "id": poll_id,
            "title": title,
            "description": description,
            "election_type": election_type,
            "start_date": start_date,
            "end_date": end_date,
            "positions": poll_positions,
            "station_ids": selected_station_ids,
            "status": POLL_STATUS_DRAFT,
            "total_votes_cast": 0,
            "created_at": timestamp_now(),
            "created_by": current_user["username"],
        }
        self.state.poll_id_counter += 1
        self.audit.log(
            "CREATE_POLL",
            current_user["username"],
            f"Created poll: {title} (ID: {poll_id})",
        )
        print()
        self.console.success(f"Poll '{title}' created! ID: {poll_id}")
        self.console.warning("Status: DRAFT - Assign candidates and then open the poll.")
        self.persist()
        self.console.pause()

    def view_all_polls(self) -> None:
        self.show_screen("ALL POLLS / ELECTIONS", themes.THEME_ADMIN)
        if not self.require_records(self.state.polls, "No polls found."):
            return

        for poll in self.state.polls.values():
            status_color = self._status_color(poll["status"])
            print(f"\n  {themes.BOLD}{themes.THEME_ADMIN}Poll #{poll['id']}: {poll['title']}{themes.RESET}")
            print(
                f"  {themes.DIM}Type:{themes.RESET} {poll['election_type']}  "
                f"{themes.DIM}│  Status:{themes.RESET} {status_color}{themes.BOLD}{poll['status'].upper()}{themes.RESET}"
            )
            print(
                f"  {themes.DIM}Period:{themes.RESET} {poll['start_date']} to {poll['end_date']}  "
                f"{themes.DIM}│  Votes:{themes.RESET} {poll['total_votes_cast']}"
            )
            for position in poll["positions"]:
                candidate_names = [
                    self.state.candidates[candidate_id]["full_name"]
                    for candidate_id in position["candidate_ids"]
                    if candidate_id in self.state.candidates
                ]
                candidate_display = ", ".join(candidate_names) if candidate_names else f"{themes.DIM}None assigned{themes.RESET}"
                print(
                    f"    {themes.THEME_ADMIN_ACCENT}▸{themes.RESET} "
                    f"{position['position_title']}: {candidate_display}"
                )
        print(f"\n  {themes.DIM}Total Polls: {len(self.state.polls)}{themes.RESET}")
        self.console.pause()

    def update_poll(self) -> None:
        current_user = self.state.current_user
        self.show_screen("UPDATE POLL", themes.THEME_ADMIN)
        if not self.require_records(self.state.polls, "No polls found."):
            return
        poll_id, poll = self.select_record(
            self.state.polls,
            self._render_poll_choice,
            "\nEnter Poll ID to update: ",
            "Poll not found.",
        )
        if poll is None:
            return
        if poll["status"] == POLL_STATUS_OPEN:
            self.console.error("Cannot update an open poll. Close it first.")
            self.console.pause()
            return
        if poll["status"] == POLL_STATUS_CLOSED and poll["total_votes_cast"] > 0:
            self.console.error("Cannot update a poll with votes.")
            self.console.pause()
            return

        print(f"\n  {themes.BOLD}Updating: {poll['title']}{themes.RESET}")
        self.console.info("Press Enter to keep current value\n")
        new_title = self.console.prompt(f"Title [{poll['title']}]: ")
        if new_title:
            poll["title"] = new_title
        new_description = self.console.prompt(f"Description [{poll['description'][:50]}]: ")
        if new_description:
            poll["description"] = new_description
        new_type = self.console.prompt(f"Election Type [{poll['election_type']}]: ")
        if new_type:
            poll["election_type"] = new_type
        new_start = self.console.prompt(f"Start Date [{poll['start_date']}]: ")
        if new_start:
            try:
                parse_date(new_start, "Start Date")
                poll["start_date"] = new_start
            except ValidationError:
                self.console.warning("Invalid date, keeping old value.")
        new_end = self.console.prompt(f"End Date [{poll['end_date']}]: ")
        if new_end:
            try:
                parse_date(new_end, "End Date")
                poll["end_date"] = new_end
            except ValidationError:
                self.console.warning("Invalid date, keeping old value.")
        self.audit.log(
            "UPDATE_POLL",
            current_user["username"],
            f"Updated poll: {poll['title']}",
        )
        print()
        self.console.success("Poll updated!")
        self.persist()
        self.console.pause()

    def delete_poll(self) -> None:
        current_user = self.state.current_user
        self.show_screen("DELETE POLL", themes.THEME_ADMIN)
        if not self.require_records(self.state.polls, "No polls found."):
            return
        poll_id, poll = self.select_record(
            self.state.polls,
            self._render_poll_choice,
            "\nEnter Poll ID to delete: ",
            "Poll not found.",
        )
        if poll is None:
            return
        if poll["status"] == POLL_STATUS_OPEN:
            self.console.error("Cannot delete an open poll. Close it first.")
            self.console.pause()
            return
        if poll["total_votes_cast"] > 0:
            self.console.warning(f"This poll has {poll['total_votes_cast']} votes recorded.")
        if self.confirm(f"Confirm deletion of '{poll['title']}'? (yes/no): "):
            deleted_title = poll["title"]
            del self.state.polls[poll_id]
            self.state.votes = [
                vote for vote in self.state.votes if vote["poll_id"] != poll_id
            ]
            self.audit.log(
                "DELETE_POLL",
                current_user["username"],
                f"Deleted poll: {deleted_title}",
            )
            print()
            self.console.success(f"Poll '{deleted_title}' deleted.")
            self.persist()
        self.console.pause()

    def open_close_poll(self) -> None:
        current_user = self.state.current_user
        self.show_screen("OPEN / CLOSE POLL", themes.THEME_ADMIN)
        if not self.require_records(self.state.polls, "No polls found."):
            return
        poll_id, poll = self.select_record(
            self.state.polls,
            self._render_poll_choice,
            "\nEnter Poll ID: ",
            "Poll not found.",
        )
        if poll is None:
            return

        if poll["status"] == POLL_STATUS_DRAFT:
            if not any(position["candidate_ids"] for position in poll["positions"]):
                self.console.error("Cannot open - no candidates assigned.")
                self.console.pause()
                return
            if self.confirm(f"Open poll '{poll['title']}'? Voting will begin. (yes/no): "):
                poll["status"] = POLL_STATUS_OPEN
                self.audit.log("OPEN_POLL", current_user["username"], f"Opened poll: {poll['title']}")
                print()
                self.console.success(f"Poll '{poll['title']}' is now OPEN for voting!")
                self.persist()
        elif poll["status"] == POLL_STATUS_OPEN:
            if self.confirm(f"Close poll '{poll['title']}'? No more votes accepted. (yes/no): "):
                poll["status"] = POLL_STATUS_CLOSED
                self.audit.log("CLOSE_POLL", current_user["username"], f"Closed poll: {poll['title']}")
                print()
                self.console.success(f"Poll '{poll['title']}' is now CLOSED.")
                self.persist()
        else:
            self.console.info("This poll is already closed.")
            if self.confirm("Reopen it? (yes/no): "):
                poll["status"] = POLL_STATUS_OPEN
                self.audit.log("REOPEN_POLL", current_user["username"], f"Reopened poll: {poll['title']}")
                print()
                self.console.success("Poll reopened!")
                self.persist()
        self.console.pause()

    def assign_candidates_to_poll(self) -> None:
        current_user = self.state.current_user
        self.show_screen("ASSIGN CANDIDATES TO POLL", themes.THEME_ADMIN)
        if not self.require_records(self.state.polls, "No polls found."):
            return
        if not self.require_records(self.state.candidates, "No candidates found."):
            return
        poll_id, poll = self.select_record(
            self.state.polls,
            self._render_poll_choice,
            "\nEnter Poll ID: ",
            "Poll not found.",
        )
        if poll is None:
            return
        if poll["status"] == POLL_STATUS_OPEN:
            self.console.error("Cannot modify candidates of an open poll.")
            self.console.pause()
            return

        active_candidates = {
            candidate_id: candidate
            for candidate_id, candidate in self.state.candidates.items()
            if candidate["is_active"] and candidate["is_approved"]
        }
        for position in poll["positions"]:
            self.console.subheader(f"Position: {position['position_title']}", themes.THEME_ADMIN_ACCENT)
            current_candidates = [
                f"{candidate_id}: {self.state.candidates[candidate_id]['full_name']}"
                for candidate_id in position["candidate_ids"]
                if candidate_id in self.state.candidates
            ]
            if current_candidates:
                print(f"  {themes.DIM}Current:{themes.RESET} {', '.join(current_candidates)}")
            else:
                self.console.info("No candidates assigned yet.")

            position_data = self.state.positions.get(position["position_id"], {})
            minimum_age = position_data.get("min_candidate_age", MIN_CANDIDATE_AGE)
            eligible = {
                candidate_id: candidate
                for candidate_id, candidate in active_candidates.items()
                if candidate["age"] >= minimum_age
            }
            if not eligible:
                self.console.info("No eligible candidates found.")
                continue
            self.console.subheader("Available Candidates", themes.THEME_ADMIN)
            for candidate_id, candidate in eligible.items():
                marker = f" {themes.GREEN}[ASSIGNED]{themes.RESET}" if candidate_id in position["candidate_ids"] else ""
                print(
                    f"    {themes.THEME_ADMIN}{candidate['id']}.{themes.RESET} "
                    f"{candidate['full_name']} {themes.DIM}({candidate['party']}) - Age: "
                    f"{candidate['age']}, Edu: {candidate['education']}{themes.RESET}{marker}"
                )
            if not self.confirm(f"\nModify candidates for {position['position_title']}? (yes/no): "):
                continue
            try:
                requested_ids = parse_int_list(
                    self.console.prompt("Enter Candidate IDs (comma-separated): "),
                    "candidate ids",
                )
            except ValidationError as error:
                self.console.error(str(error))
                continue
            valid_ids = []
            for candidate_id in requested_ids:
                if candidate_id in eligible:
                    valid_ids.append(candidate_id)
                else:
                    self.console.warning(f"Candidate {candidate_id} not eligible. Skipping.")
            position["candidate_ids"] = valid_ids
            self.console.success(f"{len(valid_ids)} candidate(s) assigned.")

        self.audit.log(
            "ASSIGN_CANDIDATES",
            current_user["username"],
            f"Updated candidates for poll: {poll['title']}",
        )
        self.persist()
        self.console.pause()
