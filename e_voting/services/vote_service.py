import datetime
import hashlib

from e_voting.constants import VOTE_HASH_LENGTH
from e_voting.models.vote import Vote


class VoteService:
    """Business logic for the voting process."""

    def __init__(self, store):
        self._store = store

    def get_available_polls(self, voter):
        """Returns polls that are open, the voter hasn't voted in,
        and the voter's station is included."""
        available = {}
        for poll_id, poll in self._store.polls.items():
            if (poll.is_open()
                    and not voter.has_voted_in_poll(poll_id)
                    and voter.station_id in poll.station_ids):
                available[poll_id] = poll
        return available

    def get_open_polls(self):
        return {
            pid: p for pid, p in self._store.polls.items()
            if p.is_open()
        }

    def get_closed_polls(self):
        return {
            pid: p for pid, p in self._store.polls.items()
            if p.is_closed()
        }

    def cast_votes(self, voter, poll_id, choices):
        """Records votes for a voter in a poll.

        Args:
            voter: The Voter object.
            poll_id: The poll ID.
            choices: List of dicts with keys:
                position_id, candidate_id (or None), abstained.

        Returns:
            The vote hash reference string.
        """
        poll = self._store.polls.get(poll_id)
        if not poll:
            return None

        vote_timestamp = str(datetime.datetime.now())
        raw_hash = f"{voter.id}{poll_id}{vote_timestamp}"
        vote_hash = hashlib.sha256(
            raw_hash.encode()
        ).hexdigest()[:VOTE_HASH_LENGTH]

        for choice in choices:
            vote = Vote(
                vote_id=vote_hash + str(choice["position_id"]),
                poll_id=poll_id,
                position_id=choice["position_id"],
                candidate_id=choice["candidate_id"],
                voter_id=voter.id,
                station_id=voter.station_id,
                timestamp=vote_timestamp,
                abstained=choice["abstained"],
            )
            self._store.votes.append(vote)

        voter.record_vote(poll_id)

        for stored_voter in self._store.voters.values():
            if stored_voter.id == voter.id:
                if poll_id not in stored_voter.has_voted_in:
                    stored_voter.record_vote(poll_id)
                break

        poll.record_vote()
        self._store.log_action(
            "CAST_VOTE", voter.voter_card_number,
            f"Voted in poll: {poll.title} (Hash: {vote_hash})"
        )
        self._store.save()
        return vote_hash

    def get_voter_votes_in_poll(self, voter_id, poll_id):
        return [
            v for v in self._store.votes
            if v.poll_id == poll_id and v.voter_id == voter_id
        ]
