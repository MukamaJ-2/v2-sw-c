import datetime
import hashlib
import json
import os

from e_voting.constants import DATA_FILE_PATH
from e_voting.models.admin import Admin
from e_voting.models.candidate import Candidate
from e_voting.models.poll import Poll
from e_voting.models.position import Position
from e_voting.models.vote import Vote
from e_voting.models.voter import Voter
from e_voting.models.voting_station import VotingStation


class DataStore:
    """Central data persistence layer. Holds all entity collections,
    manages ID counters, session state, and JSON serialization."""

    def __init__(self):
        self.candidates = {}
        self.voters = {}
        self.admins = {}
        self.voting_stations = {}
        self.polls = {}
        self.positions = {}
        self.votes = []
        self.audit_log = []

        self._id_counters = {
            "candidate": 1,
            "voter": 1,
            "admin": 2,
            "station": 1,
            "poll": 1,
            "position": 1,
        }

        self.current_user = None
        self.current_role = None

        self._init_default_admin()

    def _init_default_admin(self):
        default_admin = Admin(
            admin_id=1,
            username="admin",
            password=hashlib.sha256("admin123".encode()).hexdigest(),
            full_name="System Administrator",
            email="admin@evote.com",
            role="super_admin",
        )
        self.admins[1] = default_admin

    def next_id(self, entity_type):
        current = self._id_counters[entity_type]
        self._id_counters[entity_type] = current + 1
        return current

    def log_action(self, action, user, details):
        self.audit_log.append({
            "timestamp": str(datetime.datetime.now()),
            "action": action,
            "user": user,
            "details": details,
        })

    def login(self, user, role):
        self.current_user = user
        self.current_role = role

    def logout(self):
        self.current_user = None
        self.current_role = None

    @property
    def is_logged_in(self):
        return self.current_user is not None

    def save(self):
        data = {
            "candidates": {
                str(k): v.to_dict() for k, v in self.candidates.items()
            },
            "candidate_id_counter": self._id_counters["candidate"],
            "voting_stations": {
                str(k): v.to_dict() for k, v in self.voting_stations.items()
            },
            "station_id_counter": self._id_counters["station"],
            "polls": {
                str(k): v.to_dict() for k, v in self.polls.items()
            },
            "poll_id_counter": self._id_counters["poll"],
            "positions": {
                str(k): v.to_dict() for k, v in self.positions.items()
            },
            "position_id_counter": self._id_counters["position"],
            "voters": {
                str(k): v.to_dict() for k, v in self.voters.items()
            },
            "voter_id_counter": self._id_counters["voter"],
            "admins": {
                str(k): v.to_dict() for k, v in self.admins.items()
            },
            "admin_id_counter": self._id_counters["admin"],
            "votes": [v.to_dict() for v in self.votes],
            "audit_log": self.audit_log,
        }
        try:
            with open(DATA_FILE_PATH, "w") as file_handle:
                json.dump(data, file_handle, indent=2)
        except OSError as exc:
            raise IOError(f"Error saving data: {exc}") from exc

    def load(self):
        if not os.path.exists(DATA_FILE_PATH):
            return

        try:
            with open(DATA_FILE_PATH, "r") as file_handle:
                data = json.load(file_handle)
        except (OSError, json.JSONDecodeError) as exc:
            raise IOError(f"Error loading data: {exc}") from exc

        self.candidates = {
            int(k): Candidate.from_dict(v)
            for k, v in data.get("candidates", {}).items()
        }
        self._id_counters["candidate"] = data.get("candidate_id_counter", 1)

        self.voting_stations = {
            int(k): VotingStation.from_dict(v)
            for k, v in data.get("voting_stations", {}).items()
        }
        self._id_counters["station"] = data.get("station_id_counter", 1)

        self.polls = {
            int(k): Poll.from_dict(v)
            for k, v in data.get("polls", {}).items()
        }
        self._id_counters["poll"] = data.get("poll_id_counter", 1)

        self.positions = {
            int(k): Position.from_dict(v)
            for k, v in data.get("positions", {}).items()
        }
        self._id_counters["position"] = data.get("position_id_counter", 1)

        self.voters = {
            int(k): Voter.from_dict(v)
            for k, v in data.get("voters", {}).items()
        }
        self._id_counters["voter"] = data.get("voter_id_counter", 1)

        self.admins = {
            int(k): Admin.from_dict(v)
            for k, v in data.get("admins", {}).items()
        }
        self._id_counters["admin"] = data.get("admin_id_counter", 1)

        self.votes = [
            Vote.from_dict(v) for v in data.get("votes", [])
        ]
        self.audit_log = data.get("audit_log", [])
