from __future__ import annotations

from evoting.services.base import BaseService
from evoting.ui import themes


class VoterService(BaseService):
    def _render_voter_choice(self, voter: dict, details: str = "") -> str:
        return f"  {themes.THEME_ADMIN}{voter['id']}.{themes.RESET} {voter['full_name']}{details}"

    def view_all_voters(self) -> None:
        self.show_screen("ALL REGISTERED VOTERS", themes.THEME_ADMIN)
        if not self.require_records(self.state.voters, "No voters registered."):
            return

        print()
        self.console.table_header(
            f"{'ID':<5} {'Name':<25} {'Card Number':<15} {'Stn':<6} {'Verified':<10} {'Active':<8}",
            themes.THEME_ADMIN,
        )
        self.console.table_divider(70, themes.THEME_ADMIN)
        for voter in self.state.voters.values():
            verified = self.console.status_badge("Yes", True) if voter["is_verified"] else self.console.status_badge("No", False)
            active = self.console.status_badge("Yes", True) if voter["is_active"] else self.console.status_badge("No", False)
            print(
                f"  {voter['id']:<5} {voter['full_name']:<25} {voter['voter_card_number']:<15} "
                f"{voter['station_id']:<6} {verified:<19} {active}"
            )
        verified_count = sum(1 for voter in self.state.voters.values() if voter["is_verified"])
        unverified_count = sum(1 for voter in self.state.voters.values() if not voter["is_verified"])
        print(
            f"\n  {themes.DIM}Total: {len(self.state.voters)}  │  Verified: "
            f"{verified_count}  │  Unverified: {unverified_count}{themes.RESET}"
        )
        self.console.pause()

    def verify_voter(self) -> None:
        current_user = self.state.current_user
        self.show_screen("VERIFY VOTER", themes.THEME_ADMIN)
        unverified = {
            voter_id: voter
            for voter_id, voter in self.state.voters.items()
            if not voter["is_verified"]
        }
        if not self.require_records(unverified, "No unverified voters."):
            return

        self.console.subheader("Unverified Voters", themes.THEME_ADMIN_ACCENT)
        for voter in unverified.values():
            print(
                f"  {themes.THEME_ADMIN}{voter['id']}.{themes.RESET} {voter['full_name']} "
                f"{themes.DIM}│ NID: {voter['national_id']} │ Card: {voter['voter_card_number']}{themes.RESET}"
            )
        print()
        self.console.menu_item(1, "Verify a single voter", themes.THEME_ADMIN)
        self.console.menu_item(2, "Verify all pending voters", themes.THEME_ADMIN)
        choice = self.console.prompt("\nChoice: ")
        if choice == "1":
            voter_id, voter = self.select_record(
                self.state.voters,
                lambda item: self._render_voter_choice(
                    item,
                    f" {themes.DIM}│ Card: {item['voter_card_number']}{themes.RESET}",
                ),
                "Enter Voter ID: ",
                "Voter not found.",
            )
            if voter is None:
                return
            if voter["is_verified"]:
                self.console.info("Already verified.")
                self.console.pause()
                return
            voter["is_verified"] = True
            self.audit.log(
                "VERIFY_VOTER",
                current_user["username"],
                f"Verified voter: {voter['full_name']}",
            )
            print()
            self.console.success(f"Voter '{voter['full_name']}' verified!")
            self.persist()
        elif choice == "2":
            count = 0
            for voter in unverified.values():
                voter["is_verified"] = True
                count += 1
            self.audit.log(
                "VERIFY_ALL_VOTERS",
                current_user["username"],
                f"Verified {count} voters",
            )
            print()
            self.console.success(f"{count} voters verified!")
            self.persist()
        self.console.pause()

    def deactivate_voter(self) -> None:
        current_user = self.state.current_user
        self.show_screen("DEACTIVATE VOTER", themes.THEME_ADMIN)
        if not self.require_records(self.state.voters, "No voters found."):
            return

        voter_id, voter = self.select_record(
            self.state.voters,
            lambda item: self._render_voter_choice(item, f" {themes.DIM}│ Card: {item['voter_card_number']}{themes.RESET}"),
            "Enter Voter ID to deactivate: ",
            "Voter not found.",
        )
        if voter is None:
            return
        if not voter["is_active"]:
            self.console.info("Already deactivated.")
            self.console.pause()
            return
        if self.confirm(f"Deactivate '{voter['full_name']}'? (yes/no): "):
            voter["is_active"] = False
            self.audit.log(
                "DEACTIVATE_VOTER",
                current_user["username"],
                f"Deactivated voter: {voter['full_name']}",
            )
            print()
            self.console.success("Voter deactivated.")
            self.persist()
        self.console.pause()

    def search_voters(self) -> None:
        self.show_screen("SEARCH VOTERS", themes.THEME_ADMIN)
        self.console.subheader("Search by", themes.THEME_ADMIN_ACCENT)
        self.console.menu_item(1, "Name", themes.THEME_ADMIN)
        self.console.menu_item(2, "Voter Card Number", themes.THEME_ADMIN)
        self.console.menu_item(3, "National ID", themes.THEME_ADMIN)
        self.console.menu_item(4, "Station", themes.THEME_ADMIN)
        choice = self.console.prompt("\nChoice: ")

        results: list[dict] = []
        if choice == "1":
            term = self.console.prompt("Name: ").lower()
            results = [
                voter for voter in self.state.voters.values() if term in voter["full_name"].lower()
            ]
        elif choice == "2":
            term = self.console.prompt("Card Number: ")
            results = [
                voter for voter in self.state.voters.values() if term == voter["voter_card_number"]
            ]
        elif choice == "3":
            term = self.console.prompt("National ID: ")
            results = [
                voter for voter in self.state.voters.values() if term == voter["national_id"]
            ]
        elif choice == "4":
            try:
                station_id = int(self.console.prompt("Station ID: "))
            except ValueError:
                self.console.error("Invalid input.")
                self.console.pause()
                return
            results = [
                voter for voter in self.state.voters.values() if voter["station_id"] == station_id
            ]
        else:
            self.console.error("Invalid choice.")
            self.console.pause()
            return

        if not results:
            print()
            self.console.info("No voters found.")
            self.console.pause()
            return

        print(f"\n  {themes.BOLD}Found {len(results)} voter(s):{themes.RESET}")
        for voter in results:
            verified = self.console.status_badge("Verified", True) if voter["is_verified"] else self.console.status_badge("Unverified", False)
            print(
                f"  {themes.THEME_ADMIN}ID:{themes.RESET} {voter['id']}  {themes.DIM}│{themes.RESET}  "
                f"{voter['full_name']}  {themes.DIM}│  Card:{themes.RESET} {voter['voter_card_number']}  "
                f"{themes.DIM}│{themes.RESET}  {verified}"
            )
        self.console.pause()
