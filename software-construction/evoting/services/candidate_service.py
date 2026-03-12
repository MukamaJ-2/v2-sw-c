from __future__ import annotations

from evoting.domain.constants import (
    MAX_CANDIDATE_AGE,
    MIN_CANDIDATE_AGE,
    REQUIRED_EDUCATION_LEVELS,
)
from evoting.domain.state import timestamp_now
from evoting.domain.validators import (
    ValidationError,
    ensure_non_empty,
    ensure_unique_national_id,
    parse_birth_date_and_age,
)
from evoting.services.base import BaseService
from evoting.ui import themes


class CandidateService(BaseService):
    def _render_candidate_choice(self, candidate: dict, include_status: bool = False) -> str:
        suffix = f" {themes.DIM}({candidate['party']}){themes.RESET}"
        if include_status:
            status = (
                self.console.status_badge("Active", True)
                if candidate["is_active"]
                else self.console.status_badge("Inactive", False)
            )
            suffix = f"{suffix} {status}"
        return (
            f"  {themes.THEME_ADMIN}{candidate['id']}.{themes.RESET} "
            f"{candidate['full_name']}{suffix}"
        )

    def create_candidate(self) -> None:
        current_user = self.state.current_user
        self.show_screen("CREATE NEW CANDIDATE", themes.THEME_ADMIN)
        print()

        try:
            full_name = ensure_non_empty(self.console.prompt("Full Name: "), "Name")
            national_id = ensure_unique_national_id(
                self.state.candidates,
                self.console.prompt("National ID: "),
                "candidate",
            )
            age_data = parse_birth_date_and_age(self.console.prompt("Date of Birth (YYYY-MM-DD): "))
            if age_data.age < MIN_CANDIDATE_AGE:
                raise ValidationError(
                    f"Candidate must be at least {MIN_CANDIDATE_AGE} years old. Current age: {age_data.age}"
                )
            if age_data.age > MAX_CANDIDATE_AGE:
                raise ValidationError(
                    f"Candidate must not be older than {MAX_CANDIDATE_AGE}. Current age: {age_data.age}"
                )
            gender = self.console.prompt("Gender (M/F/Other): ").upper()
        except ValidationError as error:
            self.console.error(str(error))
            self.console.pause()
            return

        self.console.subheader("Education Levels", themes.THEME_ADMIN_ACCENT)
        for index, level in enumerate(REQUIRED_EDUCATION_LEVELS, start=1):
            print(f"    {themes.THEME_ADMIN}{index}.{themes.RESET} {level}")
        try:
            education_choice = int(self.console.prompt("Select education level: "))
            education = REQUIRED_EDUCATION_LEVELS[education_choice - 1]
        except (ValueError, IndexError):
            self.console.error("Invalid choice.")
            self.console.pause()
            return

        party = self.console.prompt("Political Party/Affiliation: ")
        manifesto = self.console.prompt("Brief Manifesto/Bio: ")
        address = self.console.prompt("Address: ")
        phone = self.console.prompt("Phone: ")
        email = self.console.prompt("Email: ")
        criminal_record = self.console.prompt("Has Criminal Record? (yes/no): ").lower()
        if criminal_record == "yes":
            self.console.error("Candidates with criminal records are not eligible.")
            self.audit.log(
                "CANDIDATE_REJECTED",
                current_user["username"],
                f"Candidate {full_name} rejected - criminal record",
            )
            self.console.pause()
            return

        experience_text = self.console.prompt(
            "Years of Public Service/Political Experience: "
        )
        try:
            years_experience = int(experience_text)
        except ValueError:
            years_experience = 0

        candidate_id = self.state.candidate_id_counter
        self.state.candidates[candidate_id] = {
            "id": candidate_id,
            "full_name": full_name,
            "national_id": national_id,
            "date_of_birth": age_data.birth_date.strftime("%Y-%m-%d"),
            "age": age_data.age,
            "gender": gender,
            "education": education,
            "party": party,
            "manifesto": manifesto,
            "address": address,
            "phone": phone,
            "email": email,
            "has_criminal_record": False,
            "years_experience": years_experience,
            "is_active": True,
            "is_approved": True,
            "created_at": timestamp_now(),
            "created_by": current_user["username"],
        }
        self.state.candidate_id_counter += 1
        self.audit.log(
            "CREATE_CANDIDATE",
            current_user["username"],
            f"Created candidate: {full_name} (ID: {candidate_id})",
        )
        print()
        self.console.success(f"Candidate '{full_name}' created successfully! ID: {candidate_id}")
        self.persist()
        self.console.pause()

    def view_all_candidates(self) -> None:
        self.show_screen("ALL CANDIDATES", themes.THEME_ADMIN)
        if not self.require_records(self.state.candidates, "No candidates found."):
            return

        print()
        self.console.table_header(
            f"{'ID':<5} {'Name':<25} {'Party':<20} {'Age':<5} {'Education':<20} {'Status':<10}",
            themes.THEME_ADMIN,
        )
        self.console.table_divider(85, themes.THEME_ADMIN)
        for candidate in self.state.candidates.values():
            status = self.console.status_badge("Active", True) if candidate["is_active"] else self.console.status_badge("Inactive", False)
            print(
                f"  {candidate['id']:<5} {candidate['full_name']:<25} {candidate['party']:<20} "
                f"{candidate['age']:<5} {candidate['education']:<20} {status}"
            )
        print(f"\n  {themes.DIM}Total Candidates: {len(self.state.candidates)}{themes.RESET}")
        self.console.pause()

    def update_candidate(self) -> None:
        current_user = self.state.current_user
        self.show_screen("UPDATE CANDIDATE", themes.THEME_ADMIN)
        if not self.require_records(self.state.candidates, "No candidates found."):
            return

        candidate_id, candidate = self.select_record(
            self.state.candidates,
            self._render_candidate_choice,
            "\nEnter Candidate ID to update: ",
            "Candidate not found.",
        )
        if candidate is None:
            return

        print(f"\n  {themes.BOLD}Updating: {candidate['full_name']}{themes.RESET}")
        self.console.info("Press Enter to keep current value\n")
        new_name = self.console.prompt(f"Full Name [{candidate['full_name']}]: ")
        if new_name:
            candidate["full_name"] = new_name
        new_party = self.console.prompt(f"Party [{candidate['party']}]: ")
        if new_party:
            candidate["party"] = new_party
        new_manifesto = self.console.prompt(f"Manifesto [{candidate['manifesto'][:50]}...]: ")
        if new_manifesto:
            candidate["manifesto"] = new_manifesto
        new_phone = self.console.prompt(f"Phone [{candidate['phone']}]: ")
        if new_phone:
            candidate["phone"] = new_phone
        new_email = self.console.prompt(f"Email [{candidate['email']}]: ")
        if new_email:
            candidate["email"] = new_email
        new_address = self.console.prompt(f"Address [{candidate['address']}]: ")
        if new_address:
            candidate["address"] = new_address
        new_experience = self.console.prompt(f"Years Experience [{candidate['years_experience']}]: ")
        if new_experience:
            try:
                candidate["years_experience"] = int(new_experience)
            except ValueError:
                self.console.warning("Invalid number, keeping old value.")
        self.audit.log(
            "UPDATE_CANDIDATE",
            current_user["username"],
            f"Updated candidate: {candidate['full_name']} (ID: {candidate_id})",
        )
        print()
        self.console.success(f"Candidate '{candidate['full_name']}' updated successfully!")
        self.persist()
        self.console.pause()

    def delete_candidate(self) -> None:
        current_user = self.state.current_user
        self.show_screen("DELETE CANDIDATE", themes.THEME_ADMIN)
        if not self.require_records(self.state.candidates, "No candidates found."):
            return

        candidate_id, candidate = self.select_record(
            self.state.candidates,
            lambda item: self._render_candidate_choice(item, include_status=True),
            "\nEnter Candidate ID to delete: ",
            "Candidate not found.",
        )
        if candidate is None:
            return

        for poll in self.state.polls.values():
            if poll["status"] != "open":
                continue
            for position in poll.get("positions", []):
                if candidate_id in position.get("candidate_ids", []):
                    self.console.error(
                        f"Cannot delete - candidate is in active poll: {poll['title']}"
                    )
                    self.console.pause()
                    return

        if self.confirm(f"Are you sure you want to delete '{candidate['full_name']}'? (yes/no): "):
            candidate["is_active"] = False
            self.audit.log(
                "DELETE_CANDIDATE",
                current_user["username"],
                f"Deactivated candidate: {candidate['full_name']} (ID: {candidate_id})",
            )
            print()
            self.console.success(f"Candidate '{candidate['full_name']}' has been deactivated.")
            self.persist()
        else:
            self.console.info("Deletion cancelled.")
        self.console.pause()

    def search_candidates(self) -> None:
        self.show_screen("SEARCH CANDIDATES", themes.THEME_ADMIN)
        self.console.subheader("Search by", themes.THEME_ADMIN_ACCENT)
        self.console.menu_item(1, "Name", themes.THEME_ADMIN)
        self.console.menu_item(2, "Party", themes.THEME_ADMIN)
        self.console.menu_item(3, "Education Level", themes.THEME_ADMIN)
        self.console.menu_item(4, "Age Range", themes.THEME_ADMIN)
        choice = self.console.prompt("\nChoice: ")

        results: list[dict] = []
        if choice == "1":
            term = self.console.prompt("Enter name to search: ").lower()
            results = [
                candidate
                for candidate in self.state.candidates.values()
                if term in candidate["full_name"].lower()
            ]
        elif choice == "2":
            term = self.console.prompt("Enter party name: ").lower()
            results = [
                candidate
                for candidate in self.state.candidates.values()
                if term in candidate["party"].lower()
            ]
        elif choice == "3":
            self.console.subheader("Education Levels", themes.THEME_ADMIN_ACCENT)
            for index, level in enumerate(REQUIRED_EDUCATION_LEVELS, start=1):
                print(f"    {themes.THEME_ADMIN}{index}.{themes.RESET} {level}")
            try:
                education_choice = int(self.console.prompt("Select: "))
                education = REQUIRED_EDUCATION_LEVELS[education_choice - 1]
            except (ValueError, IndexError):
                self.console.error("Invalid choice.")
                self.console.pause()
                return
            results = [
                candidate
                for candidate in self.state.candidates.values()
                if candidate["education"] == education
            ]
        elif choice == "4":
            try:
                min_age = int(self.console.prompt("Min age: "))
                max_age = int(self.console.prompt("Max age: "))
            except ValueError:
                self.console.error("Invalid input.")
                self.console.pause()
                return
            results = [
                candidate
                for candidate in self.state.candidates.values()
                if min_age <= candidate["age"] <= max_age
            ]
        else:
            self.console.error("Invalid choice.")
            self.console.pause()
            return

        if not results:
            print()
            self.console.info("No candidates found matching your criteria.")
            self.console.pause()
            return

        print(f"\n  {themes.BOLD}Found {len(results)} candidate(s):{themes.RESET}")
        self.console.table_header(
            f"{'ID':<5} {'Name':<25} {'Party':<20} {'Age':<5} {'Education':<20}",
            themes.THEME_ADMIN,
        )
        self.console.table_divider(75, themes.THEME_ADMIN)
        for candidate in results:
            print(
                f"  {candidate['id']:<5} {candidate['full_name']:<25} {candidate['party']:<20} "
                f"{candidate['age']:<5} {candidate['education']:<20}"
            )
        self.console.pause()
