from __future__ import annotations

from collections import Counter

from evoting.domain.constants import (
    POLL_STATUS_CLOSED,
    POLL_STATUS_DRAFT,
    POLL_STATUS_OPEN,
)
from evoting.services.base import BaseService
from evoting.ui import themes


class ResultsService(BaseService):
    def get_poll_status_color(self, status: str) -> str:
        if status == POLL_STATUS_OPEN:
            return themes.GREEN
        if status == POLL_STATUS_DRAFT:
            return themes.YELLOW
        return themes.RED

    def tally_votes_for_position(
        self,
        poll_id: int,
        position_id: int,
        station_id: int | None = None,
    ) -> dict:
        counts: Counter[int] = Counter()
        abstentions = 0
        total = 0
        for vote in self.state.votes:
            if vote["poll_id"] != poll_id or vote["position_id"] != position_id:
                continue
            if station_id is not None and vote["station_id"] != station_id:
                continue
            total += 1
            if vote["abstained"]:
                abstentions += 1
            else:
                counts[vote["candidate_id"]] += 1
        return {
            "counts": dict(counts),
            "abstentions": abstentions,
            "total": total,
        }

    def _print_ranked_results(self, tally: dict, max_winners: int, theme_color: str) -> bool:
        counts = tally["counts"]
        total = tally["total"]
        if not counts:
            self.console.info("    No votes recorded for this position.")
            if tally["abstentions"] > 0:
                percentage = (tally["abstentions"] / total * 100) if total else 0
                print(
                    f"    {themes.GRAY}Abstained: {tally['abstentions']} ({percentage:.1f}%){themes.RESET}"
                )
            return False

        for rank, (candidate_id, count) in enumerate(
            sorted(counts.items(), key=lambda item: item[1], reverse=True),
            start=1,
        ):
            candidate = self.state.candidates.get(candidate_id, {})
            percentage = (count / total * 100) if total else 0
            bar_length = int(percentage / 2)
            bar = (
                f"{theme_color}{'█' * bar_length}{themes.GRAY}"
                f"{'░' * (50 - bar_length)}{themes.RESET}"
            )
            winner = ""
            if rank <= max_winners:
                winner = f" {themes.BG_GREEN}{themes.BLACK}{themes.BOLD} WINNER {themes.RESET}"
            print(
                f"    {themes.BOLD}{rank}. {candidate.get('full_name', '?')}{themes.RESET} "
                f"{themes.DIM}({candidate.get('party', '?')}){themes.RESET}"
            )
            print(f"       {bar} {themes.BOLD}{count}{themes.RESET} ({percentage:.1f}%){winner}")

        if tally["abstentions"] > 0:
            abstention_pct = (tally["abstentions"] / total * 100) if total else 0
            print(
                f"    {themes.GRAY}Abstained: {tally['abstentions']} ({abstention_pct:.1f}%){themes.RESET}"
            )
        return True

    def view_poll_results(self) -> None:
        self.console.clear_screen()
        self.console.header("POLL RESULTS", themes.THEME_ADMIN)
        if not self.state.polls:
            print()
            self.console.info("No polls found.")
            self.console.pause()
            return

        print()
        for poll in self.state.polls.values():
            color = self.get_poll_status_color(poll["status"])
            print(
                f"  {themes.THEME_ADMIN}{poll['id']}.{themes.RESET} {poll['title']} "
                f"{color}({poll['status']}){themes.RESET}"
            )
        try:
            poll_id = int(self.console.prompt("\nEnter Poll ID: "))
        except ValueError:
            self.console.error("Invalid input.")
            self.console.pause()
            return
        poll = self.state.polls.get(poll_id)
        if poll is None:
            self.console.error("Poll not found.")
            self.console.pause()
            return

        print()
        self.console.header(f"RESULTS: {poll['title']}", themes.THEME_ADMIN)
        color = self.get_poll_status_color(poll["status"])
        print(
            f"  {themes.DIM}Status:{themes.RESET} {color}{themes.BOLD}{poll['status'].upper()}{themes.RESET}  "
            f"{themes.DIM}│  Votes:{themes.RESET} {themes.BOLD}{poll['total_votes_cast']}{themes.RESET}"
        )
        total_eligible = sum(
            1
            for voter in self.state.voters.values()
            if voter["is_verified"]
            and voter["is_active"]
            and voter["station_id"] in poll["station_ids"]
        )
        turnout = (poll["total_votes_cast"] / total_eligible * 100) if total_eligible else 0
        turnout_color = themes.GREEN if turnout > 50 else themes.YELLOW if turnout > 25 else themes.RED
        print(
            f"  {themes.DIM}Eligible:{themes.RESET} {total_eligible}  "
            f"{themes.DIM}│  Turnout:{themes.RESET} {turnout_color}{themes.BOLD}{turnout:.1f}%{themes.RESET}"
        )

        for position in poll["positions"]:
            self.console.subheader(
                f"{position['position_title']} (Seats: {position['max_winners']})",
                themes.THEME_ADMIN_ACCENT,
            )
            tally = self.tally_votes_for_position(poll_id, position["position_id"])
            self._print_ranked_results(tally, position["max_winners"], themes.THEME_ADMIN)
        self.console.pause()

    def view_closed_poll_results_voter(self) -> None:
        self.console.clear_screen()
        self.console.header("ELECTION RESULTS", themes.THEME_VOTER)
        closed_polls = {
            poll_id: poll
            for poll_id, poll in self.state.polls.items()
            if poll["status"] == POLL_STATUS_CLOSED
        }
        if not closed_polls:
            print()
            self.console.info("No closed polls with results.")
            self.console.pause()
            return

        for poll_id, poll in closed_polls.items():
            print(f"\n  {themes.BOLD}{themes.THEME_VOTER}{poll['title']}{themes.RESET}")
            print(
                f"  {themes.DIM}Type:{themes.RESET} {poll['election_type']}  "
                f"{themes.DIM}│  Votes:{themes.RESET} {poll['total_votes_cast']}"
            )
            for position in poll["positions"]:
                self.console.subheader(position["position_title"], themes.THEME_VOTER_ACCENT)
                tally = self.tally_votes_for_position(poll_id, position["position_id"])
                self._print_ranked_results(tally, position["max_winners"], themes.THEME_VOTER)
        self.console.pause()

    def station_wise_results(self) -> None:
        self.console.clear_screen()
        self.console.header("STATION-WISE RESULTS", themes.THEME_ADMIN)
        if not self.state.polls:
            print()
            self.console.info("No polls found.")
            self.console.pause()
            return

        print()
        for poll in self.state.polls.values():
            color = self.get_poll_status_color(poll["status"])
            print(
                f"  {themes.THEME_ADMIN}{poll['id']}.{themes.RESET} {poll['title']} "
                f"{color}({poll['status']}){themes.RESET}"
            )
        try:
            poll_id = int(self.console.prompt("\nEnter Poll ID: "))
        except ValueError:
            self.console.error("Invalid input.")
            self.console.pause()
            return

        poll = self.state.polls.get(poll_id)
        if poll is None:
            self.console.error("Poll not found.")
            self.console.pause()
            return

        print()
        self.console.header(f"STATION RESULTS: {poll['title']}", themes.THEME_ADMIN)
        for station_id in poll["station_ids"]:
            station = self.state.voting_stations.get(station_id)
            if station is None:
                continue
            self.console.subheader(
                f"{station['name']}  ({station['location']})",
                themes.BRIGHT_WHITE,
            )
            station_votes = [
                vote
                for vote in self.state.votes
                if vote["poll_id"] == poll_id and vote["station_id"] == station_id
            ]
            unique_voters = len({vote["voter_id"] for vote in station_votes})
            registered_active = sum(
                1
                for voter in self.state.voters.values()
                if voter["station_id"] == station_id
                and voter["is_verified"]
                and voter["is_active"]
            )
            turnout = (unique_voters / registered_active * 100) if registered_active else 0
            turnout_color = themes.GREEN if turnout > 50 else themes.YELLOW if turnout > 25 else themes.RED
            print(
                f"  {themes.DIM}Registered:{themes.RESET} {registered_active}  "
                f"{themes.DIM}│  Voted:{themes.RESET} {unique_voters}  "
                f"{themes.DIM}│  Turnout:{themes.RESET} {turnout_color}{themes.BOLD}{turnout:.1f}%{themes.RESET}"
            )

            for position in poll["positions"]:
                print(f"    {themes.THEME_ADMIN_ACCENT}▸ {position['position_title']}:{themes.RESET}")
                tally = self.tally_votes_for_position(
                    poll_id,
                    position["position_id"],
                    station_id=station_id,
                )
                counts = tally["counts"]
                total = tally["total"]
                for candidate_id, count in sorted(counts.items(), key=lambda item: item[1], reverse=True):
                    candidate = self.state.candidates.get(candidate_id, {})
                    percentage = (count / total * 100) if total else 0
                    print(
                        f"      {candidate.get('full_name', '?')} "
                        f"{themes.DIM}({candidate.get('party', '?')}){themes.RESET}: "
                        f"{themes.BOLD}{count}{themes.RESET} ({percentage:.1f}%)"
                    )
                if tally["abstentions"] > 0:
                    percentage = (tally["abstentions"] / total * 100) if total else 0
                    print(
                        f"      {themes.GRAY}Abstained: {tally['abstentions']} ({percentage:.1f}%){themes.RESET}"
                    )
        self.console.pause()

    def view_detailed_statistics(self) -> None:
        self.console.clear_screen()
        self.console.header("DETAILED STATISTICS", themes.THEME_ADMIN)
        self.console.subheader("SYSTEM OVERVIEW", themes.THEME_ADMIN_ACCENT)

        total_candidates = len(self.state.candidates)
        active_candidates = sum(1 for candidate in self.state.candidates.values() if candidate["is_active"])
        total_voters = len(self.state.voters)
        verified_voters = sum(1 for voter in self.state.voters.values() if voter["is_verified"])
        active_voters = sum(1 for voter in self.state.voters.values() if voter["is_active"])
        total_stations = len(self.state.voting_stations)
        active_stations = sum(1 for station in self.state.voting_stations.values() if station["is_active"])
        total_polls = len(self.state.polls)
        open_polls = sum(1 for poll in self.state.polls.values() if poll["status"] == POLL_STATUS_OPEN)
        closed_polls = sum(1 for poll in self.state.polls.values() if poll["status"] == POLL_STATUS_CLOSED)
        draft_polls = sum(1 for poll in self.state.polls.values() if poll["status"] == POLL_STATUS_DRAFT)

        print(f"  {themes.THEME_ADMIN}Candidates:{themes.RESET}  {total_candidates} {themes.DIM}(Active: {active_candidates}){themes.RESET}")
        print(
            f"  {themes.THEME_ADMIN}Voters:{themes.RESET}      {total_voters} "
            f"{themes.DIM}(Verified: {verified_voters}, Active: {active_voters}){themes.RESET}"
        )
        print(f"  {themes.THEME_ADMIN}Stations:{themes.RESET}    {total_stations} {themes.DIM}(Active: {active_stations}){themes.RESET}")
        print(
            f"  {themes.THEME_ADMIN}Polls:{themes.RESET}       {total_polls} "
            f"{themes.DIM}({themes.GREEN}Open: {open_polls}{themes.RESET}{themes.DIM}, "
            f"{themes.RED}Closed: {closed_polls}{themes.RESET}{themes.DIM}, "
            f"{themes.YELLOW}Draft: {draft_polls}{themes.RESET}{themes.DIM}){themes.RESET}"
        )
        print(f"  {themes.THEME_ADMIN}Total Votes:{themes.RESET} {len(self.state.votes)}")

        self.console.subheader("VOTER DEMOGRAPHICS", themes.THEME_ADMIN_ACCENT)
        gender_counts: Counter[str] = Counter()
        age_groups = {"18-25": 0, "26-35": 0, "36-45": 0, "46-55": 0, "56-65": 0, "65+": 0}
        for voter in self.state.voters.values():
            gender_counts[voter.get("gender", "?")] += 1
            age = voter.get("age", 0)
            if age <= 25:
                age_groups["18-25"] += 1
            elif age <= 35:
                age_groups["26-35"] += 1
            elif age <= 45:
                age_groups["36-45"] += 1
            elif age <= 55:
                age_groups["46-55"] += 1
            elif age <= 65:
                age_groups["56-65"] += 1
            else:
                age_groups["65+"] += 1
        for gender, count in gender_counts.items():
            percentage = (count / total_voters * 100) if total_voters else 0
            print(f"    {gender}: {count} ({percentage:.1f}%)")
        print(f"  {themes.BOLD}Age Distribution:{themes.RESET}")
        for group, count in age_groups.items():
            percentage = (count / total_voters * 100) if total_voters else 0
            print(
                f"    {group:>5}: {count:>3} ({percentage:>5.1f}%) "
                f"{themes.THEME_ADMIN}{'█' * int(percentage / 2)}{themes.RESET}"
            )

        self.console.subheader("STATION LOAD", themes.THEME_ADMIN_ACCENT)
        for station_id, station in self.state.voting_stations.items():
            voter_count = sum(1 for voter in self.state.voters.values() if voter["station_id"] == station_id)
            load_percent = (voter_count / station["capacity"] * 100) if station["capacity"] else 0
            load_color = themes.RED if load_percent > 100 else themes.YELLOW if load_percent > 75 else themes.GREEN
            status = f"{themes.RED}{themes.BOLD}OVERLOADED{themes.RESET}" if load_percent > 100 else f"{themes.GREEN}OK{themes.RESET}"
            print(
                f"    {station['name']}: {voter_count}/{station['capacity']} "
                f"{load_color}({load_percent:.0f}%){themes.RESET} {status}"
            )

        self.console.subheader("CANDIDATE PARTY DISTRIBUTION", themes.THEME_ADMIN_ACCENT)
        party_counts: Counter[str] = Counter(
            candidate["party"] for candidate in self.state.candidates.values() if candidate["is_active"]
        )
        for party, count in party_counts.most_common():
            print(f"    {party}: {themes.BOLD}{count}{themes.RESET} candidate(s)")

        self.console.subheader("CANDIDATE EDUCATION LEVELS", themes.THEME_ADMIN_ACCENT)
        education_counts: Counter[str] = Counter(
            candidate["education"] for candidate in self.state.candidates.values() if candidate["is_active"]
        )
        for education, count in education_counts.items():
            print(f"    {education}: {themes.BOLD}{count}{themes.RESET}")
        self.console.pause()

    def view_audit_log(self) -> None:
        self.console.clear_screen()
        self.console.header("AUDIT LOG", themes.THEME_ADMIN)
        if not self.state.audit_log:
            print()
            self.console.info("No audit records.")
            self.console.pause()
            return

        print(f"\n  {themes.DIM}Total Records: {len(self.state.audit_log)}{themes.RESET}")
        self.console.subheader("Filter", themes.THEME_ADMIN_ACCENT)
        self.console.menu_item(1, "Last 20 entries", themes.THEME_ADMIN)
        self.console.menu_item(2, "All entries", themes.THEME_ADMIN)
        self.console.menu_item(3, "Filter by action type", themes.THEME_ADMIN)
        self.console.menu_item(4, "Filter by user", themes.THEME_ADMIN)
        choice = self.console.prompt("\nChoice: ")

        entries = self.state.audit_log
        if choice == "1":
            entries = self.state.audit_log[-20:]
        elif choice == "3":
            action_types = sorted({entry["action"] for entry in self.state.audit_log})
            for index, action_type in enumerate(action_types, start=1):
                print(f"    {themes.THEME_ADMIN}{index}.{themes.RESET} {action_type}")
            try:
                action_choice = int(self.console.prompt("Select action type: "))
                entries = [
                    entry
                    for entry in self.state.audit_log
                    if entry["action"] == action_types[action_choice - 1]
                ]
            except (ValueError, IndexError):
                self.console.error("Invalid choice.")
                self.console.pause()
                return
        elif choice == "4":
            user_filter = self.console.prompt("Enter username/card number: ").lower()
            entries = [
                entry for entry in self.state.audit_log if user_filter in entry["user"].lower()
            ]

        print()
        self.console.table_header(
            f"{'Timestamp':<22} {'Action':<25} {'User':<20} {'Details'}",
            themes.THEME_ADMIN,
        )
        self.console.table_divider(100, themes.THEME_ADMIN)
        for entry in entries:
            action = entry["action"]
            if "CREATE" in action or action == "LOGIN":
                action_color = themes.GREEN
            elif "DELETE" in action or "DEACTIVATE" in action:
                action_color = themes.RED
            elif "UPDATE" in action:
                action_color = themes.YELLOW
            else:
                action_color = themes.RESET
            print(
                f"  {themes.DIM}{entry['timestamp'][:19]}{themes.RESET}  "
                f"{action_color}{action:<25}{themes.RESET} "
                f"{entry['user']:<20} {themes.DIM}{entry['details'][:50]}{themes.RESET}"
            )
        self.console.pause()
