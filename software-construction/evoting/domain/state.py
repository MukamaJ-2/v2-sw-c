from __future__ import annotations

import datetime
import hashlib
from dataclasses import dataclass, field
from typing import Any

from evoting.domain.constants import (
    DEFAULT_ADMIN_EMAIL,
    DEFAULT_ADMIN_FULL_NAME,
    DEFAULT_ADMIN_PASSWORD,
    DEFAULT_ADMIN_ROLE,
    DEFAULT_ADMIN_USERNAME,
)

Record = dict[str, Any]


def timestamp_now() -> str:
    return str(datetime.datetime.now())


def _normalize_int_keys(records: dict[Any, Any]) -> dict[int, Record]:
    return {int(key): value for key, value in records.items()}


@dataclass
class SystemState:
    candidates: dict[int, Record] = field(default_factory=dict)
    candidate_id_counter: int = 1
    voting_stations: dict[int, Record] = field(default_factory=dict)
    station_id_counter: int = 1
    polls: dict[int, Record] = field(default_factory=dict)
    poll_id_counter: int = 1
    positions: dict[int, Record] = field(default_factory=dict)
    position_id_counter: int = 1
    voters: dict[int, Record] = field(default_factory=dict)
    voter_id_counter: int = 1
    admins: dict[int, Record] = field(default_factory=dict)
    admin_id_counter: int = 1
    votes: list[Record] = field(default_factory=list)
    audit_log: list[Record] = field(default_factory=list)
    current_user: Record | None = None
    current_role: str | None = None

    def __post_init__(self) -> None:
        self.ensure_default_admin()

    def ensure_default_admin(self) -> None:
        if self.admins:
            self.admin_id_counter = max(self.admin_id_counter, max(self.admins) + 1)
            return
        self.admins[1] = {
            "id": 1,
            "username": DEFAULT_ADMIN_USERNAME,
            "password": hashlib.sha256(DEFAULT_ADMIN_PASSWORD.encode()).hexdigest(),
            "full_name": DEFAULT_ADMIN_FULL_NAME,
            "email": DEFAULT_ADMIN_EMAIL,
            "role": DEFAULT_ADMIN_ROLE,
            "created_at": timestamp_now(),
            "is_active": True,
        }
        self.admin_id_counter = max(self.admin_id_counter, 2)

    def clear_session(self) -> None:
        self.current_user = None
        self.current_role = None

    def serialize(self) -> dict[str, Any]:
        return {
            "candidates": self.candidates,
            "candidate_id_counter": self.candidate_id_counter,
            "voting_stations": self.voting_stations,
            "station_id_counter": self.station_id_counter,
            "polls": self.polls,
            "poll_id_counter": self.poll_id_counter,
            "positions": self.positions,
            "position_id_counter": self.position_id_counter,
            "voters": self.voters,
            "voter_id_counter": self.voter_id_counter,
            "admins": self.admins,
            "admin_id_counter": self.admin_id_counter,
            "votes": self.votes,
            "audit_log": self.audit_log,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "SystemState":
        state = cls(
            candidates=_normalize_int_keys(payload.get("candidates", {})),
            candidate_id_counter=payload.get("candidate_id_counter", 1),
            voting_stations=_normalize_int_keys(payload.get("voting_stations", {})),
            station_id_counter=payload.get("station_id_counter", 1),
            polls=_normalize_int_keys(payload.get("polls", {})),
            poll_id_counter=payload.get("poll_id_counter", 1),
            positions=_normalize_int_keys(payload.get("positions", {})),
            position_id_counter=payload.get("position_id_counter", 1),
            voters=_normalize_int_keys(payload.get("voters", {})),
            voter_id_counter=payload.get("voter_id_counter", 1),
            admins=_normalize_int_keys(payload.get("admins", {})),
            admin_id_counter=payload.get("admin_id_counter", 1),
            votes=list(payload.get("votes", [])),
            audit_log=list(payload.get("audit_log", [])),
        )
        state.ensure_default_admin()
        return state
