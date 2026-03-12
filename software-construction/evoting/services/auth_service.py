from __future__ import annotations

import hashlib
import random
import string

from evoting.domain.constants import MIN_VOTER_AGE, VALID_GENDERS, VOTER_CARD_LENGTH
from evoting.domain.state import timestamp_now
from evoting.domain.validators import (
    ValidationError,
    ensure_matches,
    ensure_non_empty,
    ensure_password_length,
    ensure_unique_national_id,
    parse_birth_date_and_age,
)
from evoting.services.base import BaseService
from evoting.ui import themes


class AuthService(BaseService):
    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def generate_voter_card_number(self) -> str:
        alphabet = string.ascii_uppercase + string.digits
        existing_cards = {voter["voter_card_number"] for voter in self.state.voters.values()}
        while True:
            card_number = "".join(random.choices(alphabet, k=VOTER_CARD_LENGTH))
            if card_number not in existing_cards:
                return card_number

    def login_admin(self) -> bool:
        self.show_screen("ADMIN LOGIN", themes.THEME_ADMIN)
        print()
        username = self.console.prompt("Username: ")
        password = self.console.masked_input("Password: ").strip()
        hashed_password = self.hash_password(password)

        for admin in self.state.admins.values():
            if admin["username"] != username or admin["password"] != hashed_password:
                continue
            if not admin["is_active"]:
                self.console.error("This account has been deactivated.")
                self.audit.log("LOGIN_FAILED", username, "Account deactivated")
                self.console.pause()
                return False
            self.state.current_user = admin
            self.state.current_role = "admin"
            self.audit.log("LOGIN", username, "Admin login successful")
            print()
            self.console.success(f"Welcome, {admin['full_name']}!")
            self.console.pause()
            return True

        self.console.error("Invalid credentials.")
        self.audit.log("LOGIN_FAILED", username, "Invalid admin credentials")
        self.console.pause()
        return False

    def login_voter(self) -> bool:
        self.show_screen("VOTER LOGIN", themes.THEME_VOTER)
        print()
        voter_card = self.console.prompt("Voter Card Number: ")
        password = self.console.masked_input("Password: ").strip()
        hashed_password = self.hash_password(password)

        for voter in self.state.voters.values():
            if voter["voter_card_number"] != voter_card or voter["password"] != hashed_password:
                continue
            if not voter["is_active"]:
                self.console.error("This voter account has been deactivated.")
                self.audit.log("LOGIN_FAILED", voter_card, "Voter account deactivated")
                self.console.pause()
                return False
            if not voter["is_verified"]:
                self.console.warning("Your voter registration has not been verified yet.")
                self.console.info("Please contact an admin to verify your registration.")
                self.audit.log("LOGIN_FAILED", voter_card, "Voter not verified")
                self.console.pause()
                return False
            self.state.current_user = voter
            self.state.current_role = "voter"
            self.audit.log("LOGIN", voter_card, "Voter login successful")
            print()
            self.console.success(f"Welcome, {voter['full_name']}!")
            self.console.pause()
            return True

        self.console.error("Invalid voter card number or password.")
        self.audit.log("LOGIN_FAILED", voter_card, "Invalid voter credentials")
        self.console.pause()
        return False

    def register_voter(self) -> None:
        self.show_screen("VOTER REGISTRATION", themes.THEME_VOTER)
        print()

        try:
            full_name = ensure_non_empty(self.console.prompt("Full Name: "), "Name")
            national_id = ensure_unique_national_id(
                self.state.voters,
                self.console.prompt("National ID Number: "),
                "voter",
            )
            age_data = parse_birth_date_and_age(
                self.console.prompt("Date of Birth (YYYY-MM-DD): ")
            )
            if age_data.age < MIN_VOTER_AGE:
                raise ValidationError(
                    f"You must be at least {MIN_VOTER_AGE} years old to register."
                )
            gender = self.console.prompt("Gender (M/F/Other): ").upper()
            if gender not in VALID_GENDERS:
                raise ValidationError("Invalid gender selection.")
            address = self.console.prompt("Residential Address: ")
            phone = self.console.prompt("Phone Number: ")
            email = self.console.prompt("Email Address: ")
            password = ensure_password_length(
                self.console.masked_input("Create Password: ").strip()
            )
            confirm_password = self.console.masked_input("Confirm Password: ").strip()
            ensure_matches(password, confirm_password, "Passwords do not match.")
        except ValidationError as error:
            self.console.error(str(error))
            self.console.pause()
            return

        if not self.state.voting_stations:
            self.console.error("No voting stations available. Contact admin.")
            self.console.pause()
            return

        active_stations = {
            station_id: station
            for station_id, station in self.state.voting_stations.items()
            if station["is_active"]
        }
        if not active_stations:
            self.console.error("No active voting stations available. Contact admin.")
            self.console.pause()
            return

        self.console.subheader("Available Voting Stations", themes.THEME_VOTER)
        for station_id, station in active_stations.items():
            print(
                f"    {themes.BRIGHT_BLUE}{station_id}.{themes.RESET} {station['name']} "
                f"{themes.DIM}- {station['location']}{themes.RESET}"
            )
        try:
            station_choice = int(self.console.prompt("\nSelect your voting station ID: "))
        except ValueError:
            self.console.error("Invalid input.")
            self.console.pause()
            return
        if station_choice not in active_stations:
            self.console.error("Invalid station selection.")
            self.console.pause()
            return

        voter_card = self.generate_voter_card_number()
        voter_id = self.state.voter_id_counter
        self.state.voters[voter_id] = {
            "id": voter_id,
            "full_name": full_name,
            "national_id": national_id,
            "date_of_birth": age_data.birth_date.strftime("%Y-%m-%d"),
            "age": age_data.age,
            "gender": gender,
            "address": address,
            "phone": phone,
            "email": email,
            "password": self.hash_password(password),
            "voter_card_number": voter_card,
            "station_id": station_choice,
            "is_verified": False,
            "is_active": True,
            "has_voted_in": [],
            "registered_at": timestamp_now(),
            "role": "voter",
        }
        self.state.voter_id_counter += 1
        self.audit.log("REGISTER", full_name, f"New voter registered with card: {voter_card}")
        print()
        self.console.success("Registration successful!")
        print(
            f"  {themes.BOLD}Your Voter Card Number: "
            f"{themes.BRIGHT_YELLOW}{voter_card}{themes.RESET}"
        )
        self.console.warning("IMPORTANT: Save this number! You need it to login.")
        self.console.info("Your registration is pending admin verification.")
        self.persist()
        self.console.pause()

    def change_voter_password(self) -> None:
        current_user = self.state.current_user
        if current_user is None:
            self.console.error("No voter is currently logged in.")
            self.console.pause()
            return

        self.show_screen("CHANGE PASSWORD", themes.THEME_VOTER)
        print()
        old_password = self.console.masked_input("Current Password: ").strip()
        if self.hash_password(old_password) != current_user["password"]:
            self.console.error("Incorrect current password.")
            self.console.pause()
            return
        try:
            new_password = ensure_password_length(
                self.console.masked_input("New Password: ").strip()
            )
            confirm_password = self.console.masked_input("Confirm New Password: ").strip()
            ensure_matches(new_password, confirm_password, "Passwords do not match.")
        except ValidationError as error:
            self.console.error(str(error))
            self.console.pause()
            return

        current_user["password"] = self.hash_password(new_password)
        self.audit.log("CHANGE_PASSWORD", current_user["voter_card_number"], "Password changed")
        print()
        self.console.success("Password changed successfully!")
        self.persist()
        self.console.pause()
