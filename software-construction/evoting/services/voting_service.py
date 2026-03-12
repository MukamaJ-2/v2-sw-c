from __future__ import annotations

import hashlib

from evoting.domain.state import timestamp_now
from evoting.services.base import BaseService
from evoting.ui import themes


class VotingService(BaseService):
    def _current_voter(self) -> dict | None:
        return self.state.current_user

    def _available_polls_for_voter(self) -> dict[int, dict]:
        current_user = self._current_voter()
        if current_user is None:
            return {}
        available = {}
        for poll_id, poll in self.state.polls.items():
            if poll["status"] != "open":
                continue
            if poll_id in current_user.get("has_voted_in", []):
                continue
            if current_user["station_id"] not in poll["station_ids"]:
                continue
            available[poll_id] = poll
        return available

    def view_open_polls_voter(self) -> None:
        current_user = self._current_voter()
        self.console.clear_screen()
        self.console.header("OPEN POLLS", themes.THEME_VOTER)
        open_polls = {
            poll_id: poll
            for poll_id, poll in self.state.polls.items()
            if poll["status"] == "open"
        }
        if not open_polls:
            print()
            self.console.info("No open polls at this time.")
            self.console.pause()
            return

        for poll_id, poll in open_polls.items():
            already_voted = poll_id in current_user.get("has_voted_in", [])
            vote_status = (
                f" {themes.GREEN}[VOTED]{themes.RESET}"
                if already_voted
                else f" {themes.YELLOW}[NOT YET VOTED]{themes.RESET}"
            )
            print(
                f"\n  {themes.BOLD}{themes.THEME_VOTER}Poll #{poll['id']}: "
                f"{poll['title']}{themes.RESET}{vote_status}"
            )
            print(
                f"  {themes.DIM}Type:{themes.RESET} {poll['election_type']}  "
                f"{themes.DIM}│  Period:{themes.RESET} {poll['start_date']} to {poll['end_date']}"
            )
            for position in poll["positions"]:
                print(
                    f"    {themes.THEME_VOTER_ACCENT}▸{themes.RESET} "
                    f"{themes.BOLD}{position['position_title']}{themes.RESET}"
                )
                for candidate_id in position["candidate_ids"]:
                    candidate = self.state.candidates.get(candidate_id)
                    if candidate is None:
                        continue
                    print(
                        f"      {themes.DIM}•{themes.RESET} {candidate['full_name']} "
                        f"{themes.DIM}({candidate['party']}) │ Age: {candidate['age']} │ "
                        f"Edu: {candidate['education']}{themes.RESET}"
                    )
        self.console.pause()

    def cast_vote(self) -> None:
        current_user = self._current_voter()
        if current_user is None:
            self.console.error("No voter is currently logged in.")
            self.console.pause()
            return

        self.console.clear_screen()
        self.console.header("CAST YOUR VOTE", themes.THEME_VOTER)
        available_polls = self._available_polls_for_voter()
        if not available_polls:
            print()
            self.console.info("No available polls to vote in.")
            self.console.pause()
            return

        self.console.subheader("Available Polls", themes.THEME_VOTER_ACCENT)
        for poll in available_polls.values():
            print(
                f"  {themes.THEME_VOTER}{poll['id']}.{themes.RESET} {poll['title']} "
                f"{themes.DIM}({poll['election_type']}){themes.RESET}"
            )
        try:
            poll_id = int(self.console.prompt("\nSelect Poll ID to vote: "))
        except ValueError:
            self.console.error("Invalid input.")
            self.console.pause()
            return
        poll = available_polls.get(poll_id)
        if poll is None:
            self.console.error("Invalid poll selection.")
            self.console.pause()
            return

        print()
        self.console.header(f"Voting: {poll['title']}", themes.THEME_VOTER)
        self.console.info("Please select ONE candidate for each position.\n")
        ballot_entries = []
        for position in poll["positions"]:
            self.console.subheader(position["position_title"], themes.THEME_VOTER_ACCENT)
            if not position["candidate_ids"]:
                self.console.info("No candidates for this position.")
                continue
            visible_candidates = []
            for candidate_id in position["candidate_ids"]:
                candidate = self.state.candidates.get(candidate_id)
                if candidate is None:
                    continue
                visible_candidates.append(candidate_id)
                option_number = len(visible_candidates)
                print(
                    f"    {themes.THEME_VOTER}{themes.BOLD}{option_number}.{themes.RESET} "
                    f"{candidate['full_name']} {themes.DIM}({candidate['party']}){themes.RESET}"
                )
                print(
                    f"       {themes.DIM}Age: {candidate['age']} │ Edu: {candidate['education']} │ "
                    f"Exp: {candidate['years_experience']} yrs{themes.RESET}"
                )
                if candidate["manifesto"]:
                    print(
                        f"       {themes.ITALIC}{themes.DIM}{candidate['manifesto'][:80]}...{themes.RESET}"
                    )
            print(f"    {themes.GRAY}{themes.BOLD}0.{themes.RESET} {themes.GRAY}Abstain / Skip{themes.RESET}")
            try:
                vote_choice = int(
                    self.console.prompt(f"\nYour choice for {position['position_title']}: ")
                )
            except ValueError:
                self.console.warning("Invalid input. Skipping.")
                vote_choice = 0

            if vote_choice == 0:
                ballot_entries.append(
                    {
                        "position_id": position["position_id"],
                        "position_title": position["position_title"],
                        "candidate_id": None,
                        "abstained": True,
                    }
                )
                continue

            if 1 <= vote_choice <= len(visible_candidates):
                selected_candidate_id = visible_candidates[vote_choice - 1]
                ballot_entries.append(
                    {
                        "position_id": position["position_id"],
                        "position_title": position["position_title"],
                        "candidate_id": selected_candidate_id,
                        "candidate_name": self.state.candidates[selected_candidate_id]["full_name"],
                        "abstained": False,
                    }
                )
                continue

            self.console.warning("Invalid choice. Marking as abstain.")
            ballot_entries.append(
                {
                    "position_id": position["position_id"],
                    "position_title": position["position_title"],
                    "candidate_id": None,
                    "abstained": True,
                }
            )

        self.console.subheader("VOTE SUMMARY", themes.BRIGHT_WHITE)
        for ballot_entry in ballot_entries:
            if ballot_entry["abstained"]:
                print(
                    f"  {ballot_entry['position_title']}: {themes.GRAY}ABSTAINED{themes.RESET}"
                )
            else:
                print(
                    f"  {ballot_entry['position_title']}: {themes.BRIGHT_GREEN}{themes.BOLD}"
                    f"{ballot_entry['candidate_name']}{themes.RESET}"
                )
        print()
        if self.console.prompt("Confirm your votes? This cannot be undone. (yes/no): ").lower() != "yes":
            self.console.info("Vote cancelled.")
            self.console.pause()
            return

        vote_timestamp = timestamp_now()
        vote_hash = hashlib.sha256(f"{current_user['id']}{poll_id}{vote_timestamp}".encode()).hexdigest()[:16]
        for ballot_entry in ballot_entries:
            self.state.votes.append(
                {
                    "vote_id": vote_hash + str(ballot_entry["position_id"]),
                    "poll_id": poll_id,
                    "position_id": ballot_entry["position_id"],
                    "candidate_id": ballot_entry["candidate_id"],
                    "voter_id": current_user["id"],
                    "station_id": current_user["station_id"],
                    "timestamp": vote_timestamp,
                    "abstained": ballot_entry["abstained"],
                }
            )
        current_user.setdefault("has_voted_in", []).append(poll_id)
        self.state.polls[poll_id]["total_votes_cast"] += 1
        self.audit.log(
            "CAST_VOTE",
            current_user["voter_card_number"],
            f"Voted in poll: {poll['title']} (Hash: {vote_hash})",
        )
        print()
        self.console.success("Your vote has been recorded successfully!")
        print(f"  {themes.DIM}Vote Reference:{themes.RESET} {themes.BRIGHT_YELLOW}{vote_hash}{themes.RESET}")
        print(f"  {themes.BRIGHT_CYAN}Thank you for participating in the democratic process!{themes.RESET}")
        self.persist()
        self.console.pause()

    def view_voting_history(self) -> None:
        current_user = self._current_voter()
        self.console.clear_screen()
        self.console.header("MY VOTING HISTORY", themes.THEME_VOTER)
        voted_polls = current_user.get("has_voted_in", [])
        if not voted_polls:
            print()
            self.console.info("You have not voted in any polls yet.")
            self.console.pause()
            return

        print(f"\n  {themes.DIM}You have voted in {len(voted_polls)} poll(s):{themes.RESET}\n")
        for poll_id in voted_polls:
            poll = self.state.polls.get(poll_id)
            if poll is None:
                continue
            status_color = themes.GREEN if poll["status"] == "open" else themes.RED
            print(f"  {themes.BOLD}{themes.THEME_VOTER}Poll #{poll_id}: {poll['title']}{themes.RESET}")
            print(
                f"  {themes.DIM}Type:{themes.RESET} {poll['election_type']}  "
                f"{themes.DIM}│  Status:{themes.RESET} {status_color}{poll['status'].upper()}{themes.RESET}"
            )
            voter_records = [
                vote
                for vote in self.state.votes
                if vote["poll_id"] == poll_id and vote["voter_id"] == current_user["id"]
            ]
            for vote_record in voter_records:
                position_title = next(
                    (
                        position["position_title"]
                        for position in poll.get("positions", [])
                        if position["position_id"] == vote_record["position_id"]
                    ),
                    "Unknown",
                )
                if vote_record["abstained"]:
                    print(
                        f"    {themes.THEME_VOTER_ACCENT}▸{themes.RESET} {position_title}: "
                        f"{themes.GRAY}ABSTAINED{themes.RESET}"
                    )
                else:
                    candidate_name = self.state.candidates.get(vote_record["candidate_id"], {}).get(
                        "full_name",
                        "Unknown",
                    )
                    print(
                        f"    {themes.THEME_VOTER_ACCENT}▸{themes.RESET} {position_title}: "
                        f"{themes.BRIGHT_GREEN}{candidate_name}{themes.RESET}"
                    )
            print()
        self.console.pause()

    def view_voter_profile(self) -> None:
        current_user = self._current_voter()
        self.console.clear_screen()
        self.console.header("MY PROFILE", themes.THEME_VOTER)
        station_name = self.state.voting_stations.get(current_user["station_id"], {}).get(
            "name",
            "Unknown",
        )
        print()
        profile_rows = [
            ("Name", current_user["full_name"]),
            ("National ID", current_user["national_id"]),
            ("Voter Card", f"{themes.BRIGHT_YELLOW}{current_user['voter_card_number']}{themes.RESET}"),
            ("Date of Birth", current_user["date_of_birth"]),
            ("Age", current_user["age"]),
            ("Gender", current_user["gender"]),
            ("Address", current_user["address"]),
            ("Phone", current_user["phone"]),
            ("Email", current_user["email"]),
            ("Station", station_name),
            (
                "Verified",
                self.console.status_badge("Yes", True)
                if current_user["is_verified"]
                else self.console.status_badge("No", False),
            ),
            ("Registered", current_user["registered_at"]),
            ("Polls Voted", len(current_user.get("has_voted_in", []))),
        ]
        for label, value in profile_rows:
            print(f"  {themes.THEME_VOTER}{label + ':':<16}{themes.RESET} {value}")
        self.console.pause()
