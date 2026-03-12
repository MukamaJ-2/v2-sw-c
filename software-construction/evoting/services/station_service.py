from __future__ import annotations

from evoting.domain.state import timestamp_now
from evoting.domain.validators import ValidationError, ensure_non_empty, parse_positive_int
from evoting.services.base import BaseService
from evoting.ui import themes


class StationService(BaseService):
    def _render_station_choice(self, station: dict, include_status: bool = False) -> str:
        suffix = f" {themes.DIM}- {station['location']}{themes.RESET}"
        if include_status:
            status = (
                self.console.status_badge("Active", True)
                if station["is_active"]
                else self.console.status_badge("Inactive", False)
            )
            suffix = f" {themes.DIM}({station['location']}){themes.RESET} {status}"
        return f"  {themes.THEME_ADMIN}{station['id']}.{themes.RESET} {station['name']}{suffix}"

    def create_voting_station(self) -> None:
        current_user = self.state.current_user
        self.show_screen("CREATE VOTING STATION", themes.THEME_ADMIN)
        print()
        try:
            name = ensure_non_empty(self.console.prompt("Station Name: "), "Name")
            location = ensure_non_empty(self.console.prompt("Location/Address: "), "Location")
            region = self.console.prompt("Region/District: ")
            capacity = parse_positive_int(self.console.prompt("Voter Capacity: "), "Capacity")
        except ValidationError as error:
            self.console.error(str(error))
            self.console.pause()
            return

        supervisor = self.console.prompt("Station Supervisor Name: ")
        contact = self.console.prompt("Contact Phone: ")
        opening_time = self.console.prompt("Opening Time (e.g. 08:00): ")
        closing_time = self.console.prompt("Closing Time (e.g. 17:00): ")

        station_id = self.state.station_id_counter
        self.state.voting_stations[station_id] = {
            "id": station_id,
            "name": name,
            "location": location,
            "region": region,
            "capacity": capacity,
            "registered_voters": 0,
            "supervisor": supervisor,
            "contact": contact,
            "opening_time": opening_time,
            "closing_time": closing_time,
            "is_active": True,
            "created_at": timestamp_now(),
            "created_by": current_user["username"],
        }
        self.state.station_id_counter += 1
        self.audit.log(
            "CREATE_STATION",
            current_user["username"],
            f"Created station: {name} (ID: {station_id})",
        )
        print()
        self.console.success(f"Voting Station '{name}' created! ID: {station_id}")
        self.persist()
        self.console.pause()

    def view_all_stations(self) -> None:
        self.show_screen("ALL VOTING STATIONS", themes.THEME_ADMIN)
        if not self.require_records(self.state.voting_stations, "No voting stations found."):
            return

        print()
        self.console.table_header(
            f"{'ID':<5} {'Name':<25} {'Location':<25} {'Region':<15} {'Cap.':<8} {'Reg.':<8} {'Status':<10}",
            themes.THEME_ADMIN,
        )
        self.console.table_divider(96, themes.THEME_ADMIN)
        for station_id, station in self.state.voting_stations.items():
            registered_count = sum(
                1 for voter in self.state.voters.values() if voter["station_id"] == station_id
            )
            status = self.console.status_badge("Active", True) if station["is_active"] else self.console.status_badge("Inactive", False)
            print(
                f"  {station['id']:<5} {station['name']:<25} {station['location']:<25} "
                f"{station['region']:<15} {station['capacity']:<8} {registered_count:<8} {status}"
            )
        print(f"\n  {themes.DIM}Total Stations: {len(self.state.voting_stations)}{themes.RESET}")
        self.console.pause()

    def update_station(self) -> None:
        current_user = self.state.current_user
        self.show_screen("UPDATE VOTING STATION", themes.THEME_ADMIN)
        if not self.require_records(self.state.voting_stations, "No stations found."):
            return
        station_id, station = self.select_record(
            self.state.voting_stations,
            self._render_station_choice,
            "\nEnter Station ID to update: ",
            "Station not found.",
        )
        if station is None:
            return

        print(f"\n  {themes.BOLD}Updating: {station['name']}{themes.RESET}")
        self.console.info("Press Enter to keep current value\n")
        new_name = self.console.prompt(f"Name [{station['name']}]: ")
        if new_name:
            station["name"] = new_name
        new_location = self.console.prompt(f"Location [{station['location']}]: ")
        if new_location:
            station["location"] = new_location
        new_region = self.console.prompt(f"Region [{station['region']}]: ")
        if new_region:
            station["region"] = new_region
        new_capacity = self.console.prompt(f"Capacity [{station['capacity']}]: ")
        if new_capacity:
            try:
                station["capacity"] = int(new_capacity)
            except ValueError:
                self.console.warning("Invalid number, keeping old value.")
        new_supervisor = self.console.prompt(f"Supervisor [{station['supervisor']}]: ")
        if new_supervisor:
            station["supervisor"] = new_supervisor
        new_contact = self.console.prompt(f"Contact [{station['contact']}]: ")
        if new_contact:
            station["contact"] = new_contact

        self.audit.log(
            "UPDATE_STATION",
            current_user["username"],
            f"Updated station: {station['name']} (ID: {station_id})",
        )
        print()
        self.console.success(f"Station '{station['name']}' updated successfully!")
        self.persist()
        self.console.pause()

    def delete_station(self) -> None:
        current_user = self.state.current_user
        self.show_screen("DELETE VOTING STATION", themes.THEME_ADMIN)
        if not self.require_records(self.state.voting_stations, "No stations found."):
            return
        station_id, station = self.select_record(
            self.state.voting_stations,
            lambda item: self._render_station_choice(item, include_status=True),
            "\nEnter Station ID to delete: ",
            "Station not found.",
        )
        if station is None:
            return

        voter_count = sum(1 for voter in self.state.voters.values() if voter["station_id"] == station_id)
        if voter_count > 0:
            self.console.warning(f"{voter_count} voters are registered at this station.")
            if not self.confirm("Proceed with deactivation? (yes/no): "):
                self.console.info("Cancelled.")
                self.console.pause()
                return

        if self.confirm(f"Confirm deactivation of '{station['name']}'? (yes/no): "):
            station["is_active"] = False
            self.audit.log(
                "DELETE_STATION",
                current_user["username"],
                f"Deactivated station: {station['name']}",
            )
            print()
            self.console.success(f"Station '{station['name']}' deactivated.")
            self.persist()
        else:
            self.console.info("Cancelled.")
        self.console.pause()
