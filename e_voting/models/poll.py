import datetime


class PollPosition:
    """Represents a position within a poll, with its assigned candidates."""

    def __init__(self, position_id, position_title, candidate_ids=None,
                 max_winners=1):
        self.position_id = position_id
        self.position_title = position_title
        self.candidate_ids = candidate_ids if candidate_ids is not None else []
        self.max_winners = max_winners

    def has_candidates(self):
        return len(self.candidate_ids) > 0

    def to_dict(self):
        return {
            "position_id": self.position_id,
            "position_title": self.position_title,
            "candidate_ids": self.candidate_ids,
            "max_winners": self.max_winners,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            position_id=data["position_id"],
            position_title=data["position_title"],
            candidate_ids=data.get("candidate_ids", []),
            max_winners=data.get("max_winners", 1),
        )


class Poll:
    DRAFT = "draft"
    OPEN = "open"
    CLOSED = "closed"

    def __init__(self, poll_id, title, description, election_type,
                 start_date, end_date, positions=None, station_ids=None,
                 status="draft", total_votes_cast=0,
                 created_at=None, created_by=None):
        self.id = poll_id
        self.title = title
        self.description = description
        self.election_type = election_type
        self.start_date = start_date
        self.end_date = end_date
        self.positions = positions or []
        self.station_ids = station_ids or []
        self.status = status
        self.total_votes_cast = total_votes_cast
        self.created_at = created_at or str(datetime.datetime.now())
        self.created_by = created_by

    def is_draft(self):
        return self.status == self.DRAFT

    def is_open(self):
        return self.status == self.OPEN

    def is_closed(self):
        return self.status == self.CLOSED

    def has_any_candidates(self):
        return any(pos.has_candidates() for pos in self.positions)

    def open_poll(self):
        self.status = self.OPEN

    def close_poll(self):
        self.status = self.CLOSED

    def record_vote(self):
        self.total_votes_cast += 1

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "election_type": self.election_type,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "positions": [p.to_dict() for p in self.positions],
            "station_ids": self.station_ids,
            "status": self.status,
            "total_votes_cast": self.total_votes_cast,
            "created_at": self.created_at,
            "created_by": self.created_by,
        }

    @classmethod
    def from_dict(cls, data):
        positions = [
            PollPosition.from_dict(p) for p in data.get("positions", [])
        ]
        return cls(
            poll_id=data["id"],
            title=data["title"],
            description=data["description"],
            election_type=data["election_type"],
            start_date=data["start_date"],
            end_date=data["end_date"],
            positions=positions,
            station_ids=data.get("station_ids", []),
            status=data.get("status", "draft"),
            total_votes_cast=data.get("total_votes_cast", 0),
            created_at=data.get("created_at"),
            created_by=data.get("created_by"),
        )
