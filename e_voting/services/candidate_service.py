import datetime

from e_voting.constants import (
    MIN_CANDIDATE_AGE, MAX_CANDIDATE_AGE, REQUIRED_EDUCATION_LEVELS,
)
from e_voting.models.candidate import Candidate


class CandidateService:
    """Business logic for candidate management."""

    def __init__(self, store):
        self._store = store

    def is_national_id_unique(self, national_id):
        return all(
            c.national_id != national_id
            for c in self._store.candidates.values()
        )

    def validate_candidate_age(self, dob_str):
        """Returns (age, None) on success, or (None, error_msg) on failure."""
        try:
            dob = datetime.datetime.strptime(dob_str, "%Y-%m-%d")
            age = (datetime.datetime.now() - dob).days // 365
        except ValueError:
            return None, "Invalid date format."

        if age < MIN_CANDIDATE_AGE:
            return None, (f"Candidate must be at least {MIN_CANDIDATE_AGE} "
                          f"years old. Current age: {age}")
        if age > MAX_CANDIDATE_AGE:
            return None, (f"Candidate must not be older than "
                          f"{MAX_CANDIDATE_AGE}. Current age: {age}")
        return age, None

    def create(self, full_name, national_id, dob_str, age, gender, education,
               party, manifesto, address, phone, email, years_experience,
               created_by):
        candidate_id = self._store.next_id("candidate")
        candidate = Candidate(
            candidate_id=candidate_id,
            full_name=full_name,
            national_id=national_id,
            date_of_birth=dob_str,
            age=age,
            gender=gender,
            education=education,
            party=party,
            manifesto=manifesto,
            address=address,
            phone=phone,
            email=email,
            years_experience=years_experience,
            created_by=created_by,
        )
        self._store.candidates[candidate_id] = candidate
        self._store.log_action(
            "CREATE_CANDIDATE", created_by,
            f"Created candidate: {full_name} (ID: {candidate_id})"
        )
        self._store.save()
        return candidate

    def get_all(self):
        return self._store.candidates

    def get(self, candidate_id):
        return self._store.candidates.get(candidate_id)

    def update(self, candidate_id, updates, updated_by):
        candidate = self._store.candidates.get(candidate_id)
        if not candidate:
            return None
        for key, value in updates.items():
            if value is not None and hasattr(candidate, key):
                setattr(candidate, key, value)
        self._store.log_action(
            "UPDATE_CANDIDATE", updated_by,
            f"Updated candidate: {candidate.full_name} (ID: {candidate_id})"
        )
        self._store.save()
        return candidate

    def can_deactivate(self, candidate_id):
        """Returns (True, None) if safe, or (False, reason) if not."""
        for poll in self._store.polls.values():
            if poll.is_open():
                for pos in poll.positions:
                    if candidate_id in pos.candidate_ids:
                        return False, (
                            f"Cannot delete - candidate is in active poll: "
                            f"{poll.title}"
                        )
        return True, None

    def deactivate(self, candidate_id, deactivated_by):
        candidate = self._store.candidates.get(candidate_id)
        if not candidate:
            return False
        candidate.deactivate()
        self._store.log_action(
            "DELETE_CANDIDATE", deactivated_by,
            f"Deactivated candidate: {candidate.full_name} "
            f"(ID: {candidate_id})"
        )
        self._store.save()
        return True

    def search_by_name(self, term):
        term_lower = term.lower()
        return [
            c for c in self._store.candidates.values()
            if term_lower in c.full_name.lower()
        ]

    def search_by_party(self, term):
        term_lower = term.lower()
        return [
            c for c in self._store.candidates.values()
            if term_lower in c.party.lower()
        ]

    def search_by_education(self, education):
        return [
            c for c in self._store.candidates.values()
            if c.education == education
        ]

    def search_by_age_range(self, min_age, max_age):
        return [
            c for c in self._store.candidates.values()
            if min_age <= c.age <= max_age
        ]
