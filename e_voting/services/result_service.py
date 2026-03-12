from e_voting.constants import (
    BAR_CHART_WIDTH, TURNOUT_HIGH_THRESHOLD, TURNOUT_MEDIUM_THRESHOLD,
    STATION_LOAD_WARNING_PERCENT, STATION_LOAD_CRITICAL_PERCENT,
)


class ResultService:
    """Calculates election results, statistics, and station breakdowns."""

    def __init__(self, store):
        self._store = store

    def get_position_tally(self, poll_id, position_id):
        """Returns (vote_counts_dict, abstain_count, total_votes)."""
        vote_counts = {}
        abstain_count = 0
        for vote in self._store.votes:
            if vote.poll_id == poll_id and vote.position_id == position_id:
                if vote.abstained:
                    abstain_count += 1
                else:
                    cid = vote.candidate_id
                    vote_counts[cid] = vote_counts.get(cid, 0) + 1
        total = sum(vote_counts.values()) + abstain_count
        return vote_counts, abstain_count, total

    def get_eligible_voter_count(self, poll):
        return sum(
            1 for v in self._store.voters.values()
            if v.is_verified and v.is_active
            and v.station_id in poll.station_ids
        )

    def calculate_turnout(self, poll):
        eligible = self.get_eligible_voter_count(poll)
        if eligible <= 0:
            return 0.0, eligible
        return (poll.total_votes_cast / eligible * 100), eligible

    def get_system_statistics(self):
        candidates = self._store.candidates
        voters = self._store.voters
        stations = self._store.voting_stations
        polls = self._store.polls

        return {
            "total_candidates": len(candidates),
            "active_candidates": sum(
                1 for c in candidates.values() if c.is_active
            ),
            "total_voters": len(voters),
            "verified_voters": sum(
                1 for v in voters.values() if v.is_verified
            ),
            "active_voters": sum(
                1 for v in voters.values() if v.is_active
            ),
            "total_stations": len(stations),
            "active_stations": sum(
                1 for s in stations.values() if s.is_active
            ),
            "total_polls": len(polls),
            "open_polls": sum(
                1 for p in polls.values() if p.is_open()
            ),
            "closed_polls": sum(
                1 for p in polls.values() if p.is_closed()
            ),
            "draft_polls": sum(
                1 for p in polls.values() if p.is_draft()
            ),
            "total_votes": len(self._store.votes),
        }

    def get_voter_demographics(self):
        voters = self._store.voters
        total_voters = len(voters)
        gender_counts = {}
        age_groups = {
            "18-25": 0, "26-35": 0, "36-45": 0,
            "46-55": 0, "56-65": 0, "65+": 0,
        }
        for voter in voters.values():
            gender = voter.gender or "?"
            gender_counts[gender] = gender_counts.get(gender, 0) + 1
            age = voter.age or 0
            if age <= 25:
                age_groups["18-25"] += 1
            elif age <= 35:
                age_groups["26-35"] += 1
            elif age <= 45:
                age_groups["36-45"] += 1
            elif age <= 55:
                age_groups["46-55"] += 1
            elif age <= 65:
                age_groups["56-65"] += 1
            else:
                age_groups["65+"] += 1
        return gender_counts, age_groups, total_voters

    def get_station_load(self):
        results = []
        for sid, station in self._store.voting_stations.items():
            voter_count = sum(
                1 for v in self._store.voters.values()
                if v.station_id == sid
            )
            load_percent = (
                (voter_count / station.capacity * 100)
                if station.capacity > 0 else 0
            )
            results.append({
                "station": station,
                "voter_count": voter_count,
                "load_percent": load_percent,
                "is_overloaded": load_percent > STATION_LOAD_CRITICAL_PERCENT,
            })
        return results

    def get_party_distribution(self):
        party_counts = {}
        for candidate in self._store.candidates.values():
            if candidate.is_active:
                party = candidate.party
                party_counts[party] = party_counts.get(party, 0) + 1
        return dict(
            sorted(party_counts.items(), key=lambda x: x[1], reverse=True)
        )

    def get_education_distribution(self):
        edu_counts = {}
        for candidate in self._store.candidates.values():
            if candidate.is_active:
                edu = candidate.education
                edu_counts[edu] = edu_counts.get(edu, 0) + 1
        return edu_counts

    def get_station_results(self, poll_id):
        poll = self._store.polls.get(poll_id)
        if not poll:
            return None

        station_data = []
        for sid in poll.station_ids:
            station = self._store.voting_stations.get(sid)
            if not station:
                continue

            station_votes = [
                v for v in self._store.votes
                if v.poll_id == poll_id and v.station_id == sid
            ]
            unique_voters = len(set(v.voter_id for v in station_votes))
            registered = sum(
                1 for v in self._store.voters.values()
                if v.station_id == sid and v.is_verified and v.is_active
            )
            turnout = (
                (unique_voters / registered * 100) if registered > 0 else 0
            )

            position_results = []
            for pos in poll.positions:
                pos_votes = [
                    v for v in station_votes
                    if v.position_id == pos.position_id
                ]
                vote_counts = {}
                abstain_count = 0
                for vote in pos_votes:
                    if vote.abstained:
                        abstain_count += 1
                    else:
                        cid = vote.candidate_id
                        vote_counts[cid] = vote_counts.get(cid, 0) + 1
                total = sum(vote_counts.values()) + abstain_count
                position_results.append({
                    "position_title": pos.position_title,
                    "vote_counts": vote_counts,
                    "abstain_count": abstain_count,
                    "total": total,
                })

            station_data.append({
                "station": station,
                "unique_voters": unique_voters,
                "registered": registered,
                "turnout": turnout,
                "position_results": position_results,
            })

        return station_data

    def get_audit_log(self, filter_type=None, filter_value=None, limit=None):
        entries = self._store.audit_log

        if filter_type == "action" and filter_value:
            entries = [
                e for e in entries if e["action"] == filter_value
            ]
        elif filter_type == "user" and filter_value:
            entries = [
                e for e in entries
                if filter_value.lower() in e["user"].lower()
            ]
        elif filter_type == "last" and limit:
            entries = entries[-limit:]

        return entries

    def get_unique_action_types(self):
        return list(set(e["action"] for e in self._store.audit_log))
